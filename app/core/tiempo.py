from datetime import datetime, timezone


def ahora_utc() -> datetime:
    """Hora actual en UTC, sin zona horaria.

    Las columnas DateTime de la base no guardan zona, así que se mantiene el mismo
    formato que producía datetime.utcnow() (obsoleto desde Python 3.12).
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
