"""
Rutas del recurso /users.
Define los endpoints HTTP y delega la lógica de negocio
a la capa de servicios (user_service).
"""

from typing import Optional
from app.schemas.loan_schema import LoanResponse  
from app.services import loan_service
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from fastapi import Request  # agregar al import existente
from app.middlewares.rate_limiter import limiter
from app.dependencies.database_dependency import get_db
from app.dependencies.user_dependencies import (
    get_user_or_404,
    validate_email_unique_for_update,
    
)
from app.dependencies.auth_dependency import get_current_active_user
from app.models.user_model import User
from app.schemas.user_schema import (
    RoleEnum,
    UserPatch,
    UserResponse,
    UserUpdate,
)
    
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Listar usuarios",
    description="Lista usuarios con filtros opcionales por rol y estado, y ordenamiento.",
    response_description="Lista de usuarios que cumplen con los filtros aplicados.",
)
@limiter.limit("30/minute")
def list_users(
    request: Request,
    role: Optional[RoleEnum] = Query(default=None, description="Filtrar por rol"),
    is_active: Optional[bool] = Query(default=None, description="Filtrar por estado activo"),
    order_by: Optional[str] = Query(
        default=None, description="Ordenar por 'name' o 'created_at'"
    ),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    role_value = role.value if role is not None else None
    return user_service.get_all_users(db, role=role_value, is_active=is_active, order_by=order_by)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar usuario por ID",
    response_description="Datos del usuario solicitado.",
    responses={404: {"description": "Usuario no encontrado"}},
)
def get_user(
    db_user: User = Depends(get_user_or_404),
    _: User = Depends(get_current_active_user),
):
    return db_user

@router.get(
    "/{user_id}/loans",
    response_model=list[LoanResponse],
    summary="Consultar préstamos de un usuario",
    response_description="Lista de préstamos asociados al usuario, activos e históricos.",
    responses={404: {"description": "Usuario no encontrado"}},
)
def get_user_loans(db_user: User = Depends(get_user_or_404), db: Session = Depends(get_db)):
    return loan_service.get_loans_by_user(db, db_user.id)

@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario completo",
    response_description="Usuario actualizado con todos sus campos reemplazados.",
    responses={
        404: {"description": "Usuario no encontrado"},
        400: {"description": "Correo ya registrado por otro usuario"},
    },
)
def update_user(
    data=Depends(validate_email_unique_for_update),
    db: Session = Depends(get_db),
):
    user_data, db_user = data
    return user_service.update_user_full(db, db_user, user_data)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario parcial",
    response_description="Usuario actualizado con los campos enviados.",
    responses={404: {"description": "Usuario no encontrado"}},
)
def patch_user(
    user_data: UserPatch,
    db_user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
):
    if not user_data.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar",
        )

    if user_data.email is not None:
        existing_user = user_service.get_user_by_email(db, user_data.email)
        if existing_user is not None and existing_user.id != db_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con ese correo",
            )

    return user_service.update_user_partial(db, db_user, user_data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    response_description="Usuario eliminado; no se retorna contenido.",
    responses={404: {"description": "Usuario no encontrado"}},
)
def delete_user(
    db_user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
):
    user_service.delete_user(db, db_user)
    return None