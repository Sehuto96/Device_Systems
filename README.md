# device_systems

API REST desarrollada con **FastAPI** para la gestión de usuarios, dispositivos y préstamos del sistema `device_systems`. Este proyecto evolucionó desde una API básica de usuarios (GET/POST en memoria), pasando por persistencia con SQLAlchemy y modelos relacionados con Alembic, hasta convertirse en esta versión: una API **protegida y lista para producción**, con autenticación OAuth2 + JWT, hash de contraseñas, autorización por roles, middleware personalizado, CORS, rate limiting y validaciones avanzadas con Pydantic v2.

## Descripción de la API

`device_systems` expone los recursos:

- `/auth` — registro, login y perfil del usuario autenticado.
- `/users` — gestión de usuarios (protegido).
- `/devices` — gestión de dispositivos (protegido por rol).
- `/loans` — gestión de préstamos (protegido por rol).
- `/security` — información pública sobre las políticas de seguridad de la API.

Funcionalidades principales:

- Registro de usuarios con contraseña segura (hash con `bcrypt` vía `passlib`).
- Autenticación OAuth2 con tokens JWT (`python-jose`).
- Protección de rutas mediante dependencias (`get_current_active_user`, `require_roles`, `require_admin`).
- Autorización basada en roles (`admin`, `support`, `user`).
- Middleware personalizado de trazabilidad (tiempo de respuesta, `X-Request-ID`, logging).
- CORS configurado para clientes frontend autorizados.
- Rate limiting con `slowapi` en endpoints sensibles.
- Validaciones avanzadas con Pydantic v2 (`field_validator`, `model_config`, `Field()`).
- CRUD completo de usuarios, dispositivos y préstamos, con relaciones, joins y filtros (heredado de la actividad anterior).

## Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python (>=3.14) | Lenguaje base |
| FastAPI | Framework principal de la API |
| Pydantic v2 | Validación y serialización de datos |
| SQLAlchemy | ORM y persistencia |
| Alembic | Migraciones de base de datos |
| Uvicorn | Servidor ASGI |
| uv | Gestor de dependencias y entornos virtuales |
| passlib[bcrypt] | Hash seguro de contraseñas |
| python-jose[cryptography] | Generación y validación de tokens JWT |
| python-multipart | Procesamiento de formularios (login OAuth2) |
| slowapi | Rate limiting |
| Swagger UI / ReDoc | Documentación automática |

## Estructura del proyecto

```
device_systems/
├── app/
│   ├── main.py                          # Punto de entrada: FastAPI, CORS, middleware, rate limiter, routers
│   ├── auth/
│   │   ├── auth_routes.py               # Endpoints /auth (register, login, me)
│   │   ├── auth_service.py              # Lógica de registro y autenticación
│   │   └── security.py                  # Hash de contraseñas y JWT (crear/validar)
│   ├── database/
│   │   └── connection.py                # Engine, SessionLocal, Base declarativa
│   ├── models/
│   │   ├── user_model.py                # User (con hashed_password, role, is_active)
│   │   ├── device_model.py              # Device
│   │   └── loan_model.py                # Loan
│   ├── schemas/
│   │   ├── user_schema.py               # Schemas de User (RoleEnum, CRUD, respuesta)
│   │   ├── device_schema.py             # Schemas de Device
│   │   ├── loan_schema.py               # Schemas de Loan
│   │   └── auth_schema.py               # UserRegister, UserLogin, Token, TokenData
│   ├── routes/
│   │   ├── user_routes.py               # Endpoints /users (protegidos)
│   │   ├── device_routes.py             # Endpoints /devices (protegidos por rol)
│   │   └── loan_routes.py               # Endpoints /loans (protegidos)
│   ├── services/
│   │   ├── user_service.py
│   │   ├── device_service.py
│   │   └── loan_service.py
│   ├── dependencies/
│   │   ├── database_dependency.py       # get_db
│   │   ├── user_dependencies.py         # get_user_or_404, validación de email único
│   │   ├── device_dependencies.py
│   │   ├── loan_dependencies.py
│   │   └── auth_dependency.py           # get_current_user, get_current_active_user, require_roles, require_admin
│   └── middlewares/
│       ├── request_middleware.py        # Trazabilidad: X-Process-Time, X-Request-ID, logging
│       └── rate_limiter.py              # Instancia compartida de Limiter (slowapi)
├── alembic/
│   └── versions/
├── .env                                 # Variables de entorno (no versionado)
├── .env.example                         # Plantilla de variables de entorno
├── alembic.ini
├── pyproject.toml
├── uv.lock
├── requirements.txt
└── README.md
```

## Variables de entorno

Copia `.env.example` a `.env` y define:

```
SECRET_KEY=genera-una-clave-con-python -c "import secrets; print(secrets.token_hex(32))"
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Instalación y ejecución

```bash
git clone https://github.com/Sehuto96/Device_Systems.git
cd device_systems
git checkout device_systems_security

uv sync

# Configura tu .env (ver sección anterior)

