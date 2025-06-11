from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# Base schema for User
class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)

# Schema to create user
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

# Schema to update user
class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    profile_image: Optional[str] = None

# Schema for response (what the API returns)
class UserResponse(UserBase):
    id: str
    profile_image: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schema for login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse