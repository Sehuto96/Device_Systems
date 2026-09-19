"""
Schemas Pydantic para el recurso Device.
Definen la forma de los datos que entran y salen por la API,
independientes del modelo SQLAlchemy.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DeviceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Laptop Lenovo ThinkPad"])
    serial_number: str = Field(..., min_length=1, max_length=100, examples=["LEN-2024-001"])
    device_type: str = Field(..., min_length=1, max_length=50, examples=["laptop"])
    brand: Optional[str] = Field(None, max_length=50, examples=["Lenovo"])


class DeviceCreate(DeviceBase):
    """Datos requeridos para crear un dispositivo. is_available siempre inicia en True."""
    pass


class DeviceUpdate(DeviceBase):
    """Reemplazo completo de un dispositivo (PUT)."""
    is_available: bool = True


class DevicePatch(BaseModel):
    """Actualización parcial de un dispositivo (PATCH). Todos los campos opcionales."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    serial_number: Optional[str] = Field(None, min_length=1, max_length=100)
    device_type: Optional[str] = Field(None, min_length=1, max_length=50)
    brand: Optional[str] = Field(None, max_length=50)
    is_available: Optional[bool] = None


class DeviceResponse(DeviceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_available: bool
    created_at: datetime