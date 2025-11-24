import os
from dotenv import load_dotenv

load_dotenv()

LAST_POKEMON_ID = 1025
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-fallback-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
