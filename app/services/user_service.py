# app/services/user_service.py
from app.data.user_data import fake_db
from app.schemas.user_schemas import UserCreate, RoleEnum
from typing import Optional


def list_users(role: Optional[RoleEnum] = None, is_active: Optional[bool] = None) -> list[dict]:
    results = fake_db
    if role is not None:
        results = [u for u in results if u["role"] == role]
    if is_active is not None:
        results = [u for u in results if u["is_active"] == is_active]
    return results


def find_user_by_id(user_id: int) -> Optional[dict]:
    return next((u for u in fake_db if u["id"] == user_id), None)


def email_exists(email: str, exclude_id: Optional[int] = None) -> bool:
    return any(
        u["email"] == email and u["id"] != exclude_id
        for u in fake_db
    )


def create_user(user: UserCreate) -> dict:
    import app.data.user_data as data
    new_user = user.model_dump()
    new_user["id"] = data.next_id
    fake_db.append(new_user)
    data.next_id += 1
    return new_user

from app.schemas.user_schemas import UserUpdate, UserPatch


def replace_user(user_id: int, user_update: UserUpdate) -> dict:
    """Reemplaza completamente un usuario existente (PUT)."""
    user = find_user_by_id(user_id)
    updated_data = user_update.model_dump()
    updated_data["id"] = user_id
    user.clear()
    user.update(updated_data)
    return user


def patch_user(user_id: int, patch_data: dict) -> dict:
    """Actualiza parcialmente un usuario existente (PATCH)."""
    user = find_user_by_id(user_id)
    user.update(patch_data)
    return user

def delete_user(user_id: int) -> None:
    """Elimina un usuario existente de la base de datos en memoria."""
    user = find_user_by_id(user_id)
    fake_db.remove(user)