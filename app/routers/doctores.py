from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@router.get("/")
def listar_doctores(db: Session = Depends(get_db)):
    doctores = db.query(Doctor).all()
    return [map_doctor(d) for d in doctores]

@router.get("/{doctor_id}")
def obtener_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    return map_doctor(doctor)

@router.post("/")
def crear_doctor(payload: DoctorCreate, db: Session = Depends(get_db)):
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
        password_hash=None, # Registro directo desde CRUD admin no requiere contraseña hash obligatoria inicial en el demo
        embedding_facial=payload.embedding_facial,
        activo=payload.activo
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return map_doctor(doctor)

@router.put("/{doctor_id}")
def actualizar_doctor(doctor_id: int, payload: DoctorCreate, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    
    doctor.nombres = payload.nombres
    doctor.apellidos = payload.apellidos
    doctor.correo = payload.correo
    doctor.especialidad = payload.especialidad
    doctor.cedula = payload.cedula
    doctor.telefono = payload.telefono
    doctor.activo = payload.activo
    
    db.commit()
    db.refresh(doctor)
    return map_doctor(doctor)

@router.delete("/{doctor_id}")
def eliminar_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    db.delete(doctor)
    db.commit()
    return {"mensaje": "Doctor eliminado"}

@router.post("/{doctor_id}/biometria")
def guardar_biometria_doctor(doctor_id: int, payload: dict, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    
    embedding = payload.get("embedding")
    if not embedding:
        raise HTTPException(status_code=400, detail="Falta el embedding facial")
        
    doctor.embedding_facial = json.dumps(embedding)
    db.commit()
    return {"mensaje": "Biometría registrada exitosamente"}