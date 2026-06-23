from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.database import Base

class Examen(Base):
    __tablename__ = "examenes"

    id = Column(Integer, primary_key=True)

    consulta_id = Column(Integer, ForeignKey("consultas.id", ondelete="CASCADE"))
    paciente_id = Column(Integer, ForeignKey("pacientes.id"))
    doctor_solicitante_id = Column(Integer, ForeignKey("doctores.id"))

    tipo_examen = Column(String(50))
    nombre_examen = Column(String(150), nullable=False)
    categoria = Column(String(50))

    resultado = Column(Text)
    archivo_url = Column(String(255))
    es_imagen = Column(Boolean, default=False)

    fecha_solicitud = Column(TIMESTAMP, server_default=func.now())
    fecha_resultado = Column(TIMESTAMP)

    estado = Column(String(20), default="pendiente")
    notas_doctor = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())

    consulta = relationship("Consulta", back_populates="examenes")
    paciente = relationship("Paciente", back_populates="examenes")
    doctor = relationship("Doctor", back_populates="examenes")