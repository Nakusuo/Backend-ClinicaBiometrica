from sqlalchemy import Column, Integer, String, Boolean
from app.db.database import Base

class Doctor(Base):
    __tablename__ = "doctores"

    id = Column(Integer, primary_key=True)
    nombres = Column(String)
    apellidos = Column(String)
    correo = Column(String, unique=True)
    especialidad = Column(String)
    password_hash = Column(String)
    embedding_facial = Column(String)
    rol = Column(String)
    activo = Column(Boolean)