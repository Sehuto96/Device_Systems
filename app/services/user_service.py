"""
Capa de servicios para el recurso User.
Contiene la lógica de negocio y el acceso a la base de datos,
desacoplada de FastAPI para facilitar pruebas y mantenimiento.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserPatch, UserUpdate


def create_user(db: Session, user_data: UserCreate) -> User:
    """Crea un nuevo usuario en la base de datos."""
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        role=user_data.role.value,
        is_active=user_data.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_users(
    db: Session,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    order_by: Optional[str] = None,
) -> list[User]:
    """
    Lista usuarios, con filtros opcionales por rol y estado,
    y ordenamiento opcional por nombre o fecha de creación.
    """
    query = db.query(User)

    if role is not None:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if order_by == "name":
        query = query.order_by(User.name)
    elif order_by == "created_at":
        query = query.order_by(User.created_at)

    return query.all()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Busca un usuario por su ID. Retorna None si no existe."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Busca un usuario por su email. Retorna None si no existe."""
    return db.query(User).filter(User.email == email).first()


def update_user_full(db: Session, db_user: User, user_data: UserUpdate) -> User:
    """Reemplaza completamente los datos de un usuario (PUT)."""
    db_user.name = user_data.name
    db_user.email = user_data.email
    db_user.role = user_data.role.value
    db_user.is_active = user_data.is_active

    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_partial(db: Session, db_user: User, user_data: UserPatch) -> User:
    """Actualiza parcialmente un usuario (PATCH), solo los campos enviados."""
    update_data = user_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "role" and value is not None:
            value = value.value
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, db_user: User) -> None:
    """Elimina un usuario existente de la base de datos."""
    db.delete(db_user)
    db.commit()