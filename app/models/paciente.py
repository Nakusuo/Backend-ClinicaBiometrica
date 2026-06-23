from sqlalchemy import Column, Integer, String, Date, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.db.database import Base

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String(20), unique=True, nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    telefono = Column(String(20))
    correo = Column(String(100))
    fecha_nacimiento = Column(Date)
    direccion = Column(Text)
    genero = Column(String(10))

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())

    expediente = relationship(
        "Expediente",
        back_populates="paciente",
        uselist=False
    )

    citas = relationship("Cita", back_populates="paciente")
    recetas = relationship("Receta", back_populates="paciente")
    examenes = relationship("Examen", back_populates="paciente")
    llamadas = relationship("Llamada", back_populates="paciente")