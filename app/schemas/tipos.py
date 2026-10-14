from datetime import date
from typing import Annotated, List

from pydantic import AfterValidator, BeforeValidator, Field

from app.core.biometria import DIMENSION_EMBEDDING

# face-api.js produce descriptores de 128 valores
Embedding = Annotated[List[float], Field(min_length=DIMENSION_EMBEDDING, max_length=DIMENSION_EMBEDDING)]


def _normalizar_fecha(valor):
    """Acepta 'AAAA-MM-DD' o una fecha ISO con hora y guarda siempre 'AAAA-MM-DD'."""
    if valor is None or valor == "":
        return None
    if isinstance(valor, date):
        return valor.isoformat()[:10]
    if isinstance(valor, str):
        try:
            return date.fromisoformat(valor.strip()[:10]).isoformat()
        except ValueError:
            pass
    raise ValueError("Fecha inválida, usa el formato AAAA-MM-DD")


def _no_futura(valor):
    if valor and date.fromisoformat(valor) > date.today():
        raise ValueError("La fecha de nacimiento no puede estar en el futuro")
    return valor


# Las columnas siguen siendo texto; esto garantiza que lo guardado sea siempre AAAA-MM-DD válido
Fecha = Annotated[str, BeforeValidator(_normalizar_fecha)]
FechaNacimiento = Annotated[str, BeforeValidator(_normalizar_fecha), AfterValidator(_no_futura)]
