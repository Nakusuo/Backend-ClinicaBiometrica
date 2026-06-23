from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CitaBase(BaseModel):
    paciente_id: int
    doctor_id: int
    fecha: Optional[str] = None
    hora: Optional[str] = None
    estado: Optional[str] = "programada"
    motivo: Optional[str] = None

class CitaCreate(CitaBase):
    pass

class CitaUpdateEstado(BaseModel):
    estado: str

class CitaResponse(BaseModel):
    id: int
    paciente_id: int
    doctor_id: int
    patientId: int
    doctorId: int
    fecha: Optional[str] = None
    hora: Optional[str] = None
    estado: str
    motivo: Optional[str] = None
    created_at: datetime
    patientName: Optional[str] = None
    doctorName: Optional[str] = None
    age: Optional[int] = 30

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
