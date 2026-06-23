from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class DoctorBase(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    correo: EmailStr
    especialidad: Optional[str] = None
    cedula: Optional[str] = None
    telefono: Optional[str] = None
    rol: Optional[str] = "doctor"
    activo: Optional[bool] = True

class DoctorCreate(DoctorBase):
    password: str
    embedding_facial: Optional[str] = None

class DoctorResponse(DoctorBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
