import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key() -> str:
    return os.getenv("API_KEY")

def is_test_mode() -> bool:
    return os.getenv("TEST_MODE", "true").lower() == "true"
