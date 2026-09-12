# device_systems

API REST desarrollada con **FastAPI** para la gestión de usuarios del sistema `device_systems`. Este proyecto evoluciona desde una API básica en memoria (GET/POST), pasando por un CRUD completo también en memoria, hasta esta versión actual que incorpora **persistencia real de datos mediante SQLAlchemy y una base de datos relacional (SQLite)**.

## Descripción de la API

`device_systems` expone el recurso `/users`, permitiendo:

- Crear, listar, consultar, actualizar (completa y parcialmente) y eliminar usuarios, **almacenados de forma persistente en base de datos**.
- Filtrar usuarios por rol (`admin`, `support`, `user`) y por estado activo.
- Ordenar usuarios por nombre o fecha de creación.
- Validar datos de entrada mediante modelos Pydantic.
- Aplicar restricciones de integridad a nivel de base de datos (`NOT NULL`, `UNIQUE`) mediante modelos SQLAlchemy.
- Manejar errores de forma clara y consistente usando `HTTPException`.
- Documentación automática interactiva vía Swagger UI y ReDoc.
- Reutilización de lógica común mediante Dependency Injection (`Depends()`).

## Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python 3.14 | Lenguaje base |
| FastAPI | Framework principal de la API |
| SQLAlchemy | ORM para persistencia de datos en base de datos relacional |
| SQLite | Motor de base de datos relacional (desarrollo) |
| Pydantic v2 | Validación y serialización de datos |
| Uvicorn | Servidor ASGI |
| uv | Gestor de dependencias y entornos virtuales |
| Swagger UI / ReDoc | Documentación automática |

## Estructura del proyecto

El proyecto sigue una separación de responsabilidades por capas, ahora incluyendo la capa de persistencia:

```
device_systems/
├── app/
│   ├── main.py                          # Punto de entrada, configuración de FastAPI, middleware y creación de tablas
│   ├── database/
│   │   └── connection.py                # Engine, SessionLocal, Base declarativa y create_tables()
│   ├── models/
│   │   └── user_model.py                # Modelo SQLAlchemy: estructura real de la tabla 'users'
│   ├── routes/
│   │   └── user_routes.py               # Definición de endpoints del recurso /users
│   ├── schemas/
│   │   └── user_schema.py               # Schemas Pydantic (entrada y salida de la API)
│   ├── services/
│   │   └── user_service.py              # Lógica de negocio y operaciones CRUD contra la base de datos
│   └── dependencies/
│       ├── database_dependency.py       # Dependencia get_db(): entrega una sesión de BD por request
│       └── user_dependencies.py         # Dependencias reutilizables con Depends()
├── device_systems.db                    # Archivo de base de datos SQLite (generado automáticamente)
├── pyproject.toml
├── uv.lock
├── requirements.txt
└── README.md
```

### Captura — Estructura del proyecto

<!-- INSERTAR AQUÍ: /Imagenes/EstructuraProyecto.png -->

**Explicación de las capas:**

- **database**: configura la conexión con la base de datos (`engine`, `SessionLocal`, `Base`) y expone `create_tables()` para generar el esquema al iniciar la aplicación.
- **models**: define las tablas reales de la base de datos mediante clases SQLAlchemy (`Column`, tipos SQL, constraints). Es la capa de **persistencia**.
- **schemas**: define la forma de los datos que entran y salen de la API mediante Pydantic. Es la capa de **presentación/validación**, independiente del modelo de base de datos.
- **routes**: define los endpoints (URLs, métodos HTTP, códigos de estado) y delega la lógica a `services`.
- **services**: contiene la lógica de negocio y las consultas SQLAlchemy (crear, buscar, filtrar, actualizar, eliminar), desacoplada de FastAPI.
- **dependencies**: funciones reutilizables inyectadas con `Depends()` — incluye tanto la sesión de base de datos (`get_db`) como validaciones de negocio (`get_user_or_404`, correo único).

## Modelo SQLAlchemy vs. Schema Pydantic

Uno de los aprendizajes centrales de esta fase es la diferencia entre estos dos conceptos, que cumplen roles distintos y complementarios:

