import os
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://vkkcnnbvfttvnzamvcsh.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

# Cache for JWKS keys
_jwks_cache = None

def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        try:
            headers = {"apikey": SUPABASE_ANON_KEY} if SUPABASE_ANON_KEY else {}
            response = requests.get(JWKS_URL, headers=headers)
            if response.status_code != 200:
                print(f"Error fetching JWKS: Status {response.status_code}, {response.text}")
                return None
            _jwks_cache = response.json()
            if "keys" not in _jwks_cache:
                print(f"Error: JWKS response missing 'keys': {_jwks_cache}")
                _jwks_cache = None
                return None
        except Exception as e:
            print(f"Error fetching JWKS: {e}")
            return None
    return _jwks_cache

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = auth.credentials
    jwks = get_jwks()
    
    if not jwks:
        raise HTTPException(status_code=500, detail="Authentication server unavailable")

    try:
        # 1. Get the 'kid' (Key ID) from the token header
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        alg = header.get("alg")
        
        # 2. Find the matching key in JWKS
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            print(f"No matching key found for kid: {kid}")
            raise credentials_exception

        # 3. Decode the token using the Public Key from JWKS
        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256", "RS256", "HS256"],
            options={"verify_aud": False, "verify_exp": False}
        )
        
        auth_uid: str = payload.get("sub")
        if auth_uid is None:
            raise credentials_exception
            
    except JWTError as e:
        print(f"JWT Validation Error: {e}")
        # Log header for debugging
        try:
            print(f"DEBUG: Token Header: {jwt.get_unverified_header(token)}")
        except: pass
        raise credentials_exception
    
    # 4. Fetch or create local user
    user = db.query(User).filter(User.auth_uid == auth_uid).first()
    if user is None:
        user = User(
            auth_uid=auth_uid,
            account_status="active",
            role="wholesale_user",
            name="New User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user
