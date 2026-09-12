"""
Schemas Pydantic para el recurso User.
Definen la forma de los datos que entran y salen por la API,
independientes de la estructura de la tabla en la base de datos.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RoleEnum(str, Enum):
    admin = "admin"
    support = "support"
    user = "user"


# ---------- Schema para CREAR usuario ----------
class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    role: RoleEnum
    is_active: bool = True


# ---------- Schema para ACTUALIZAR usuario completo (PUT) ----------
class UserUpdate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    role: RoleEnum
    is_active: bool = True


# ---------- Schema para ACTUALIZAR usuario parcial (PATCH) ----------
class UserPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None


# ---------- Schema de RESPUESTA ----------
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)