# app/routes/user_routes.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from typing import Optional
from app.schemas.user_schemas import UserCreate, UserResponse, UserUpdate, UserPatch, RoleEnum
from app.services import user_service
from app.dependencies.user_dependencies import (
    get_user_or_404,
    validate_email_unique_for_create,
    validate_email_unique_for_update,
    get_api_settings,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Listar usuarios",
    description="Obtiene la lista de usuarios registrados, con filtros opcionales por rol y estado activo.",
    response_description="Lista de usuarios que cumplen los filtros aplicados.",
)
def get_users(
    role: Optional[RoleEnum] = Query(None, description="Filtrar por rol"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
):
    return user_service.list_users(role, is_active)


@router.get(
    "/meta/config",
    summary="Configuración de la API",
    description="Retorna metadatos generales de la API, inyectados mediante Dependency Injection.",
)
def api_config(settings: dict = Depends(get_api_settings)):
    return settings


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar usuario por ID",
    description="Busca y retorna un usuario específico según su ID.",
    response_description="Datos del usuario encontrado.",
)
def get_user(user_id: int = Path(..., gt=0, description="ID del usuario")):
    user = user_service.find_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.get(
    "/meta/config",
    summary="Configuración de la API",
    description="Retorna metadatos generales de la API, inyectados mediante Dependency Injection.",
)
def api_config(settings: dict = Depends(get_api_settings)):
    return settings

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario. Valida que el correo electrónico no esté duplicado.",
    response_description="Usuario creado exitosamente.",
)
def create_user(user: UserCreate = Depends(validate_email_unique_for_create)):
    return user_service.create_user(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario (completo)",
    description="Reemplaza completamente los datos de un usuario existente. Todos los campos son requeridos.",
    response_description="Usuario actualizado con los nuevos datos.",
)
def update_user(
    user_update: UserUpdate = Depends(validate_email_unique_for_update),
    user: dict = Depends(get_user_or_404),
):
    return user_service.replace_user(user["id"], user_update)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario (parcial)",
    description="Actualiza solo los campos enviados por el cliente. Debe enviarse al menos un campo.",
    response_description="Usuario actualizado con los campos modificados.",
)
def patch_user(
    user_patch: UserPatch,
    user: dict = Depends(get_user_or_404),
):
    patch_data = user_patch.model_dump(exclude_unset=True)
    if not patch_data:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

    if "email" in patch_data:
        if any(u["email"] == patch_data["email"] and u["id"] != user["id"] for u in user_service.list_users()):
            raise HTTPException(status_code=400, detail="Ya existe un usuario con ese correo")

    return user_service.patch_user(user["id"], patch_data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario existente. No retorna cuerpo de respuesta.",
    response_description="Usuario eliminado correctamente (sin contenido).",
)
def delete_user(user: dict = Depends(get_user_or_404)):
    user_service.delete_user(user["id"])
    return None

