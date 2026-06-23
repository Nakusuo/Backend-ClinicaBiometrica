from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class PacienteBase(BaseModel):
    nombre: str
    apellido: str
    dni: str
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    fechaNacimiento: Optional[str] = None
    direccion: Optional[str] = None

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