| | **Modelo SQLAlchemy** (`user_model.py`) | **Schema Pydantic** (`user_schema.py`) |
|---|---|---|
| Hereda de | `Base` (DeclarativeBase) | `BaseModel` |
| Representa | Una tabla en la base de datos | La forma de los datos de entrada/salida de la API |
| Define | Columnas con tipos SQL (`Column`, `Integer`, `String`, `Boolean`, `DateTime`) | Campos con type hints de Python y validaciones (`EmailStr`, `Field`, `Enum`) |
| Aplica | Constraints de integridad (`nullable=False`, `unique=True`) — la **última línea de defensa**, se cumplen sin importar el origen de los datos | Reglas de negocio de la API (formato de email, longitud mínima, valores permitidos de `role`) — validación **antes** de tocar la base de datos |
| Se expone al cliente | **No**, es interno | **Sí**, es lo que ve el consumidor de la API |
| Ejemplo en el proyecto | `User` (una sola clase, representa la tabla `users`) | `UserCreate`, `UserUpdate`, `UserPatch`, `UserResponse` (varios schemas, cada uno para un propósito distinto) |

En la práctica, un mismo dato pasa por ambas capas en cada request: primero Pydantic valida el JSON de entrada (`UserCreate`/`UserUpdate`/`UserPatch`), luego ese dato validado se usa para crear o modificar un objeto `User` de SQLAlchemy, que es lo que finalmente se persiste en `device_systems.db`. Al responder, el objeto `User` se convierte de nuevo a un schema (`UserResponse`) gracias a `model_config = ConfigDict(from_attributes=True)`.

## Persistencia de datos

A diferencia de la versión anterior de `device_systems` (donde los usuarios se almacenaban en una lista de Python que se perdía al reiniciar el servidor), esta versión persiste los datos en un archivo real de base de datos: **`device_systems.db`** (SQLite).

**Configuración de la conexión** (`app/database/connection.py`):

```python
DATABASE_URL = "sqlite:///./device_systems.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass
```

Las tablas se crean automáticamente al iniciar la aplicación (mediante el `lifespan` de FastAPI en `main.py`), llamando a `Base.metadata.create_all(bind=engine)`.

**Gestión de sesiones por request** (`app/dependencies/database_dependency.py`):

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Cada request HTTP obtiene su propia sesión de base de datos mediante `Depends(get_db)`, que se cierra automáticamente al finalizar la petición, evite o no una excepción.

### Captura — Base de datos generada

