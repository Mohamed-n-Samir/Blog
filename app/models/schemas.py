import enum
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Enums
class UserRole(enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(max_length=320)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)


class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=320)
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=320)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    image_file: str | None
    bio: str | None


class UserPublicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str = Field(min_length=3, max_length=50)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image_file: str | None
    bio: str | None
    image_path: str

class UserPrivateResponse(UserPublicResponse):
    email:EmailStr = Field(max_length=320)


class Token(BaseModel):
    access_token: str
    token_type: str


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)
    content: str = Field(min_length=1)
    pinned: bool = False
    image_file: Optional[str] = None
    category_id: Optional[int] = None

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
    author: UserPublicResponse
    category: Optional[CategoryResponse] = None


class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    model_config = ConfigDict(from_attributes=True)


class TagResponse(TagBase):
    model_config = ConfigDict(from_attributes=True)

    id:int

