"""
Rutas del recurso /devices.
Define los endpoints HTTP y delega la lógica a device_service.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.dependencies.device_dependencies import (
    get_device_or_404,
    validate_serial_unique_for_create,
    validate_serial_unique_for_update,
)
from app.dependencies.auth_dependency import require_admin, require_roles
from app.models.device_model import Device
from app.schemas.device_schema import (
    DeviceCreate,
    DevicePatch,
    DeviceResponse,
    DeviceUpdate,
)
from app.schemas.loan_schema import LoanResponse
from app.services import device_service, loan_service

router = APIRouter(prefix="/devices", tags=["Dispositivos"])


@router.get(
    "",
    response_model=list[DeviceResponse],
    summary="Listar dispositivos",
    description="Lista dispositivos con filtros opcionales por tipo, disponibilidad, marca y búsqueda de texto.",
    response_description="Lista de dispositivos que cumplen con los filtros aplicados.",
)
def list_devices(
    device_type: Optional[str] = Query(default=None, description="Filtrar por tipo de dispositivo"),
    is_available: Optional[bool] = Query(default=None, description="Filtrar por disponibilidad"),
    brand: Optional[str] = Query(default=None, description="Filtrar por marca"),
    search: Optional[str] = Query(default=None, description="Buscar en nombre, serial o marca"),
    db: Session = Depends(get_db),
):
    return device_service.get_all_devices(
        db, device_type=device_type, is_available=is_available, brand=brand, search=search
    )


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Consultar dispositivo por ID",
    response_description="Datos del dispositivo solicitado.",
    responses={404: {"description": "Dispositivo no encontrado"}},
)
def get_device(db_device: Device = Depends(get_device_or_404)):
    return db_device


@router.get(
    "/{device_id}/loans",
    response_model=list[LoanResponse],
    summary="Consultar historial de préstamos de un dispositivo",
    response_description="Lista de préstamos asociados al dispositivo, activos e históricos.",
    responses={404: {"description": "Dispositivo no encontrado"}},
)
def get_device_loans(db_device: Device = Depends(get_device_or_404), db: Session = Depends(get_db)):
    return loan_service.get_loans_by_device(db, db_device.id)


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear dispositivo",
    response_description="Dispositivo creado exitosamente, con is_available en true por defecto.",
    responses={400: {"description": "Número de serie ya registrado"}},
)
def create_device(
    device_data: DeviceCreate = Depends(validate_serial_unique_for_create),
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("admin", "support")),
):
    return device_service.create_device(db, device_data)


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar dispositivo completo",
    response_description="Dispositivo actualizado con todos sus campos reemplazados.",
    responses={
        404: {"description": "Dispositivo no encontrado"},
        400: {"description": "Número de serie ya registrado por otro dispositivo"},
    },
)
def update_device(
    data=Depends(validate_serial_unique_for_update),
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("admin", "support")),
):
    device_data, db_device = data
    return device_service.update_device_full(db, db_device, device_data)


@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar dispositivo parcial",
    response_description="Dispositivo actualizado con los campos enviados.",
    responses={404: {"description": "Dispositivo no encontrado"}},
)
def patch_device(
    device_data: DevicePatch,
    db_device: Device = Depends(get_device_or_404),
    db: Session = Depends(get_db),
):
    if not device_data.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar",
        )

    if device_data.serial_number is not None:
        existing_device = device_service.get_device_by_serial(db, device_data.serial_number)
        if existing_device is not None and existing_device.id != db_device.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un dispositivo con ese número de serie",
            )

    return device_service.update_device_partial(db, db_device, device_data)


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar dispositivo",
    response_description="Dispositivo eliminado; no se retorna contenido.",
    responses={404: {"description": "Dispositivo no encontrado"}},
)
def delete_device(
    db_device: Device = Depends(get_device_or_404),
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
):
    device_service.delete_device(db, db_device)
    return None