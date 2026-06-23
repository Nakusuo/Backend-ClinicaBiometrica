from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ExpedienteBase(BaseModel):
    paciente_id: Optional[int] = None
    patientId: Optional[int] = None
    doctor_id: Optional[int] = None
    doctorId: Optional[int] = None
    historial: Optional[str] = None
    diagnostico: Optional[str] = None
    tratamiento: Optional[str] = None
    notas: Optional[str] = None
    observaciones: Optional[str] = None
    fecha: Optional[str] = None

class ExpedienteCreate(ExpedienteBase):
    pass

class ExpedienteResponse(BaseModel):
    id: int
    paciente_id: int
    patientId: int
    doctor_id: Optional[int] = None
    doctorId: Optional[int] = None
    historial: Optional[str] = None
    diagnostico: Optional[str] = None
    tratamiento: Optional[str] = None
    notas: Optional[str] = None
    observaciones: Optional[str] = None
    fecha: Optional[str] = None
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
