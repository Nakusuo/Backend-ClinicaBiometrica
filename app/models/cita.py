from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctores.id"), nullable=False)
    fecha = Column(String(50), nullable=True)
    hora = Column(String(20), nullable=True)
    estado = Column(String(30), default="programada") # programada, en_curso, finalizada, cancelada
    motivo = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    paciente = relationship("Paciente")
    doctor = relationship("Doctor")
