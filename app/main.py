from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.auth import auth_routes
from app.routes import device_routes, loan_routes, user_routes
from app.database.connection import create_tables
from fastapi.middleware.cors import CORSMiddleware
from app.middlewares.request_middleware import request_tracing_middleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.middlewares.rate_limiter import limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se ejecuta al iniciar la aplicación: crea las tablas si no existen
    create_tables()
    yield
    # Aquí podría ir lógica de cierre (cleanup) si se necesitara en el futuro


app = FastAPI(
    title="device_systems API",
    description="API REST segura para la gestión de usuarios, dispositivos y préstamos "
                 "del sistema device_systems. Incluye autenticación OAuth2 con JWT, "
                 "hash de contraseñas, control de acceso por roles, middleware de "
                 "trazabilidad, CORS y rate limiting.",
    version="3.0.0",
    contact={
        "name": "Sebastian Hurtado",
        "url": "https://github.com/Sehuto96/Device_Systems",
    },
    openapi_tags=[
        {
            "name": "Auth",
            "description": "Registro, inicio de sesión y consulta del usuario autenticado. "
                            "Emite y valida tokens JWT mediante el flujo OAuth2PasswordBearer.",
        },
        {
            "name": "Usuarios",
            "description": "Operaciones sobre el recurso de usuarios: consulta, "
                            "actualización y eliminación, protegidas por autenticación.",
        },
        {
            "name": "Dispositivos",
            "description": "Operaciones sobre el recurso de dispositivos: creación, consulta, "
                            "actualización, eliminación y filtros por tipo, marca y disponibilidad. "
                            "Creación y modificación restringidas por rol.",
        },
        {
            "name": "Préstamos",
            "description": "Gestión de préstamos de dispositivos: creación, consulta, "
                            "devolución y filtros por estado, usuario o dispositivo. "
                            "Creación requiere autenticación; devolución restringida por rol.",
        },
        {
            "name": "Security",
            "description": "Información pública sobre las políticas de seguridad de la API "
                    "(requisitos de contraseña, expiración de tokens).",
        },
    ],
    lifespan=lifespan,
)

origenes_permitidos = [
    "http://localhost:5173",  # Vite (frontend típico de la actividad)
    "http://localhost:3000",  # React
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(request_tracing_middleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(device_routes.router)
app.include_router(loan_routes.router)


@app.get("/", tags=["Root"], summary="Endpoint raíz", description="Mensaje de bienvenida de la API.")
def read_root():
    return {"message": "Bienvenido a device_system API"}

@app.get(
    "/security/policy",
    tags=["Security"],
    summary="Consultar política de seguridad",
    description="Expone los requisitos de seguridad de la API: reglas de contraseña "
    "y tiempo de expiración de tokens. No expone secretos ni configuración sensible.",
)
def get_security_policy():
    from app.auth.security import ACCESS_TOKEN_EXPIRE_MINUTES

    return {
        "password_policy": {
            "min_length": 8,
            "requires_uppercase": True,
            "requires_lowercase": True,
            "requires_number": True,
            "allows_whitespace": False,
        },
        "token_policy": {
            "type": "JWT (Bearer)",
            "algorithm": "HS256",
            "expires_in_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
        },
    }