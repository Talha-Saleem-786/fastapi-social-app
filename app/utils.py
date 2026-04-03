from passlib.context import CryptContext
from typing import Annotated
from fastapi import Path
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def hash_password(password: Annotated[str, Path(min_length=8, max_length=25, description="Password must be at least 8 characters")]) -> str:
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)