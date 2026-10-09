from datetime import date, datetime, timezone


def ahora_utc() -> datetime:
    """Hora actual en UTC, sin zona horaria.

    Las columnas DateTime de la base no guardan zona, así que se mantiene el mismo
    formato que producía datetime.utcnow() (obsoleto desde Python 3.12).
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def calcular_edad(fecha_nacimiento: str | None, hoy: date | None = None) -> int | None:
    """Edad en años a partir de 'AAAA-MM-DD'. None si la fecha falta o no es válida."""
    if not fecha_nacimiento:
        return None
    try:
        nacimiento = date.fromisoformat(fecha_nacimiento[:10])
    except ValueError:
        return None
    hoy = hoy or date.today()
    return hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
