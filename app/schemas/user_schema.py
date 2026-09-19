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
    name: str = Field(min_length=3, max_length=100, examples=["Ana Pérez"])
    email: EmailStr = Field(examples=["ana@sena.edu.co"])
    role: RoleEnum = Field(examples=["user"])
    is_active: bool = Field(default=True, examples=[True])


# ---------- Schema para ACTUALIZAR usuario completo (PUT) ----------
class UserUpdate(BaseModel):
    name: str = Field(min_length=3, max_length=100, examples=["Ana Pérez"])
    email: EmailStr = Field(examples=["ana@sena.edu.co"])
    role: RoleEnum = Field(examples=["user"])
    is_active: bool = Field(default=True, examples=[True])


# ---------- Schema para ACTUALIZAR usuario parcial (PATCH) ----------
class UserPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=100, examples=["Ana Pérez"])
    email: Optional[EmailStr] = Field(default=None, examples=["ana@sena.edu.co"])
    role: Optional[RoleEnum] = Field(default=None, examples=["support"])
    is_active: Optional[bool] = Field(default=None, examples=[False])


# ---------- Schema de RESPUESTA ----------
class UserResponse(BaseModel):
    id: int = Field(examples=[1])
    name: str = Field(examples=["Ana Pérez"])
    email: EmailStr = Field(examples=["ana@sena.edu.co"])
    role: RoleEnum = Field(examples=["user"])
    is_active: bool = Field(examples=[True])
    created_at: datetime = Field(examples=["2026-09-17T00:28:28.584970"])

    model_config = ConfigDict(from_attributes=True)