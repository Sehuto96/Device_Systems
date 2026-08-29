# device_systems – API REST de Gestión de Usuarios

API REST desarrollada con **FastAPI** para la gestión del recurso `usuarios` dentro del sistema **device_systems**. Implementa validaciones con **Pydantic v2**, parámetros de ruta (path parameters), parámetros de consulta (query parameters), modelos de respuesta (`response_model`) y cabeceras HTTP personalizadas.

**Autor:** Sebastian Hurtado
**Actividad:** Fundamentos de FastAPI – API REST para Gestión de Usuarios

---

## Tabla de contenido

1. [Descripción de la aplicación](#descripción-de-la-aplicación)
2. [Instalación de dependencias](#instalación-de-dependencias)
3. [Ejecución del servidor](#ejecución-del-servidor)
4. [Tabla de endpoints](#tabla-de-endpoints)
5. [Capturas de Swagger UI](#capturas-de-swagger-ui)
6. [Evidencia de pruebas GET /users](#evidencia-de-pruebas-get-users)
7. [Evidencia de pruebas GET /users/{user_id}](#evidencia-de-pruebas-get-usersuser_id)
8. [Evidencia de pruebas POST /users](#evidencia-de-pruebas-post-users)
9. [Evidencia de validaciones y errores](#evidencia-de-validaciones-y-errores)
10. [Reflexión sobre el uso de FastAPI](#reflexión-sobre-el-uso-de-fastapi-para-construir-apis-rest)

---

## Descripción de la aplicación

`device_systems` es una API REST construida con FastAPI que permite administrar los usuarios del sistema. Sobre el recurso `usuarios` se pueden realizar las siguientes operaciones:

- Listar todos los usuarios registrados.
- Consultar un usuario específico mediante su identificador (path parameter).
- Filtrar usuarios por rol (`admin`, `support`, `user`) y por estado (`is_active`) mediante query parameters.
- Registrar un nuevo usuario, validando los datos de entrada con Pydantic v2 y evitando correos duplicados.

Cada respuesta utiliza un `response_model` para estandarizar la salida y ocultar datos que no deben exponerse, y todas las respuestas incluyen las cabeceras personalizadas `X-App-Name` y `X-API-Version`.

**Estructura del proyecto:**

```
device_systems/
│── app/
│   │── main.py
│   │── schemas/
│   │   │── user_schemas.py
│   │── routes/
│   │   │── user_routes.py
│── pyproject.toml
│── uv.lock
│── README.md
```

---

## Instalación de dependencias

El proyecto usa **uv** como gestor de dependencias y entornos virtuales.

```bash
# Clonar el repositorio
git clone <URL-del-repositorio>
cd device_systems

# Sincronizar/instalar dependencias declaradas en pyproject.toml
uv sync

# Dependencia adicional para validación de correos (EmailStr)
uv add "pydantic[email]"
```

Dependencias principales:

| Paquete | Uso |
|---|---|
| `fastapi` | Framework para construir la API REST |
| `uvicorn[standard]` | Servidor ASGI para ejecutar la aplicación |
| `pydantic[email]` | Validación de datos y formato de correo electrónico |

---

## Ejecución del servidor

```bash
uv run uvicorn app.main:app --reload
```

El servidor queda disponible en:

- API: `http://127.0.0.1:8000`
- Documentación interactiva (Swagger UI): `http://127.0.0.1:8000/docs`
- Documentación alternativa (ReDoc): `http://127.0.0.1:8000/redoc`

---

## Tabla de endpoints

| Método | Endpoint | Descripción | Parámetros |
|---|---|---|---|
| GET | `/` | Mensaje de bienvenida de la API | — |
| GET | `/users` | Lista todos los usuarios registrados | Query: `role`, `is_active` (opcionales) |
| GET | `/users/{user_id}` | Consulta un usuario por su ID | Path: `user_id` |
| POST | `/users` | Registra un nuevo usuario | Body: `name`, `email`, `role`, `is_active` |

**Modelo de entrada (`UserCreate`):**

| Campo | Tipo | Validación |
|---|---|---|
| `name` | string | Obligatorio, mínimo 3 caracteres |
| `email` | string (email) | Formato de correo válido |
| `role` | enum | Uno de: `admin`, `support`, `user` |
| `is_active` | boolean | Por defecto `true` |

**Modelo de salida (`UserResponse`):** igual al de entrada, más el campo `id` generado por el servidor.

**Cabeceras personalizadas en todas las respuestas:**

| Cabecera | Valor |
|---|---|
| `X-App-Name` | `device_systems` |
| `X-API-Version` | `1.0` |

---







**Ejemplo de petición y respuesta:**

```http
GET /users?role=admin HTTP/1.1
```

```json
[
  {
    "name": "Sebastian Hurtado",
    "email": "sehuto96@gmail.com",
    "role": "admin",
    "is_active": true,
    "id": 1
  }
]
```




```http
GET /users/1 HTTP/1.1
```

```json
{
  "name": "Sebastian Hurtado",
  "email": "sehuto96@gmail.com",
  "role": "admin",
  "is_active": true,
  "id": 1
}
```

### Consulta con ID inexistente (404)



```json
{
  "detail": "Usuario no encontrado"
}
```

---

## Evidencia de pruebas POST /users



```http
POST /users HTTP/1.1
Content-Type: application/json
```

```json
{
  "name": "Esteban Torres",
  "email": "este@example.com",
  "role": "admin",
  "is_active": true
}
```

**Respuesta:**

```json
{
  "name": "Esteban Torres",
  "email": "este@example.com",
  "role": "admin",
  "is_active": true,
  "id": 2
}
```

**Cabeceras de respuesta:**
```
x-api-version: 1.0
x-app-name: device_systems
```

---

## Evidencia de validaciones y errores

### Correo duplicado (400)


```json
{
  "detail": "Ya existe un usuario con ese correo"
}
```

### Rol inválido (422 – validación automática de Pydantic)

`[Captura: POST /users con "role": "gerente" — código 422]`

```json
{
  "name": "Prueba Rol",
  "email": "pruebarol@example.com",
  "role": "gerente",
  "is_active": true
}
```

**Respuesta:**

```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["body", "role"],
      "msg": "Input should be 'admin', 'support' or 'user'",
      "input": "gerente"
    }
  ]
}
```

### Nombre demasiado corto (422)

`[Captura opcional: POST /users con "name" de menos de 3 caracteres — código 422]`

### Correo con formato inválido (422)

`[Captura opcional: POST /users con un email mal formado — código 422]`

---

## Reflexión sobre el uso de FastAPI para construir APIs REST

*(Espacio para tu reflexión personal — a continuación una guía de puntos que puedes desarrollar con tus propias palabras)*

Durante el desarrollo de esta actividad pude comprobar cómo FastAPI simplifica la construcción de una API REST al integrar de forma nativa la validación de datos mediante Pydantic. Definir los modelos `UserCreate` y `UserResponse` permitió separar claramente lo que el cliente envía de lo que el servidor devuelve, evitando exponer información innecesaria y estandarizando las respuestas con `response_model`.

El uso de **path parameters** (`/users/{user_id}`) frente a **query parameters** (`?role=admin`, `?is_active=true`) dejó clara la diferencia entre identificar un recurso específico y filtrar una colección de recursos, algo esencial en el diseño de APIs REST.

La generación automática de documentación interactiva (Swagger UI) resultó especialmente útil para probar cada endpoint sin necesidad de herramientas externas, y para verificar visualmente las validaciones (errores 422 generados automáticamente por Pydantic) y las reglas de negocio implementadas manualmente (como el error 400 por correo duplicado).

Finalmente, trabajar con **cabeceras HTTP personalizadas** mediante un middleware permitió entender cómo se puede enriquecer cada respuesta de la API con metadatos propios de la aplicación, útiles por ejemplo para identificar la versión del servicio.

En conjunto, la actividad reforzó la importancia de un buen diseño de modelos de entrada/salida, la validación temprana de datos y el uso de un flujo de trabajo ordenado con Git (ramas `main`, `develop` y `feature`) para el control de versiones del proyecto.
