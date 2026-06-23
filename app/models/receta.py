from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.database import Base

class Receta(Base):
    __tablename__ = "recetas"

    id = Column(Integer, primary_key=True)

    consulta_id = Column(Integer, ForeignKey("consultas.id", ondelete="CASCADE"))
    paciente_id = Column(Integer, ForeignKey("pacientes.id"))
    doctor_id = Column(Integer, ForeignKey("doctores.id"))

    nombre_medicamento = Column(String(150), nullable=False)
    concentracion = Column(String(50))
    presentacion = Column(String(50))
    dosis = Column(String(100))
    frecuencia = Column(String(100))
    duracion_tratamiento = Column(String(50))
    indicaciones_especiales = Column(Text)

    fecha_receta = Column(TIMESTAMP, server_default=func.now())
    activo = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())

    consulta = relationship("Consulta", back_populates="recetas")
    paciente = relationship("Paciente", back_populates="recetas")
    doctor = relationship("Doctor", back_populates="recetas")