from fastapi import APIRouter, Depends
from app.deps.auth import require_token
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from app.errors import AppError


router = APIRouter()

# In-memory data store
_fake_db: list[dict] = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin", "created_at": "2024-01-01T00:00:00"},
    {"id": 2, "name": "Bob",   "email": "bob@example.com",   "role": "user",  "created_at": "2024-01-02T00:00:00"},
]

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


@router.get("/users/me")
def get_current_user(auth=Depends(require_token)):
    return {
        "success": True,
        "data": {
            "user_id": auth["user_id"],
            "token": auth["token"][:10] + "..."
        }
    }

@router.get("/users")
def list_users():
    return {
        "success": True,
        "data": [],
        "meta": {
            "page": 1,
            "page_size": 20,
            "total_items": 0
        }
    }

# @router.get("/users/{user_id}")
# def get_user(user_id: int):
#     return {
#         "success": True,
#         "data": {
#             "id": user_id,
#             "name": "Sample User",
#             "email": "user@example.com"
#         }
#     }

@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    user = next((u for u in _fake_db if u["id"] == user_id), None)
    if not user:
        raise AppError(
            status_code=404,
            code="USER_NOT_FOUND",
            message=f"User dengan ID {user_id} tidak ditemukan",
            detail=[]
        )
    return user

