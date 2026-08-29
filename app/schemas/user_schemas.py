from enum import Enum
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RoleEnum(str, Enum):
    admin = "admin"
    support = "support"
    user = "user"


class UserBase(BaseModel):
    name: str = Field(..., min_length=3, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Correo electrónico válido")
    role: RoleEnum = Field(..., description="Rol del usuario en el sistema")
    is_active: bool = Field(default=True, description="Estado del usuario")


class UserCreate(UserBase):
    """Modelo de entrada para crear un usuario (POST /users)."""
    pass


class UserResponse(UserBase):
    """Modelo de salida: lo que ve el cliente."""
    id: int
    model_config = ConfigDict(from_attributes=True)