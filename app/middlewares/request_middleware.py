"""
Middleware personalizado para trazabilidad de peticiones.
Agrega cabeceras de diagnóstico y registra cada petición en el log.
"""

import logging
import time
import uuid

from fastapi import Request

logger = logging.getLogger("device_systems")
logging.basicConfig(level=logging.INFO)


async def request_tracing_middleware(request: Request, call_next):
    # --- Antes del endpoint ---
    inicio = time.perf_counter()

    # Reutiliza el X-Request-ID del cliente si lo envía (útil en sistemas
    # distribuidos), o genera uno nuevo si no viene
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])

    # --- Llama al endpoint ---
    response = await call_next(request)

    # --- Después del endpoint ---
    duracion = time.perf_counter() - inicio

    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-Process-Time"] = f"{duracion:.4f}"
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "method=%s path=%s status=%d duration=%.4fs request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duracion,
        request_id,
    )

    return response