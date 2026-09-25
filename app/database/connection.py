"""
Módulo de conexión a la base de datos.
Configura el engine, la fábrica de sesiones (SessionLocal)
y la clase base declarativa para los modelos SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 1. URL de conexión — SQLite para desarrollo
DATABASE_URL = "sqlite:///./device_systems.db"

# 2. Motor de base de datos
# check_same_thread=False es necesario porque SQLite por defecto
# solo permite un hilo; FastAPI puede manejar múltiples requests concurrentes.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 3. Fábrica de sesiones
# autocommit=False -> control manual de cuándo confirmar cambios (commit)
# autoflush=False  -> no sincroniza automáticamente antes de cada consulta
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# 4. Base declarativa: todos los modelos heredarán de esta clase
class Base(DeclarativeBase):
    pass


def create_tables():
    """
    Crea todas las tablas definidas en los modelos que heredan de Base.
    Se debe llamar una vez al iniciar la aplicación (en main.py).
    """
    Base.metadata.create_all(bind=engine)