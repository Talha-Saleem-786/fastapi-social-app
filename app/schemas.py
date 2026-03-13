from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# -------------------------
# USER SCHEMAS
# -------------------------

class UserCreated(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# -------------------------
# POST SCHEMAS
# -------------------------

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    created_at: datetime
    user_id: int
    owner: UserOut

    class Config:
        from_attributes = True


# -------------------------
# POST + VOTE COUNT
# -------------------------

class PostOut(BaseModel):
    Post: PostResponse
    votes: int

    class Config:
        from_attributes = True


# -------------------------
# TOKEN SCHEMAS
# -------------------------

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


# -------------------------
# VOTE SCHEMA
# -------------------------

class Vote(BaseModel):
    post_id: int
    dir: int