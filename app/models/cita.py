from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.database import Base

class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True)

    paciente_id = Column(
        Integer,
        ForeignKey("pacientes.id", ondelete="CASCADE")
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctores.id", ondelete="CASCADE")
    )

    fecha = Column(TIMESTAMP)

    estado = Column(String(30), default="pendiente")
    motivo = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())

    paciente = relationship(
        "Paciente",
        back_populates="citas"
    )

    doctor = relationship(
        "Doctor",
        back_populates="citas"
    )

    consultas = relationship(
        "Consulta",
        back_populates="cita"
    )