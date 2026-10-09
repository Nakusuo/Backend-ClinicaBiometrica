from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.schemas.tipos import FechaNacimiento

class PacienteBase(BaseModel):
    nombre: str
    apellido: str
    dni: str
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    fechaNacimiento: Optional[FechaNacimiento] = None
    direccion: Optional[str] = None
    genero: Optional[str] = None

class PacienteCreate(PacienteBase):
    pass

class PacienteResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    nombres: str
    apellidos: str
    dni: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    correo: Optional[str] = None
    fechaNacimiento: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    direccion: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
