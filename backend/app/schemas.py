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

