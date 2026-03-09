import cohere

import os
from dotenv import load_dotenv

# Load environment variables from app/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

co = cohere.ClientV2(os.getenv("COHERE_API_KEY", "YOUR_COHERE_API_KEY"))



response = co.chat(
    model="command-r-08-2024",
    messages=[{"role": "user", "content": "Explain how IC engine works in a few words"}]
)

print(response.message.content[0].text)