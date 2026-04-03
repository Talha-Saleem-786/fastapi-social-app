from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field


# -------------------------
# USER SCHEMAS
# -------------------------

class UserCreated(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(
        min_length=8,
        max_length=25,
        description="Password must be at least 8 characters"
    )]

class UserOut(BaseModel):
    id: Annotated[int, Field(gt=0)]
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(
        min_length=8,
        max_length=25,
    )]

class User_Response(BaseModel):
    id: Annotated[int, Field(gt=0)]
    email: EmailStr
    created_At: datetime

    class Config:
        from_attributes = True


# -------------------------
# POST SCHEMAS
# -------------------------

class PostBase(BaseModel):
    title: Annotated[str, Field(
        min_length=3,
        max_length=100,
        description="Post title",
    )]
    content: Annotated[str, Field(
        min_length=10,         
        description="Post content",
    )]
    published: bool = True

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: Annotated[int, Field(gt=0)]
    created_at: datetime
    user_id: Annotated[int, Field(gt=0)]
    owner: UserOut

    class Config:
        from_attributes = True


# -------------------------
# POST + VOTE COUNT
# -------------------------

class PostOut(BaseModel):
    Post: PostResponse
    votes: Annotated[int, Field(
        ge=0,                   
        description="Vote count"
    )]

    class Config:
        from_attributes = True


# -------------------------
# TOKEN SCHEMAS
# -------------------------

class Token(BaseModel):
    access_token: Annotated[str, Field(
        min_length=1,
        description="JWT access token"
    )]
    token_type: str

class TokenData(BaseModel):
    id: Optional[Annotated[str, Field(min_length=1)]] = None


# -------------------------
# VOTE SCHEMA
# -------------------------

class Vote(BaseModel):
    post_id: Annotated[int, Field(
        gt=0,                   
        description="Post ID to vote on"
    )]
    dir: Annotated[int, Field(
        ge=0,
        le=1,
        description="1 = upvote, 0 = remove vote"
    )]