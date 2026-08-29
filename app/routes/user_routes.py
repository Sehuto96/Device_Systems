from fastapi import APIRouter, HTTPException, Path, Query, status
from typing import Optional
from app.schemas.user_schemas import UserCreate, UserResponse, RoleEnum

router = APIRouter(prefix="/users", tags=["Users"])
fake_db: list[dict] = []
next_id = 1


@router.get("", response_model=list[UserResponse])
def get_users(
    role: Optional[RoleEnum] = Query(None, description="Filtrar por rol"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
):
    results = fake_db
    if role is not None:
        results = [u for u in results if u["role"] == role]
    if is_active is not None:
        results = [u for u in results if u["is_active"] == is_active]
    return results


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int = Path(..., gt=0, description="ID del usuario")):
    for user in fake_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    global next_id
    if any(u["email"] == user.email for u in fake_db):
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese correo")

    new_user = user.model_dump()
    new_user["id"] = next_id
    fake_db.append(new_user)
    next_id += 1
    return new_user