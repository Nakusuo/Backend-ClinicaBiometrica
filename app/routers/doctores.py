from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate
from app.core.biometria import DIMENSION_EMBEDDING
from app.core.security import get_current_user, get_current_doctor, prohibido
from app.routers.auth import hash_password
import json

router = APIRouter()

class BiometriaRequest(BaseModel):
    embedding: list[float] = Field(min_length=DIMENSION_EMBEDDING, max_length=DIMENSION_EMBEDDING)

def map_doctor(d: Doctor) -> dict:
    if not d:
        return None
    return {
        "id": d.id,
        "nombres": d.nombres,
        "apellidos": d.apellidos,
        "nombre": d.nombres,      # Compatibilidad con Angular
        "apellido": d.apellidos,  # Compatibilidad con Angular
        "correo": d.correo,
        "email": d.correo,        # Compatibilidad con Angular
        "especialidad": d.especialidad,
        "cedula": d.cedula,
        "telefono": d.telefono,
        "activo": d.activo,
        "rol": d.rol,
        "created_at": d.created_at
    }

def obtener_doctor_o_404(doctor_id: int, db: Session) -> Doctor:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    return doctor

def exigir_misma_cuenta(current_doctor: Doctor, doctor_id: int) -> None:
    if current_doctor.id != doctor_id:
        raise prohibido("Solo puedes modificar tu propia cuenta de médico")

@router.get("/")
def listar_doctores(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    doctores = db.query(Doctor).all()
    return [map_doctor(d) for d in doctores]

@router.get("/{doctor_id}")
def obtener_doctor(doctor_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return map_doctor(obtener_doctor_o_404(doctor_id, db))

@router.post("/")
def crear_doctor(payload: DoctorCreate, db: Session = Depends(get_db), current_doctor = Depends(get_current_doctor)):
    existing = db.query(Doctor).filter(Doctor.correo == payload.correo).first()
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya se encuentra registrado.")

    doctor = Doctor(
        nombres=payload.nombres,
        apellidos=payload.apellidos,
        correo=payload.correo,
        especialidad=payload.especialidad,
        cedula=payload.cedula,
        telefono=payload.telefono,
        password_hash=hash_password(payload.password),
        # La biometría la registra cada médico desde su propia cuenta
        embedding_facial=None,
        activo=payload.activo
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return map_doctor(doctor)

@router.put("/{doctor_id}")
def actualizar_doctor(doctor_id: int, payload: DoctorCreate, db: Session = Depends(get_db), current_doctor = Depends(get_current_doctor)):
    exigir_misma_cuenta(current_doctor, doctor_id)
    doctor = obtener_doctor_o_404(doctor_id, db)

    doctor.nombres = payload.nombres
    doctor.apellidos = payload.apellidos
    doctor.correo = payload.correo
    doctor.especialidad = payload.especialidad
    doctor.cedula = payload.cedula
    doctor.telefono = payload.telefono
    # "activo" no se cambia aquí: se usa /activar

    db.commit()
    db.refresh(doctor)
    return map_doctor(doctor)

@router.delete("/{doctor_id}")
def eliminar_doctor(doctor_id: int, db: Session = Depends(get_db), current_doctor = Depends(get_current_doctor)):
    exigir_misma_cuenta(current_doctor, doctor_id)
    doctor = obtener_doctor_o_404(doctor_id, db)
    db.delete(doctor)
    db.commit()
    return {"mensaje": "Doctor eliminado"}

@router.post("/{doctor_id}/activar")
def activar_doctor(doctor_id: int, db: Session = Depends(get_db), current_doctor = Depends(get_current_doctor)):
    """Aprueba a un médico que se registró solo (DOCTOR_REQUIRES_APPROVAL=true)."""
    doctor = obtener_doctor_o_404(doctor_id, db)
    doctor.activo = True
    db.commit()
    db.refresh(doctor)
    return map_doctor(doctor)

@router.post("/{doctor_id}/biometria")
def guardar_biometria_doctor(doctor_id: int, payload: BiometriaRequest, db: Session = Depends(get_db), current_doctor = Depends(get_current_doctor)):
    exigir_misma_cuenta(current_doctor, doctor_id)
    doctor = obtener_doctor_o_404(doctor_id, db)
    doctor.embedding_facial = json.dumps(payload.embedding)
    db.commit()
    return {"mensaje": "Biometría registrada exitosamente"}
