from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Receta(Base):
    __tablename__ = "recetas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    consulta_id = Column(Integer, ForeignKey("consultas.id", ondelete="CASCADE"), nullable=False)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("doctores.id"), nullable=True)
    
    nombre_medicamento = Column(String(150), nullable=False)
    concentracion = Column(String(50), nullable=True)
    presentacion = Column(String(50), nullable=True)
    dosis = Column(String(100), nullable=True)
    frecuencia = Column(String(100), nullable=True)
    duracion_tratamiento = Column(String(50), nullable=True)
    indicaciones_especiales = Column(Text, nullable=True)
    
    fecha_receta = Column(DateTime, server_default=func.now())
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    consulta = relationship("Consulta")
    paciente = relationship("Paciente")
    doctor = relationship("Doctor")