<!-- INSERTAR AQUÍ: /Imagenes/BaseDatosGenerada.png -->
*Vista de la tabla `users` desde la extensión SQLite Viewer de VS Code, mostrando los registros persistidos en `device_systems.db`.*

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/Sehuto96/Device_Systems.git
cd device_systems
```

### 2. Instalar dependencias con uv

```bash
uv sync
```

### 3. Ejecutar el servidor de desarrollo

```bash
uv run fastapi dev app/main.py
```

Al iniciar, la aplicación crea automáticamente el archivo `device_systems.db` y la tabla `users` si no existen.

El servidor quedará disponible en:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Tabla de endpoints

| Recurso | Método | Ruta | Descripción | Código de éxito |
|---|---|---|---|---|
| Usuarios | GET | `/users` | Lista usuarios, con filtros opcionales por `role`, `is_active` y ordenamiento por `order_by` | 200 OK |
| Usuarios | GET | `/users/{user_id}` | Consulta un usuario específico por ID | 200 OK |
| Usuarios | POST | `/users` | Crea un nuevo usuario en la base de datos | 201 Created |
| Usuarios | PUT | `/users/{user_id}` | Reemplaza completamente los datos de un usuario | 200 OK |
| Usuarios | PATCH | `/users/{user_id}` | Actualiza parcialmente un usuario | 200 OK |
| Usuarios | DELETE | `/users/{user_id}` | Elimina un usuario existente de la base de datos | 204 No Content |

## Códigos de estado HTTP utilizados

| Código | Significado | Cuándo se retorna |
|---|---|---|
| 200 OK | Operación exitosa | GET, PUT, PATCH exitosos |
| 201 Created | Recurso creado exitosamente | POST exitoso |
| 204 No Content | Eliminación exitosa, sin cuerpo de respuesta | DELETE exitoso |
| 400 Bad Request | Solicitud inválida | Correo duplicado, PATCH sin campos enviados |
| 404 Not Found | Recurso no encontrado | Usuario inexistente en GET, PUT, PATCH o DELETE por ID |
| 422 Unprocessable Entity | Error de validación de datos | Datos con formato/tipo inválido (por ejemplo, rol fuera del enum permitido) |

## Ejemplos de peticiones y respuestas

### Crear usuario — `POST /users`

**Request:**
```json
{
  "name": "Sebastian Hurtado",
  "email": "sebastian@example.com",
  "role": "admin",
  "is_active": true
}
```

**Response — 201 Created:**
```json
{
  "id": 1,
  "name": "Sebastian Hurtado",
  "email": "sebastian@example.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-09-12T01:03:28.275492"
}
```

### Actualización parcial — `PATCH /users/1`

**Request:**
```json
{
  "role": "support"
}
```

**Response — 200 OK:**
```json
{
  "id": 1,
  "name": "Sebastian Hurtado",
  "email": "sebastian@example.com",
  "role": "support",
  "is_active": true,
  "created_at": "2026-09-12T01:03:28.275492"
}
```

### Usuario no encontrado — `GET /users/9999`

**Response — 404 Not Found:**
```json
{
  "detail": "Usuario no encontrado"
}
```

### Correo duplicado — `POST /users`

**Response — 400 Bad Request:**
```json
{
  "detail": "Ya existe un usuario con ese correo"
}
```

### Actualización parcial sin datos — `PATCH /users/1`

**Request:**
```json
{}
```

**Response — 400 Bad Request:**
```json
{
  "detail": "No se enviaron campos para actualizar"
}
```

## Uso de Dependency Injection (`Depends()`)

El proyecto reutiliza lógica común mediante dependencias definidas en `app/dependencies/`:

- **`get_db`** (`database_dependency.py`): entrega una sesión de base de datos (`Session`) por cada request, y la cierra automáticamente al finalizar mediante `yield`/`finally`.
- **`get_user_or_404`**: busca un usuario por `user_id` (tomado del path) usando la sesión de base de datos, y lanza `404` automáticamente si no existe. Se usa en `GET` por ID, `PUT`, `PATCH` y `DELETE`.
- **`validate_email_unique_for_create`**: valida contra la base de datos que el correo no esté duplicado al crear un usuario (`POST`).
- **`validate_email_unique_for_update`**: valida que el correo no esté duplicado al actualizar un usuario (`PUT`). Esta dependencia **depende a su vez de `get_user_or_404`**, formando una cadena de dependencias: FastAPI resuelve primero que el usuario exista, y luego valida el correo, sin duplicar la búsqueda del usuario en la base de datos.

Este enfoque evita repetir la misma validación en múltiples endpoints, centraliza la lógica y hace el código más mantenible y fácil de probar.

## Manejo de errores

La API controla los siguientes escenarios usando `HTTPException`:

- **Usuario no encontrado** → `404 Not Found`, mediante la dependencia `get_user_or_404`.
- **Correo electrónico duplicado** → `400 Bad Request`, tanto al crear como al actualizar (validado contra la base de datos).
- **Rol no permitido** → `422 Unprocessable Entity`, validado automáticamente por Pydantic mediante `RoleEnum` (cualquier valor fuera de `admin`, `support`, `user` es rechazado sin necesidad de código adicional).
- **Actualización parcial sin datos** → `400 Bad Request`, cuando el body de un `PATCH` llega vacío.
- **Eliminación de usuario inexistente** → `404 Not Found`, mediante la misma dependencia `get_user_or_404`.

Adicionalmente, el modelo SQLAlchemy aplica sus propias restricciones de integridad (`nullable=False`, `unique=True` en la columna `email`) como última línea de defensa a nivel de base de datos, incluso si algún dato llegara a saltarse la validación de Pydantic.

Todas las respuestas de error siguen el formato estándar de FastAPI:

```json
{
  "detail": "Mensaje descriptivo del error"
}
```

## Documentación automática

FastAPI genera documentación interactiva automáticamente a partir de los modelos Pydantic y los metadatos configurados en `main.py` (título, descripción, versión, contacto y tags).

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### Captura — Swagger UI

![Swagger](/Imagenes/Swagger.png)

### Captura — ReDoc

![reDoc](/Imagenes/reDoc.png)

## Evidencia de pruebas funcionales

### POST /users — Crear usuario válido

![UsuarioNuevo](/Imagenes/UsuarioNuevo.png)

### GET /users — Listar usuarios

![ListaUsuarios](/Imagenes/ListaUsuarios.png)

### GET /users/{user_id} — Consultar usuario por ID

![UsuarioID](/Imagenes/UsuarioID.png)

### GET /users?role=admin — Filtrar usuarios por rol

![UsuarioRol](/Imagenes/UsuarioRol.png)

### GET /users?is_active=true — Filtrar usuarios activos

![UsuariosActivos](/Imagenes/UsuariosActivos.png)

### PUT /users/{user_id} — Actualización completa

![ActualizacionUsuario](/Imagenes/ActualizacionUsuario.png)

### PATCH /users/{user_id} — Actualización parcial

![ActualizacionParcial](/Imagenes/ActualizacionUsuario.png)

### DELETE /users/{user_id} — Eliminar usuario

![UsuarioEliminado](/Imagenes/UsuarioEliminado.png)

### Verificación de persistencia — Datos en SQLite Viewer

![BaseDatos](/Imagenes/BaseDatos.png)

## Evidencia de errores controlados

### 404 — Usuario no encontrado

![UsuarioNoEncontrado](/Imagenes/UsuarioNoEncontrado.png)

### 400 — Correo duplicado

![CorreoDuplicado](/Imagenes/CorreoRepetido.png)

### 422 — Rol no permitido / datos inválidos

![RolNoPermitido](/Imagenes/RolNoPermitido.png)

### 400 — PATCH sin datos enviados

![DatosVacios](/Imagenes/DatosVacios.png)

### 404 — Eliminación de usuario inexistente

![EliminacionUsuarioInexistente](/Imagenes/EliminarUsuarioInexistente.png)

## Flujo de trabajo con Git

Esta actividad se desarrolló en la rama `feature-sqlalchemy-crud`, creada a partir de `develop` (donde ya estaba mergeado el CRUD completo en memoria de la actividad anterior). Una vez finalizada y probada, esta rama se integró a `develop` mediante un Pull Request en GitHub, siguiendo el mismo flujo de trabajo por ramas utilizado en fases anteriores del proyecto.

## Reflexión final

Uno de los aprendizajes más grandes de esta fase fue comprender la diferencia real entre un **modelo SQLAlchemy** y un **schema Pydantic**. Al principio parecía redundante tener dos representaciones distintas del mismo "usuario", pero al implementar el CRUD completo quedó claro el propósito de cada una: el modelo SQLAlchemy define cómo se almacenan los datos y garantiza su integridad a nivel de base de datos (constraints como `unique=True` o `nullable=False`), mientras que los schemas Pydantic controlan qué información entra y sale por la API, con sus propias reglas de negocio (como el `RoleEnum` o el formato de email). Tener ambas capas separadas permitió, por ejemplo, exponer un `UserResponse` con exactamente los campos que quiero mostrar, sin acoplar la respuesta de la API a la estructura interna de la tabla.

La separación en capas (`database`, `models`, `schemas`, `services`, `dependencies`, `routes`) también se sintió más natural en esta fase que en la anterior: al agregar la base de datos, quedó evidente por qué cada capa existe — `services` concentra toda la lógica de consultas SQLAlchemy, `dependencies` reutiliza validaciones como `get_user_or_404` y la gestión de sesiones (`get_db`), y `routes` queda enfocado únicamente en la definición de endpoints y códigos de estado, sin lógica de negocio mezclada.

En cuanto a la importancia de la persistencia en sí: pasar de una lista de Python en memoria a un archivo real de base de datos (`device_systems.db`) cambia por completo el comportamiento de la API. Antes, cada reinicio del servidor borraba todos los datos; ahora, los usuarios creados sobreviven a reinicios del servidor e incluso a cerrar por completo el entorno de desarrollo, que es justamente el comportamiento que se espera de una API real en producción. Verificar esto directamente en la base de datos (con la extensión SQLite Viewer) fue clave para confirmar que no se trataba solo de respuestas JSON convincentes en Swagger, sino de datos realmente persistidos.

Si continuara evolucionando esta API, el siguiente paso lógico sería migrar de SQLite a PostgreSQL para un entorno de producción (cambiando únicamente la `DATABASE_URL`, gracias a que SQLAlchemy abstrae el motor de base de datos), incorporar Alembic para gestionar migraciones de esquema de forma versionada, y agregar autenticación (hash de contraseñas, JWT) para proteger los endpoints de escritura.

## Autor

Sebastian Hurtado — [GitHub](https://github.com/Sehuto96/Device_Systems)
