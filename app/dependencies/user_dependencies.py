# app/dependencies/user_dependencies.py
from fastapi import HTTPException, Path, Header, Depends
from typing import Optional
from app.services import user_service
from app.schemas.user_schemas import UserCreate, UserUpdate


def get_user_or_404(user_id: int = Path(..., gt=0, description="ID del usuario")) -> dict:
    """
    Dependencia reutilizable: busca un usuario por ID.
    Si no existe, lanza 404 automáticamente antes de llegar al endpoint.
    """
    user = user_service.find_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


def validate_email_unique_for_create(user: UserCreate) -> UserCreate:
    """
    Dependencia: valida que el correo no esté duplicado al crear un usuario.
    FastAPI inyecta aquí el mismo body que llega al endpoint (UserCreate),
    valida antes de que la función de la ruta se ejecute, y si pasa, lo retorna.
    """
    if user_service.email_exists(user.email):
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese correo")
    return user


def validate_email_unique_for_update(
    user_update: UserUpdate,
    user: dict = Depends(get_user_or_404),
) -> UserUpdate:
    """
    Dependencia: valida que el correo no esté duplicado al actualizar (PUT).
    Nota cómo esta dependencia depende a su vez de get_user_or_404 — FastAPI
    resuelve la cadena automáticamente y reutiliza el mismo resultado sin
    volver a buscar el usuario dos veces.
    """
    if any(
        u["email"] == user_update.email and u["id"] != user["id"]
        for u in user_service.list_users()
    ):
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese correo")
    return user_update


def get_api_settings() -> dict:
    """
    Dependencia reutilizable: configuración general de la API.
    Útil para inyectar metadatos comunes en varios endpoints.
    """
    return {
        "app_name": "device_systems",
        "api_version": "2.0.0",
    }


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> None:
    """
    Dependencia reutilizable: simula autenticación básica mediante cabecera.
    El cliente debe enviar la cabecera X-API-Key.
    """
    if x_api_key is None or x_api_key != "secreto123":
        raise HTTPException(status_code=401, detail="API Key inválida o ausente")