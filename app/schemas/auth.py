from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional

from app.schemas.tipos import Embedding, FechaNacimiento

class FacialLoginRequest(BaseModel):
    correo: EmailStr
    embedding_facial: Embedding
    role: Optional[Literal["doctor", "paciente"]] = None

class LoginRequest(BaseModel):
    correo: EmailStr
    password: str
    role: Optional[Literal["doctor", "paciente"]] = None

class DoctorRegisterRequest(BaseModel):
    nombre: str
    email: EmailStr
    especialidad: str
    cedula: str
    telefono: str
    password: str = Field(min_length=8)
    faceEmbedding: Embedding

class PatientRegisterRequest(BaseModel):
    nombre: str
    apellido: str
    dni: str
    email: EmailStr
    telefono: str
    fechaNacimiento: FechaNacimiento
    password: str = Field(min_length=8)
    faceEmbedding: Optional[Embedding] = None
