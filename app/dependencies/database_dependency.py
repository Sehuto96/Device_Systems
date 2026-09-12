"""
Dependencia de FastAPI para obtener una sesión de base de datos.
Se inyecta con Depends() en los endpoints que necesitan
consultar o modificar datos.
"""

from typing import Generator

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()