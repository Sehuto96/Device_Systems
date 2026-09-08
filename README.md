# device_systems

API REST desarrollada con **FastAPI** para la gestión de usuarios del sistema `device_systems`. Este proyecto evoluciona una API básica de usuarios (operaciones GET y POST) hacia una API REST completa y profesional, implementando CRUD completo, manejo de errores, validación de datos, documentación automática con Swagger/OpenAPI y reutilización de lógica mediante Dependency Injection.

## Descripción de la API

`device_systems` expone el recurso `/users`, permitiendo:

- Crear, listar, consultar, actualizar (completa y parcialmente) y eliminar usuarios.
- Filtrar usuarios por rol (`admin`, `support`, `user`) y por estado activo.
- Validar datos de entrada mediante modelos Pydantic.
- Manejar errores de forma clara y consistente usando `HTTPException`.
- Documentación automática interactiva vía Swagger UI y ReDoc.
- Reutilización de lógica común mediante Dependency Injection (`Depends()`).

## Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python 3.14 | Lenguaje base |
| FastAPI | Framework principal de la API |
| Pydantic v2 | Validación y serialización de datos |
| Uvicorn | Servidor ASGI |
| uv | Gestor de dependencias y entornos virtuales |
| Swagger UI / ReDoc | Documentación automática |

## Estructura del proyecto

El proyecto sigue una separación de responsabilidades por capas:

```
device_systems/
├── app/
│   ├── main.py                     # Punto de entrada, configuración de FastAPI y middleware
│   ├── routes/
│   │   └── user_routes.py          # Definición de endpoints del recurso /users
│   ├── schemas/
│   │   └── user_schemas.py         # Modelos Pydantic (entrada y salida)
│   ├── services/
│   │   └── user_service.py         # Lógica de negocio (búsqueda, creación, actualización, eliminación)
│   ├── dependencies/
│   │   └── user_dependencies.py    # Dependencias reutilizables con Depends()
│   └── data/
│       └── user_data.py            # Simulación de base de datos en memoria
├── pyproject.toml
├── uv.lock
└── README.md
```

**Explicación de las capas:**

- **routes**: define los endpoints (URLs, métodos HTTP, códigos de estado) y delega la lógica a `services`.
- **schemas**: define la forma de los datos que entran y salen de la API (validación con Pydantic).
- **services**: contiene la lógica de negocio, desacoplada de FastAPI, lo que facilita las pruebas y el mantenimiento.
- **dependencies**: funciones reutilizables inyectadas con `Depends()`, que evitan repetir código de validación en múltiples endpoints.
- **data**: simula una base de datos en memoria (`fake_db`), reemplazable en el futuro por una base de datos real sin afectar las demás capas.

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

El servidor quedará disponible en:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Tabla de endpoints

| Recurso | Método | Ruta | Descripción | Código de éxito |
|---|---|---|---|---|
| Usuarios | GET | `/users` | Lista usuarios, con filtros opcionales por `role` e `is_active` | 200 OK |
| Usuarios | GET | `/users/meta/config` | Retorna configuración general de la API (vía Dependency Injection) | 200 OK |
| Usuarios | GET | `/users/{user_id}` | Consulta un usuario específico por ID | 200 OK |
| Usuarios | POST | `/users` | Crea un nuevo usuario | 201 Created |
| Usuarios | PUT | `/users/{user_id}` | Reemplaza completamente los datos de un usuario | 200 OK |
| Usuarios | PATCH | `/users/{user_id}` | Actualiza parcialmente un usuario | 200 OK |
| Usuarios | DELETE | `/users/{user_id}` | Elimina un usuario existente | 204 No Content |

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
  "is_active": true
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
  "is_active": true
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

El proyecto reutiliza lógica común mediante dependencias definidas en `app/dependencies/user_dependencies.py`:

- **`get_user_or_404`**: busca un usuario por `user_id` (tomado del path) y lanza `404` automáticamente si no existe, antes de que la función del endpoint se ejecute. Se usa en `PUT`, `PATCH` y `DELETE`.
- **`validate_email_unique_for_create`**: valida que el correo no esté duplicado al crear un usuario (`POST`), recibiendo directamente el body como dependencia.
- **`validate_email_unique_for_update`**: valida que el correo no esté duplicado al actualizar un usuario (`PUT`). Esta dependencia **depende a su vez de `get_user_or_404`**, formando una cadena de dependencias: FastAPI resuelve primero que el usuario exista, y luego valida el correo, sin duplicar la búsqueda del usuario.
- **`get_api_settings`**: inyecta metadatos generales de la API (nombre y versión), usada en el endpoint `GET /users/meta/config`.

