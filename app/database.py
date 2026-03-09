from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = "postgresql://postgres.vkkcnnbvfttvnzamvcsh:Hudhaifa%402025@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres"

engine = create_engine(DATABASE_URL,pool_pre_ping=True,connect_args={"sslmode": "require"})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()