alembic upgrade head

uv run fastapi dev app/main.py
```

El servidor queda disponible en:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Roles del sistema

| Rol | Descripción |
|---|---|
| `admin` | Acceso total: crear, actualizar y eliminar dispositivos; gestionar préstamos. |
| `support` | Puede crear y actualizar dispositivos, gestionar devoluciones de préstamos; no puede eliminar dispositivos. |
| `user` | Puede consultar usuarios/dispositivos y crear préstamos, sin permisos administrativos. |

## Tabla de endpoints y protección

| Recurso | Método | Ruta | Protección | Límite de peticiones |
|---|---|---|---|---|
| Auth | POST | `/auth/register` | Pública | 3/minuto |
| Auth | POST | `/auth/login` | Pública | 5/minuto |
| Auth | GET | `/auth/me` | Autenticado | — |
| Usuarios | GET | `/users` | Autenticado | 30/minuto |
| Usuarios | GET | `/users/{user_id}` | Autenticado | — |
| Usuarios | PUT/PATCH/DELETE | `/users/{user_id}` | Sin protección adicional* | — |
| Dispositivos | GET | `/devices`, `/devices/{id}` | Pública | — |
| Dispositivos | POST | `/devices` | admin o support | — |
| Dispositivos | PUT | `/devices/{device_id}` | admin o support | — |
| Dispositivos | DELETE | `/devices/{device_id}` | admin | — |
| Préstamos | GET | `/loans`, `/loans/{id}` | Pública | — |
| Préstamos | POST | `/loans` | Autenticado | 10/minuto |
| Préstamos | PATCH | `/loans/{loan_id}/return` | admin o support | — |
| Préstamos | GET | `/loans/details` | admin o support | — |
| Security | GET | `/security/policy` | Pública | — |

\* La guía de la actividad no exige proteger estas rutas; quedan pendientes de una futura iteración.

## Códigos de estado HTTP utilizados

| Código | Significado | Cuándo se retorna |
|---|---|---|
| 200 OK | Operación exitosa | GET, PUT, PATCH, login exitosos |
| 201 Created | Recurso creado | POST exitoso (registro, dispositivo, préstamo) |
| 204 No Content | Eliminación exitosa | DELETE exitoso |
| 400 Bad Request | Solicitud inválida | Correo duplicado, PATCH sin campos |
| 401 Unauthorized | Token ausente, inválido o expirado; credenciales incorrectas | Rutas protegidas sin token válido, login fallido |
| 403 Forbidden | Usuario autenticado sin el rol requerido | Operación restringida por rol |
| 404 Not Found | Recurso no encontrado | Usuario/dispositivo/préstamo inexistente |
| 422 Unprocessable Entity | Error de validación | Contraseña insegura, rol inválido, datos mal formados |
| 429 Too Many Requests | Límite de peticiones excedido | Rate limiting activado |

## Autenticación: registro, login y tokens

### Registro — `POST /auth/register`

```json
{
  "name": "Sebastian Hurtado",
  "email": "sebastian@example.com",
  "password": "MiPass123",
  "role": "user"
}
```

La contraseña debe tener mínimo 8 caracteres, al menos una mayúscula, una minúscula, un número, y no contener espacios. La contraseña nunca se guarda en texto plano: se hashea con `bcrypt` antes de persistirse, y el campo `hashed_password` nunca se expone en las respuestas.

### Login — `POST /auth/login`

Recibe las credenciales como **form-data** (estándar `OAuth2PasswordRequestForm`, campo `username` = email), no como JSON — esto permite que el botón **Authorize** de Swagger funcione automáticamente.

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Perfil autenticado — `GET /auth/me`

Requiere header `Authorization: Bearer <token>`. Retorna los datos del usuario dueño del token, sin `hashed_password`.

## Middleware personalizado

Cada petición pasa por `request_tracing_middleware`, que agrega:

- `X-App-Name: device_systems`
- `X-Process-Time`: tiempo de procesamiento en segundos.
- `X-Request-ID`: identificador único de la petición (reutiliza el del cliente si lo envía, o genera uno nuevo).

Además, registra en el log el método, la ruta, el código de estado y la duración de cada petición.

## Configuración de CORS

Se configuró `CORSMiddleware` permitiendo los orígenes de desarrollo local `http://localhost:5173` (Vite) y `http://localhost:3000` (React), con `allow_credentials=True`, `allow_methods=["*"]` y `allow_headers=["*"]`.

**¿Por qué no usar `allow_origins=["*"]` en producción cuando hay credenciales?**

El comodín `"*"` combinado con `allow_credentials=True` está prohibido por la especificación CORS (y Starlette lo rechaza en tiempo de ejecución). La razón es de seguridad: si el servidor aceptara credenciales desde *cualquier* origen sin distinción, un sitio malicioso podría hacer peticiones autenticadas a la API en nombre de un usuario con sesión activa, sin que el navegador lo impidiera — justo lo que CORS existe para evitar. Por eso, en producción, `allow_origins` debe listar explícitamente los dominios exactos del frontend autorizado.

