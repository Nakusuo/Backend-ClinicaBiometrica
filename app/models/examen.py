from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Examen(Base):
    __tablename__ = "examenes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    consulta_id = Column(Integer, ForeignKey("consultas.id", ondelete="CASCADE"), nullable=False)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=True)
    doctor_solicitante_id = Column(Integer, ForeignKey("doctores.id"), nullable=True)
    
    tipo_examen = Column(String(50), nullable=True)
    nombre_examen = Column(String(150), nullable=False)
    categoria = Column(String(50), nullable=True)
    resultado = Column(Text, nullable=True)
    archivo_url = Column(String(255), nullable=True)
    es_imagen = Column(Boolean, default=False)
    
    fecha_solicitud = Column(DateTime, server_default=func.now())
    fecha_resultado = Column(DateTime, nullable=True)
    estado = Column(String(20), default="pendiente") # pendiente, en_proceso, completado
    notas_doctor = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    consulta = relationship("Consulta")
    paciente = relationship("Paciente")
    doctor_solicitante = relationship("Doctor", foreign_keys=[doctor_solicitante_id])
