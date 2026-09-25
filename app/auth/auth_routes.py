"""
Endpoints de autenticación: registro, login y perfil del usuario autenticado.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import auth_service
from app.auth.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from app.dependencies.auth_dependency import get_current_active_user
from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.schemas.auth_schema import Token, UserRegister
from app.schemas.user_schema import UserResponse
from app.services.user_service import get_user_by_email
from fastapi import Request
from app.middlewares.rate_limiter import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
    response_description="Usuario registrado exitosamente, sin exponer la contraseña.",
    responses={400: {"description": "Correo ya registrado"}},
)
@limiter.limit("3/minute")
def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_data.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese correo",
        )
    return auth_service.register_user(db, user_data)


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    response_description="Token de acceso JWT.",
    responses={401: {"description": "Credenciales incorrectas"}},
)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Consultar usuario autenticado",
    response_description="Datos del usuario dueño del token enviado.",
    responses={401: {"description": "Token inválido o ausente"}},
)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user