from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
import uuid

def gen_uuid() -> str:
    return str(uuid.uuid4())

class UserBase(SQLModel):
    email: str
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    background_url: Optional[str] = None

class User(UserBase, table=True):
    __tablename__ = "users"
    id: str = Field(default_factory=gen_uuid, primary_key=True, nullable=False)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    posts: List["Post"] = Relationship(back_populates="user")
    progress: List["Progress"] = Relationship(back_populates="user")

    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("username", name="uq_users_username"),
    )

class PostBase(SQLModel):
    content: str

class Post(PostBase, table=True):
    __tablename__ = "posts"
    id: str = Field(default_factory=gen_uuid, primary_key=True, nullable=False)
    user_id: str = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user: Optional[User] = Relationship(back_populates="posts")

class ProgressBase(SQLModel):
    module: str
    percent: int = 0

class Progress(ProgressBase, table=True):
    __tablename__ = "progress"
    id: str = Field(default_factory=gen_uuid, primary_key=True, nullable=False)
    user_id: str = Field(foreign_key="users.id")
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user: Optional[User] = Relationship(back_populates="progress")

    __table_args__ = (
        UniqueConstraint("user_id", "module", name="user_module_unique"),
    )
