from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(max_length=320)

class UnAuthUserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)

class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    image_file: str | None
    bio: str | None
    image_path: str


class UnAuthUserResponse(UnAuthUserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    image_file: str | None
    bio: str | None
    image_path: str


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)
    content: str = Field(min_length=1)
    pinned: bool = False
    image_file: Optional[str] = None

class PostCreate(PostBase):
    user_id: int # temp
    tags: list[str] = []

class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id:int
    user_id: int
    title: str
    content: str
    description: str
    created_at: datetime
    author: UnAuthUserResponse


class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    model_config = ConfigDict(from_attributes=True)


class TagResponse(TagBase):
    model_config = ConfigDict(from_attributes=True)

    id:int

