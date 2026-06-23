from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.db.database import Base

class Doctor(Base):
    __tablename__ = "doctores"

    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    especialidad = Column(String(100))
    password_hash = Column(String)
    embedding_facial = Column(String)
    rol = Column(String(20), default="doctor")
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    citas = relationship("Cita", back_populates="doctor")
    consultas = relationship("Consulta", back_populates="doctor")
    recetas = relationship("Receta", back_populates="doctor")
    examenes = relationship("Examen", back_populates="doctor")
    llamadas = relationship("Llamada", back_populates="doctor")