## Rate limiting

Implementado con `slowapi`, identificando clientes por dirección IP:

| Endpoint | Límite |
|---|---|
| `POST /auth/register` | 3 por minuto |
| `POST /auth/login` | 5 por minuto |
| `GET /users` | 30 por minuto |
| `POST /loans` | 10 por minuto |

Al superar el límite, la API responde `429 Too Many Requests`.

## Dificultades técnicas y cómo se resolvieron

**Incompatibilidad `passlib` + `bcrypt` reciente:** `passlib` 1.7.4 (su última versión, sin mantenimiento activo desde hace años) intenta leer `bcrypt.__about__.__version__` para detectar la versión instalada, atributo que las versiones de `bcrypt` 4.1+ eliminaron. Esto producía `AttributeError` al hashear contraseñas. Se resolvió fijando la dependencia a `bcrypt<4.1`.

**Migración con columna `NOT NULL` sobre datos existentes:** al agregar `hashed_password` como campo obligatorio, SQLite no permite añadir una columna `NOT NULL` directamente sobre una tabla con filas existentes. La migración se ajustó en 3 pasos: agregar la columna como *nullable*, rellenar las filas existentes con un valor placeholder inválido (no utilizable para login), y luego forzar `NOT NULL`.

**Import circular con `slowapi`:** el decorador `@limiter.limit(...)` se usa en los routers, pero la instancia `Limiter` se registra en `main.py`, que a su vez importa los routers — esto causaba un import circular. Se resolvió moviendo la instancia `Limiter` a un módulo independiente (`app/middlewares/rate_limiter.py`), importado tanto por `main.py` como por los routers.

## Evidencia de pruebas funcionales

### Estructura del proyecto

![Estructura del proyecto](/Imagenes/Security/EstructuraProyecto.png)

### Migración Alembic aplicada

![Migracion alembic cabecera](/Imagenes/Security/AlembicCurrentHead.png)

### Registro de usuario

![Registro usuario correcto](/Imagenes/Security/RegistroExitoso.png)

### Registro con contraseña débil

![Registro con contraseña debil](/Imagenes/Security/ContraseñaDebil.png)

### Registro con email duplicado

![Registro con Email duplicado](/Imagenes/Security/CorreoDuplicado.png)

### Login correcto y token generado

![captura del login (200) con access_token](/Imagenes/Security/LoginCorrecto.png)

### Login con contraseña incorrecta

![captura del error 401](/Imagenes/Security/ContraseñaIncorrecta.png)

### Consulta de /auth/me

![captura de la respuesta, sin hashed_password](/Imagenes/Security/RespuestaSinHashed.png)

### Acceso a ruta protegida sin token

![captura del error 401](/Imagenes/Security/CabecerasMiddleware.png)

### Acceso con token inválido

![captura del error 401](/Imagenes/Security/TokenInvalido.png)

### Acceso con usuario sin permisos

![captura del error 403](/Imagenes/Security/UsuarioSinPermiso.png)

### Creación de dispositivo con rol permitido

![captura del dispositivo creado (201)](/Imagenes/Security/DispositivoNuevoRolPermitido.png)

### Eliminación de dispositivo con rol no permitido

![captura del error 403](/Imagenes/Security/UsuarioSinPermiso.png)

### Configuración CORS

![captura de la respuesta con las cabeceras access-control](/Imagenes/Security/CabecerasAcces.png)

### Cabeceras generadas por middleware

![captura con X-App-Name, X-Process-Time, X-Request-ID](/Imagenes/Security/CabecerasMiddleware.png)

### Activación de rate limiting

![captura de los 6 intentos, con el sexto en 429](/Imagenes/Security/IntentosIngresoYCodigos.png)

### Swagger/OpenAPI con OAuth2

![captura general de /docs mostrando los 5 grupos y el candado de las rutas protegidas](/Imagenes/Security/SwaggerOpenApi.png)

## Reflexión final

Esta actividad transformó `device_systems` de una API funcional a una API lista para producción. La diferencia clave no fue solo agregar login, sino cambiar la forma de pensar cada endpoint: ya no basta con que la lógica de negocio sea correcta, también hay que preguntarse *quién puede llamar a esta ruta*.

Entender el flujo OAuth2 completo (por qué el token lleva `sub` y `exp`, por qué el login usa form-data en vez de JSON, y cómo encadenar dependencias como `require_roles` sin duplicar código) fue el mayor aprendizaje. La dificultad técnica más real fue la incompatibilidad entre `passlib` y versiones recientes de `bcrypt` — un recordatorio de que, en proyectos reales, las versiones de las dependencias importan tanto como el código propio.

Como siguiente paso, agregaría refresh tokens y un mecanismo de revocación, ya que por ahora un JWT robado sigue siendo válido hasta que expira por sí solo.

## Autor

Sebastian Hurtado — [GitHub](https://github.com/Sehuto96/Device_Systems)
