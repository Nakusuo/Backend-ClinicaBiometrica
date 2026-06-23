from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.database import Base

class Llamada(Base):
    __tablename__ = "llamadas"

    id = Column(Integer, primary_key=True)

    cita_id = Column(Integer, ForeignKey("citas.id", ondelete="CASCADE"))
    paciente_id = Column(Integer, ForeignKey("pacientes.id"))
    doctor_id = Column(Integer, ForeignKey("doctores.id"))

    room_id = Column(String(50), unique=True)

    estado = Column(String(20), default="esperando")

    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)

    duracion = Column(Integer)

    created_at = Column(TIMESTAMP, server_default=func.now())

    paciente = relationship("Paciente", back_populates="llamadas")
    doctor = relationship("Doctor", back_populates="llamadas")