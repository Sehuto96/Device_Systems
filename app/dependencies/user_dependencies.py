"""
Dependencias reutilizables para el recurso User.
Encapsulan validaciones comunes (existencia de usuario, email único)
para evitar repetir lógica en cada endpoint.
"""

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate
from app.services import user_service


def get_user_or_404(
    user_id: int = Path(..., description="ID del usuario a buscar"),
    db: Session = Depends(get_db),
) -> User:
    """
    Busca un usuario por ID y lanza 404 automáticamente si no existe.
    Usado en GET por ID, PUT, PATCH y DELETE.
    """
    db_user = user_service.get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return db_user


def validate_email_unique_for_create(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> UserCreate:
    """
    Valida que el email no esté ya registrado antes de crear un usuario.
    """
    existing_user = user_service.get_user_by_email(db, user_data.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese correo",
        )
    return user_data


def validate_email_unique_for_update(
    user_data: UserUpdate,
    db_user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
) -> tuple[UserUpdate, User]:
    """
    Valida que el nuevo email no pertenezca a otro usuario distinto
    al que se está actualizando. Depende de get_user_or_404,
    formando una cadena: primero se confirma que el usuario existe,
    luego se valida el correo, sin repetir la búsqueda por ID.
    """
    existing_user = user_service.get_user_by_email(db, user_data.email)
    if existing_user is not None and existing_user.id != db_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese correo",
        )
    return user_data, db_user