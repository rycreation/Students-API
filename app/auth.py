
import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from app.config import (SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES,)
from app.database import get_connection

router = APIRouter(prefix="/auth", tags=["Authentication"])

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



ALGORITHM = "HS256"


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=12, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def create_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    return jwt.encode(
        {"sub": str(user_id), "exp": expires},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


@router.post("/register", status_code=201)
def register(data: RegisterRequest):
    email = data.email.strip().lower()
    hashed = password_hash.hash(data.password)

    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, hashed),
        )
        conn.commit()

        return {"id": cursor.lastrowid, "email": email}

    except Exception as exc:
        conn.rollback()
        import sqlite3

        if isinstance(exc, sqlite3.IntegrityError):
            raise HTTPException(
                status_code=409,
                detail="Email already registered",
            ) from exc
        raise
    finally:
        conn.close()


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username.strip().lower()
    password = form_data.password

    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT id, email, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    finally:
        conn.close()

    if user is None or not password_hash.verify(
        password, user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_token(user["id"]),
        "token_type": "bearer",
    }

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        subject = payload.get("sub")

        if subject is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

        user_id = int(subject)

    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    conn = get_connection()
    try:
       user = conn.execute(
    "SELECT id, email, role FROM users WHERE id = ?",
    (user_id,),
).fetchone()
    finally:
        conn.close()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User no longer exists",
        )

    return {
    "id": user["id"],
    "email": user["email"],
    "role": user["role"],
}

def require_admin(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin permission required",
        )

    return user

@router.get("/me")
def get_my_profile(user: dict = Depends(get_current_user)):
    return user


@router.get("/me")
def get_my_profile(user: dict = Depends(get_current_user)):
    return user
