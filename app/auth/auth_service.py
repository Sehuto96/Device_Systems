"""
Lógica de negocio para autenticación: registro y verificación de credenciales.
Desacoplada de FastAPI, igual que el resto de las capas de servicios.
"""

from app.auth.security import get_password_hash, verify_password
from app.models.user_model import User
from app.schemas.auth_schema import UserRegister
from sqlalchemy.orm import Session


def register_user(db: Session, user_data: UserRegister) -> User:
    """
    Crea un nuevo usuario con la contraseña hasheada.
    La unicidad del email ya fue validada en la ruta antes de llegar aquí.
    """
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role.value,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Verifica las credenciales de un usuario.
    Retorna el usuario si son válidas, None en caso contrario.
    """
    from app.services.user_service import get_user_by_email

    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user