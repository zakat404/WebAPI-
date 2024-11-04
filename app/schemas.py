from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class ImageBase(BaseModel):
    name: str
    tags: Optional[str] = None

class ImageCreate(ImageBase):
    pass

class ImageUpdate(BaseModel):
    name: Optional[str] = None
    tags: Optional[str] = None

class Image(ImageBase):
    id: int
    file_path: str
    upload_date: datetime
    resolution: str
    size: float

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
