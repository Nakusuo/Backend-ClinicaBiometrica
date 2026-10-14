import base64
import hashlib
import hmac
import time

from app.core.config import settings


def credenciales_turn(usuario: str, secreto: str, ttl: int, ahora: float | None = None) -> dict:
    """Credencial temporal de coturn (use-auth-secret): el usuario lleva su vencimiento
    y la clave es HMAC-SHA1 del usuario con el secreto compartido."""
    vence = int((ahora if ahora is not None else time.time()) + ttl)
    username = f"{vence}:{usuario}"
    clave = hmac.new(secreto.encode(), username.encode(), hashlib.sha1).digest()
    return {"username": username, "credential": base64.b64encode(clave).decode()}


def ice_servers(usuario: str) -> list[dict]:
    servidores = [{"urls": settings.stun_urls}] if settings.stun_urls else []
    if settings.turn_urls and settings.turn_secret:
        servidores.append({"urls": settings.turn_urls,
                           **credenciales_turn(usuario, settings.turn_secret, settings.turn_ttl_segundos)})
    return servidores
