from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    profile_image: Optional[str]

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    profile_image: Optional[str] = None

class PostCreate(BaseModel):
    content: str

class CommentCreate(BaseModel):
    content: str
    post_id: int

class LikeCreate(BaseModel):
    post_id: int

class FollowerCreate(BaseModel):
    followed_id: int

class MessageCreate(BaseModel):
    content: str
    receiver_id: int

