"""
Schemas Pydantic para el recurso Loan.
Incluye schemas "planos" (LoanResponse) y schemas con información
relacionada de usuario y dispositivo (LoanDetailResponse), usados
en los endpoints de consultas con joins.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoanStatus(str, Enum):
    active = "active"
    returned = "returned"
    overdue = "overdue"


class LoanCreate(BaseModel):
    user_id: int = Field(..., examples=[1])
    device_id: int = Field(..., examples=[3])


class LoanUpdate(BaseModel):
    """Actualización parcial de un préstamo (PATCH genérico, distinto del endpoint /return)."""
    status: Optional[LoanStatus] = Field(default=None, examples=["returned"])
    return_date: Optional[datetime] = Field(default=None, examples=["2026-09-17T00:32:24.451703"])


class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(examples=[1])
    user_id: int = Field(examples=[1])
    device_id: int = Field(examples=[3])
    loan_date: datetime = Field(examples=["2026-09-17T00:28:28.584970"])
    return_date: Optional[datetime] = Field(default=None, examples=["2026-09-17T00:32:24.451703"])
    status: LoanStatus = Field(examples=["active"])


# --- Schemas anidados para respuestas con joins ---

class UserBasicInfo(BaseModel):
    """Datos mínimos del usuario, para incrustar en LoanDetailResponse."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(examples=[1])
    name: str = Field(examples=["Ana Pérez"])
    email: EmailStr = Field(examples=["ana@sena.edu.co"])


class DeviceBasicInfo(BaseModel):
    """Datos mínimos del dispositivo, para incrustar en LoanDetailResponse."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(examples=[3])
    name: str = Field(examples=["Laptop Lenovo ThinkPad"])
    serial_number: str = Field(examples=["LEN-2024-001"])
    device_type: str = Field(examples=["laptop"])


class LoanDetailResponse(BaseModel):
    """
    Respuesta de préstamo con información relacionada de usuario y dispositivo.
    Se construye manualmente en la capa de servicio (no directamente con
    from_attributes) porque combina datos de tres tablas.
    """
    model_config = ConfigDict(from_attributes=True)

    loan_id: int = Field(examples=[1])
    status: LoanStatus = Field(examples=["active"])
    loan_date: datetime = Field(examples=["2026-09-17T00:28:28.584970"])
    return_date: Optional[datetime] = Field(default=None, examples=["2026-09-17T00:32:24.451703"])
    user: UserBasicInfo
    device: DeviceBasicInfo