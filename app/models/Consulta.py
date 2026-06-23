from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from app.db.database import Base

class Consulta(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True)

    expediente_id = Column(
        Integer,
        ForeignKey("expedientes.id", ondelete="CASCADE")
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctores.id")
    )

    cita_id = Column(
        Integer,
        ForeignKey("citas.id")
    )

    fecha_consulta = Column(TIMESTAMP, server_default=func.now())

    motivo_consulta = Column(Text)
    sintomas = Column(Text)

    signos_vitales = Column(JSON)

    diagnostico_principal = Column(Text)
    diagnostico_diferencial = Column(Text)

    notas_doctor = Column(Text)

    tipo_consulta = Column(String(30))
    estado = Column(String(20), default="activa")

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())

    expediente = relationship(
        "Expediente",
        back_populates="consultas"
    )

    doctor = relationship(
        "Doctor",
        back_populates="consultas"
    )

    cita = relationship(
        "Cita",
        back_populates="consultas"
    )

    recetas = relationship(
        "Receta",
        back_populates="consulta"
    )

    examenes = relationship(
        "Examen",
        back_populates="consulta"
    )