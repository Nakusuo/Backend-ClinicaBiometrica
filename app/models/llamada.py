from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Llamada(Base):
    __tablename__ = "llamadas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cita_id = Column(Integer, ForeignKey("citas.id", ondelete="CASCADE"), nullable=False)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("doctores.id"), nullable=True)
    room_id = Column(String(50), unique=True, nullable=True)
    estado = Column(String(20), default="esperando") # esperando, activa, terminada
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duracion = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    cita = relationship("Cita")
    paciente = relationship("Paciente")
    doctor = relationship("Doctor")
