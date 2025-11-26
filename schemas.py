from pydantic import BaseModel
from typing import Optional, List

class FileBase(BaseModel):
    title: str

class FileCreate(FileBase):
    file: bytes

class File(FileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    files: List[File] = []

    class Config:
        from_attributes = True
