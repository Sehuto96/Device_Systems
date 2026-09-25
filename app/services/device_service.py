"""
Capa de servicios para el recurso Device.
Contiene la lógica de negocio y el acceso a la base de datos.
"""

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DevicePatch, DeviceUpdate


def create_device(db: Session, device_data: DeviceCreate) -> Device:
    """Crea un nuevo dispositivo. is_available inicia en True por defecto del modelo."""
    db_device = Device(
        name=device_data.name,
        serial_number=device_data.serial_number,
        device_type=device_data.device_type,
        brand=device_data.brand,
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_all_devices(
    db: Session,
    device_type: Optional[str] = None,
    is_available: Optional[bool] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
) -> list[Device]:
    """
    Lista dispositivos con filtros opcionales.
    'search' busca coincidencias parciales (ilike) en nombre, serial o marca.
    """
    query = db.query(Device)

    if device_type is not None:
        query = query.filter(Device.device_type == device_type)

    if is_available is not None:
        query = query.filter(Device.is_available == is_available)

    if brand is not None:
        query = query.filter(Device.brand.ilike(brand))

    if search is not None:
        like_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Device.name.ilike(like_pattern),
                Device.serial_number.ilike(like_pattern),
                Device.brand.ilike(like_pattern),
            )
        )

    return query.all()


def get_device_by_id(db: Session, device_id: int) -> Optional[Device]:
    return db.query(Device).filter(Device.id == device_id).first()


def get_device_by_serial(db: Session, serial_number: str) -> Optional[Device]:
    return db.query(Device).filter(Device.serial_number == serial_number).first()


def update_device_full(db: Session, db_device: Device, device_data: DeviceUpdate) -> Device:
    """Reemplaza completamente los datos de un dispositivo (PUT)."""
    db_device.name = device_data.name
    db_device.serial_number = device_data.serial_number
    db_device.device_type = device_data.device_type
    db_device.brand = device_data.brand
    db_device.is_available = device_data.is_available

    db.commit()
    db.refresh(db_device)
    return db_device


def update_device_partial(db: Session, db_device: Device, device_data: DevicePatch) -> Device:
    """Actualiza parcialmente un dispositivo (PATCH), solo los campos enviados."""
    update_data = device_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_device, field, value)

    db.commit()
    db.refresh(db_device)
    return db_device


def delete_device(db: Session, db_device: Device) -> None:
    db.delete(db_device)
    db.commit()