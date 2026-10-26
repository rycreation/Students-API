
# Student Management System

A REST API built with FastAPI, SQLite, Pydantic, and JWT authentication.

## Features

- Student CRUD operations
- User registration and login
- JWT-based authentication
- Role-based authorization
- Input validation
- Automated API tests

## Requirements

- Python 3.11 or a compatible Python version
- pip

## Setup

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a `.env` file with the required configuration:

```dotenv
SECRET_KEY=replace_with_a_random_secret
DATABASE_PATH=students.db
```

Never commit real secrets to Git.

## Run the API

```powershell
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## Run tests

```powershell
python -m pytest -v
```

## Security

- Passwords must be stored as secure hashes.
- Protected endpoints must validate authentication.
- Admin-only operations must enforce authorization.
- Production deployments should use HTTPS and secure configuration.


## 🌐 Live Demo

**Live Application:** ## 🌐 Live Demo

**Live Application:**(https://client-server-course.onrender.com/)

**API Documentation (Swagger UI):** (https://client-server-course.onrender.com/docs)
**ReDoc Documentation:** (https://client-server-course.onrender.com/redoc)



