"""
Schemas Pydantic v2 para autenticación.
Distintos de los schemas de app/schemas/user_schema.py: estos son
específicos del flujo de registro, login y tokens JWT.
"""

import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.user_schema import RoleEnum


class UserRegister(BaseModel):
    """Datos requeridos para registrar un nuevo usuario."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombre completo del usuario",
        examples=["Sebastian Hurtado"],
    )
    email: EmailStr = Field(
        ...,
        description="Correo electrónico único del usuario",
        examples=["sebastian@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,  # límite real de bcrypt
        description="Contraseña: mínimo 8 caracteres, con mayúscula, minúscula y número",
        examples=["MiPass123"],
    )
    role: RoleEnum = Field(
        default=RoleEnum.user,
        description="Rol del usuario dentro del sistema",
    )

    @field_validator("password")
    @classmethod
    def password_segura(cls, v: str) -> str:
        if " " in v:
            raise ValueError("La contraseña no puede contener espacios en blanco")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class UserLogin(BaseModel):
    """Credenciales para iniciar sesión."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Respuesta del endpoint de login: el token de acceso."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos extraídos del payload de un token JWT decodificado."""

    email: str | None = None