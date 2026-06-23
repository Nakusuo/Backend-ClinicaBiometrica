from pydantic import BaseModel, EmailStr
from typing import List, Optional

class FacialLoginRequest(BaseModel):
    correo: EmailStr
    embedding_facial: List[float]

class DoctorRegisterRequest(BaseModel):
    nombre: str
    email: EmailStr
    especialidad: str
    cedula: str
    telefono: str
    password: str
    faceEmbedding: List[float]

class PatientRegisterRequest(BaseModel):
    nombre: str
    apellido: str
    dni: str
    email: EmailStr
    telefono: str
    fechaNacimiento: str
    password: str
    faceEmbedding: Optional[List[float]] = None