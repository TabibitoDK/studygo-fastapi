from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=6)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    background_url: Optional[str] = None
    class Config:
        from_attributes = True

class UserUpdateIn(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    background_url: Optional[str] = None

class PostCreateIn(BaseModel):
    content: str = Field(min_length=1, max_length=5000)

class PostOut(BaseModel):
    id: str
    content: str
    created_at: str
    user_id: str
    class Config:
        from_attributes = True

class ProgressIn(BaseModel):
    module: str = Field(min_length=1, max_length=128)
    percent: int = Field(ge=0, le=100)

class ProgressOut(BaseModel):
    id: str
    module: str
    percent: int
    updated_at: str
    class Config:
        from_attributes = True
