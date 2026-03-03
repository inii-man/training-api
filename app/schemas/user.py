from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    """Schema untuk request create user (POST)"""
    name: str = Field(
        min_length=1, max_length=100,
        description="Nama lengkap user"
    )
    email: EmailStr = Field(description="Email valid")
    role: str = Field(
        default="user",
        pattern="^(admin|user|lecturer)$"
    )

class UserUpdate(BaseModel):
    """Schema untuk PATCH - semua field optional"""
    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    role: str | None = Field(None, pattern="^(admin|user|lecturer)$")

class UserOut(BaseModel):
    """Schema untuk response user"""
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True  # Allow ORM models