Este enfoque evita repetir la misma validación en múltiples endpoints, centraliza la lógica y hace el código más mantenible y fácil de probar.

## Manejo de errores

La API controla los siguientes escenarios usando `HTTPException`:

- **Usuario no encontrado** → `404 Not Found`, mediante la dependencia `get_user_or_404`.
- **Correo electrónico duplicado** → `400 Bad Request`, tanto al crear como al actualizar.
- **Rol no permitido** → `422 Unprocessable Entity`, validado automáticamente por Pydantic mediante `RoleEnum` (cualquier valor fuera de `admin`, `support`, `user` es rechazado sin necesidad de código adicional).
- **Actualización parcial sin datos** → `400 Bad Request`, cuando el body de un `PATCH` llega vacío.
- **Eliminación de usuario inexistente** → `404 Not Found`, mediante la misma dependencia `get_user_or_404`.

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

![Swagger completo](/Imagenes/SwaggerUI.png)

### Captura — ReDoc

![Redoc](/Imagenes/Redoc.png)

## Evidencia de pruebas funcionales

### GET /users — Listar usuarios

![Lista usuarios](/Imagenes/ListaUsuarios.png)

### GET /users/{user_id} — Consultar usuario por ID

![Busqueda por ID](/Imagenes/BusquedaID.png)

### POST /users — Crear usuario

![Usuarion nuevo](/Imagenes/CreacionUsuario.png)

### PUT /users/{user_id} — Actualización completa

![Actualizacion usuario completa](/Imagenes/ActualizacionUsuario.png)

### PATCH /users/{user_id} — Actualización parcial

![Actualizacion parcial](/Imagenes/ActualizacionParcial.png)

### DELETE /users/{user_id} — Eliminar usuario

<!-- INSERTAR AQUÍ: captura de la prueba -->

### GET /users/meta/config — Configuración vía Dependency Injection

![Usuario eliminado](/Imagenes/UsuarioEliminado.png)

## Evidencia de errores controlados

### 404 — Usuario no encontrado

![Usuario no encontrado](/Imagenes/UsuarioNoEncontrado.png)

### 400 — Correo duplicado

![Correo duplicado](/Imagenes/CorreoRepetido.png)

### 422 — Rol no permitido / datos inválidos

![Rol no permitido](/Imagenes/RolNoPermitido.png)

### 400 — PATCH sin datos enviados

![Sin datos enviados](/Imagenes/SinDatos.png)

### 404 — Eliminación de usuario inexistente

![Eliminacion usuario inexistente](/Imagenes/EliminacionUsuarioInexistente.png)

## Reflexión final


Uno de los aprendizajes más grandes fue la separación en capas (`routes`, `schemas`, `services`, `dependencies`, `data`). Al principio, tener toda la lógica dentro de las funciones de las rutas parecía suficiente, pero al ir agregando PUT, PATCH y DELETE me di cuenta de que estaba repitiendo código de validación una y otra vez. Mover la lógica de negocio a `services` y las validaciones reutilizables a `dependencies` no solo hizo el código más corto, sino mucho más fácil de leer y mantener: cada archivo tiene una responsabilidad clara, y si necesito cambiar cómo se valida un correo duplicado, solo lo hago en un lugar.

En cuanto a dificultades técnicas, la más grande no fue de código sino de entorno: tener el proyecto dentro de una carpeta sincronizada por OneDrive me generó errores recurrentes de acceso denegado (`os error 5`) al intentar que `uv` modificara el entorno virtual. Después de varios intentos fallidos, la solución definitiva fue sacar el proyecto por completo de la carpeta sincronizada, lo cual eliminó el problema de raíz. Esto me dejó una lección clara sobre la importancia de mantener los entornos de desarrollo fuera del alcance de servicios de sincronización en la nube, algo que no había considerado antes de enfrentarme al problema.

En general, este proyecto me ayudó a entender que una API "que funciona" y una API "bien diseñada" no son lo mismo: la segunda piensa en mantenibilidad, manejo de errores predecible y documentación clara desde el principio.

## Autor

Sebastian Hurtado — [GitHub](https://github.com/Sehuto96/Device_Systems)
