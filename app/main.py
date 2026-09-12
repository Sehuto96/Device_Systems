from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.connection import create_tables
from app.routes import user_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se ejecuta al iniciar la aplicación: crea las tablas si no existen
    create_tables()
    yield
    # Aquí podría ir lógica de cierre (cleanup) si se necesitara en el futuro


app = FastAPI(
    title="device_systems API",
    description="API REST para la gestión de usuarios del sistema device_systems. "
                 "Permite crear, consultar, actualizar y eliminar usuarios, "
                 "con persistencia en base de datos mediante SQLAlchemy, "
                 "manejo profesional de errores y validaciones.",
    version="3.0.0",
    contact={
        "name": "Sebastian Hurtado",
        "url": "https://github.com/Sehuto96/Device_Systems",
    },
    openapi_tags=[
        {
            "name": "Usuarios",
            "description": "Operaciones sobre el recurso de usuarios: creación, consulta, "
                            "actualización y eliminación, con persistencia en base de datos.",
        },
    ],
    lifespan=lifespan,
)


@app.middleware("http")
async def add_custom_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "3.0"
    return response


app.include_router(user_routes.router)


@app.get("/", tags=["Root"], summary="Endpoint raíz", description="Mensaje de bienvenida de la API.")
def read_root():
    return {"message": "Bienvenido a device_system API"}