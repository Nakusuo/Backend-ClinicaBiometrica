# Importar este paquete registra todas las tablas en Base.metadata (lo usan Alembic y los tests)
from app.models.doctor import Doctor
from app.models.paciente import Paciente
from app.models.cita import Cita
from app.models.expediente import Expediente
from app.models.consulta import Consulta
from app.models.receta import Receta
from app.models.examen import Examen
from app.models.llamada import Llamada

__all__ = ["Doctor", "Paciente", "Cita", "Expediente", "Consulta", "Receta", "Examen", "Llamada"]
