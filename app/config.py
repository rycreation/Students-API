
import os
from pathlib import Path
from dotenv import load_dotenv

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env for local development.
# Render environment variables are read automatically by os.getenv().
load_dotenv(BASE_DIR / ".env")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is missing. Set SECRET_KEY in your local .env "
        "file or in Render Environment Variables."
    )

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15

# Database configuration
database_value = os.getenv("DATABASE_PATH", "students.db")
database_path = Path(database_value)

if not database_path.is_absolute():
    database_path = BASE_DIR / database_path

DATABASE_PATH = database_path
