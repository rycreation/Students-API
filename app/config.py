import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing from .env")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15

database_value = os.getenv("DATABASE_PATH","students.db")
database_path = Path(database_value)

if not database_path.is_absolute():
    database_path = BASE_DIR / database_path

DATABASE_PATH = database_path