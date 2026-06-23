from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Expediente(Base):
    __tablename__ = "expedientes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False)
    
    alergias_conocidas = Column(Text, nullable=True)
    padecimientos_cronicos = Column(Text, nullable=True)
    grupo_sanguineo = Column(String(5), nullable=True)
    factor_rh = Column(String(2), nullable=True)
    
    historial_resumido = Column(Text, nullable=True)
    antecedentes_familiares = Column(Text, nullable=True)
    antecedentes_quirurgicos = Column(Text, nullable=True)
    habitos_salud = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    paciente = relationship("Paciente")
