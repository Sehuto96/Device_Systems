"""
Dependencias reutilizables para autenticación y autorización.
Extraen el usuario actual desde el token JWT y validan permisos por rol.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.services.user_service import get_user_by_email

# tokenUrl apunta al endpoint de login, para que Swagger sepa dónde
# pedir el token cuando usas el botón "Authorize"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extrae y valida el token JWT del header Authorization.
    Retorna el usuario correspondiente al 'sub' del token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verifica que el usuario autenticado esté activo."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    return current_user


def require_roles(*allowed_roles: str):
    """
    Fábrica de dependencias: retorna una dependencia que exige
    que el usuario autenticado tenga uno de los roles permitidos.

    Uso: Depends(require_roles("admin", "support"))
    """

    def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para esta operación",
            )
        return current_user

    return role_checker


# Atajo para el caso más común: exigir rol admin exclusivamente
def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    return require_roles("admin")(current_user)