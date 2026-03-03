# 🐍 Pydantic Cheat Sheet (v2)
> Digunakan bersama FastAPI untuk validasi request & response body.

---

## 1. Basic Model

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = True   # default value
```

---

## 2. Field — Validasi & Metadata

```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    name: str  = Field(min_length=1, max_length=100, description="Nama lengkap")
    age:  int  = Field(ge=0, le=150, description="Umur dalam tahun")
    role: str  = Field(default="user", pattern="^(admin|user|lecturer)$")
    score: float = Field(gt=0, lt=100)   # gt=greater-than, lt=less-than
```

| Constraint | Arti |
|---|---|
| `min_length` / `max_length` | Panjang string |
| `ge` / `le` | ≥ / ≤ (untuk angka) |
| `gt` / `lt` | > / < (untuk angka) |
| `pattern` | Regex untuk string |
| `default` | Nilai default |
| `description` | Keterangan (muncul di Swagger) |

---

## 3. Tipe Data Umum

```python
from pydantic import BaseModel, EmailStr, HttpUrl
from datetime import datetime
from typing import Optional, List

class Example(BaseModel):
    email:      EmailStr            # validasi format email otomatis
    website:    HttpUrl             # validasi format URL
    created_at: datetime            # ISO 8601 string → datetime otomatis
    tags:       List[str] = []      # list of strings
    nickname:   Optional[str] = None  # boleh None
```

---

## 4. Optional / Partial (untuk PATCH)

```python
# Semua field None by default → cocok untuk PATCH endpoint
class UserUpdate(BaseModel):
    name:  str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    role:  str | None = Field(None, pattern="^(admin|user|lecturer)$")
```

> **Tip:** Gunakan `.model_dump(exclude_none=True)` saat update ke DB  
> supaya field yang `None` tidak menimpa data lama.

```python
payload = user_update.model_dump(exclude_none=True)
# {"name": "Alice"}  → hanya field yang diisi
```

---

## 5. Nested Model

```python
class Address(BaseModel):
    city:    str
    country: str

class UserWithAddress(BaseModel):
    name:    str
    address: Address   # nested model

# Input JSON:
# { "name": "Alice", "address": { "city": "Jakarta", "country": "ID" } }
```

---

## 6. Validator Custom (`@field_validator`)

```python
from pydantic import BaseModel, field_validator

class UserCreate(BaseModel):
    name:     str
    password: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Nama tidak boleh kosong atau spasi saja")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password minimal 8 karakter")
        return v
```

---

## 7. Model Validator (lintas field)

```python
from pydantic import BaseModel, model_validator

class PasswordReset(BaseModel):
    password:         str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self) -> "PasswordReset":
        if self.password != self.confirm_password:
            raise ValueError("Password dan konfirmasi tidak cocok")
        return self
```

---

## 8. Response Model dengan ORM (`from_attributes`)

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserOut(BaseModel):
    id:         int
    name:       str
    email:      EmailStr
    role:       str
    created_at: datetime

    model_config = {"from_attributes": True}  # Pydantic v2
    # class Config:
    #     from_attributes = True              # cara lama (masih works)
```

Gunakan di router:
```python
@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    user = get_from_db(user_id)   # SQLAlchemy ORM object
    return user                   # Pydantic konversi otomatis
```

---

## 9. Serialisasi & Deserialisasi

```python
user = UserCreate(name="Alice", email="alice@example.com")

# → dict
user.model_dump()
# → dict, tanpa field None
user.model_dump(exclude_none=True)
# → JSON string
user.model_dump_json()

# Dari dict
data = {"name": "Alice", "email": "alice@example.com"}
user = UserCreate.model_validate(data)

# Dari JSON string
user = UserCreate.model_validate_json('{"name":"Alice","email":"alice@example.com"}')
```

---

## 10. Inheritance (Reuse Schema)

```python
class UserBase(BaseModel):
    name:  str
    email: EmailStr

class UserCreate(UserBase):
    password: str          # tambah field baru

class UserOut(UserBase):
    id:         int        # tambah field baru
    created_at: datetime

    model_config = {"from_attributes": True}
```

---

## 11. Enum sebagai Tipe

```python
from enum import Enum
from pydantic import BaseModel

class RoleEnum(str, Enum):
    admin    = "admin"
    user     = "user"
    lecturer = "lecturer"

class UserCreate(BaseModel):
    name: str
    role: RoleEnum = RoleEnum.user

# FastAPI otomatis tampilkan pilihan di Swagger
```

---

## 12. Contoh Lengkap (seperti di proyek ini)

```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from enum import Enum

class RoleEnum(str, Enum):
    admin    = "admin"
    user     = "user"
    lecturer = "lecturer"

class UserCreate(BaseModel):
    name:  str      = Field(min_length=1, max_length=100, description="Nama lengkap")
    email: EmailStr = Field(description="Email valid")
    role:  RoleEnum = Field(default=RoleEnum.user)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()

class UserUpdate(BaseModel):
    name:  str | None      = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    role:  RoleEnum | None = None

class UserOut(BaseModel):
    id:         int
    name:       str
    email:      EmailStr
    role:       str
    created_at: datetime

    model_config = {"from_attributes": True}
```

---

## Quick Reference

| Kebutuhan | Solusi |
|---|---|
| Validasi format email | `EmailStr` |
| Validasi URL | `HttpUrl` |
| Field optional (PATCH) | `field: Type \| None = None` |
| Nilai min/max string | `Field(min_length=..., max_length=...)` |
| Nilai min/max angka | `Field(ge=..., le=...)` |
| Validasi regex | `Field(pattern="...")` |
| Validasi custom | `@field_validator` |
| Validasi antar field | `@model_validator(mode="after")` |
| Konversi ORM → schema | `model_config = {"from_attributes": True}` |
| Update parsial ke DB | `model.model_dump(exclude_none=True)` |
| Reuse schema | Inheritance dari `BaseModel` |
| Pilihan tetap | `Enum` |
