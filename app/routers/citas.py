from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.cita import Cita
from app.models.paciente import Paciente
from app.models.doctor import Doctor
from app.schemas.cita import CitaCreate, CitaUpdateEstado
from app.core.security import get_current_user, get_current_doctor, get_current_patient

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def map_cita(c: Cita) -> dict:
    if not c:
        return None
    age = 30
    patient_name = "Paciente Desconocido"
    if c.paciente:
        patient_name = f"{c.paciente.nombres} {c.paciente.apellidos}"
        if c.paciente.fecha_nacimiento:
            try:
                parts = c.paciente.fecha_nacimiento.split("-")
                if len(parts) == 3:
                    birth_year = int(parts[0])
                    age = 2026 - birth_year
            except:
                pass
                
    doctor_name = "Dr. de Turno"
    if c.doctor:
        doctor_name = f"{c.doctor.nombres} {c.doctor.apellidos}"

    return {
        "id": c.id,
        "paciente_id": c.paciente_id,
        "patientId": c.paciente_id,
        "doctor_id": c.doctor_id,
        "doctorId": c.doctor_id,
        "fecha": c.fecha,
        "hora": c.hora,
        "estado": c.estado,
        "motivo": c.motivo,
        "created_at": c.created_at,
        "patientName": patient_name,
        "doctorName": doctor_name,
        "age": age,
        "time": c.hora,
        "status": c.estado
    }

@router.get("/")
def listar_citas(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    citas = db.query(Cita).all()
    return [map_cita(c) for c in citas]

@router.get("/doctor/{doctor_id}")
def listar_citas_doctor(doctor_id: int, db: Session = Depends(get_db), current_doctor = Depends(get_current_doctor)):
    citas = db.query(Cita).filter(Cita.doctor_id == doctor_id).all()
    return [map_cita(c) for c in citas]

@router.get("/paciente/{patient_id}")
def listar_citas_paciente(patient_id: int, db: Session = Depends(get_db), current_patient = Depends(get_current_patient)):
    citas = db.query(Cita).filter(Cita.paciente_id == patient_id).all()
    return [map_cita(c) for c in citas]

@router.get("/{cita_id}")
def obtener_cita(cita_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return map_cita(cita)

@router.post("/")
def crear_cita(payload: CitaCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cita = Cita(
        paciente_id=payload.paciente_id,
        doctor_id=payload.doctor_id,
        fecha=payload.fecha,
        hora=payload.hora,
        estado=payload.estado or "programada",
        motivo=payload.motivo
    )
    db.add(cita)
    db.commit()
    db.refresh(cita)
    return map_cita(cita)

@router.put("/{cita_id}")
def actualizar_cita(cita_id: int, payload: CitaCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    cita.paciente_id = payload.paciente_id
    cita.doctor_id = payload.doctor_id
    cita.fecha = payload.fecha
    cita.hora = payload.hora
    cita.estado = payload.estado
    cita.motivo = payload.motivo
    
    db.commit()
    db.refresh(cita)
    return map_cita(cita)

@router.patch("/{cita_id}/estado")
def actualizar_cita_estado(cita_id: int, payload: CitaUpdateEstado, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    cita.estado = payload.estado
    db.commit()
    db.refresh(cita)
    return map_cita(cita)

@router.delete("/{cita_id}")
def eliminar_cita(cita_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    db.delete(cita)
    db.commit()
    return {"mensaje": "Cita eliminada"}