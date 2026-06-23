from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Consulta(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    expediente_id = Column(Integer, ForeignKey("expedientes.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctores.id"), nullable=True)
    cita_id = Column(Integer, ForeignKey("citas.id"), nullable=True)
    
    fecha_consulta = Column(DateTime, server_default=func.now())
    motivo_consulta = Column(Text, nullable=True)
    sintomas = Column(Text, nullable=True)
    signos_vitales = Column(Text, nullable=True) # Almacena JSON serializado como texto para compatibilidad SQLite
    diagnostico_principal = Column(Text, nullable=True)
    diagnostico_diferencial = Column(Text, nullable=True)
    notas_doctor = Column(Text, nullable=True)
    
    tipo_consulta = Column(String(30), nullable=True)
    estado = Column(String(20), default="activa")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    expediente = relationship("Expediente")
    doctor = relationship("Doctor")
    cita = relationship("Cita")
