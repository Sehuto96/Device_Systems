"""
Dependencias reutilizables para el recurso Device.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DeviceUpdate
from app.services import device_service


def get_device_or_404(device_id: int, db: Session = Depends(get_db)) -> Device:
    """Busca un dispositivo por ID y lanza 404 automáticamente si no existe."""
    db_device = device_service.get_device_by_id(db, device_id)
    if db_device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado",
        )
    return db_device


def validate_serial_unique_for_create(
    device_data: DeviceCreate,
    db: Session = Depends(get_db),
) -> DeviceCreate:
    """Valida que el número de serie no esté duplicado al crear un dispositivo."""
    existing = device_service.get_device_by_serial(db, device_data.serial_number)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un dispositivo con ese número de serie",
        )
    return device_data


def validate_serial_unique_for_update(
    device_data: DeviceUpdate,
    db_device: Device = Depends(get_device_or_404),
    db: Session = Depends(get_db),
) -> tuple[DeviceUpdate, Device]:
    """
    Valida el número de serie al actualizar (PUT). Depende de get_device_or_404,
    formando una cadena: primero se confirma que el dispositivo existe,
    luego se valida el serial, sin duplicar la búsqueda.
    """
    existing = device_service.get_device_by_serial(db, device_data.serial_number)
    if existing is not None and existing.id != db_device.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un dispositivo con ese número de serie",
        )
    return device_data, db_device