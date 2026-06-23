from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.database import Base

class Expediente(Base):
    __tablename__ = "expedientes"

    id = Column(Integer, primary_key=True)

    paciente_id = Column(
        Integer,
        ForeignKey("pacientes.id", ondelete="CASCADE")
    )

    alergias_conocidas = Column(Text)
    padecimientos_cronicos = Column(Text)
    grupo_sanguineo = Column(String(5))
    factor_rh = Column(String(2))

    historial_resumido = Column(Text)
    antecedentes_familiares = Column(Text)
    antecedentes_quirurgicos = Column(Text)
    habitos_salud = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())

    paciente = relationship(
        "Paciente",
        back_populates="expediente"
    )

    consultas = relationship(
        "Consulta",
        back_populates="expediente"
    )