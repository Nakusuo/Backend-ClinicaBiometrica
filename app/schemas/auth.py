from pydantic import BaseModel, EmailStr, Field
from typing import Annotated, List, Literal, Optional

# face-api.js produce descriptores de 128 valores
Embedding = Annotated[List[float], Field(min_length=128, max_length=128)]

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
    fechaNacimiento: str
    password: str = Field(min_length=8)
    faceEmbedding: Optional[Embedding] = None
