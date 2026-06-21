from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class Doctor(Base):
    __tablename__ = "doctores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombres = Column(String(100), nullable=True)
    apellidos = Column(String(100), nullable=True)
    correo = Column(String(100), unique=True, index=True, nullable=False)
    especialidad = Column(String(100), nullable=True)
    password_hash = Column(Text, nullable=True)
    embedding_facial = Column(Text, nullable=True)

    rol = Column(String(20), default="doctor")
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())