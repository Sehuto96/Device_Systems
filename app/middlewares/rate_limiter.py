"""
Instancia compartida del limitador de peticiones (slowapi).
Vive en su propio módulo para evitar imports circulares entre
main.py y los routers que aplican límites (@limiter.limit(...)).
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)