from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.cita import Cita
from app.models.paciente import Paciente
from app.models.doctor import Doctor
from app.schemas.cita import CitaCreate, CitaUpdateEstado
from app.core.security import (
    get_current_user,
    get_current_doctor,
    es_doctor,
    es_paciente,
    prohibido,
    exigir_doctor_o_mismo_paciente,
    exigir_participante_de_cita,
)

router = APIRouter()

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
    # Cada usuario ve solo sus propias citas
    if es_doctor(current_user):
        citas = db.query(Cita).filter(Cita.doctor_id == current_user.id).all()
    else:
        citas = db.query(Cita).filter(Cita.paciente_id == current_user.id).all()
    return [map_cita(c) for c in citas]

@router.get("/doctor/{doctor_id}")
def listar_citas_doctor(doctor_id: int, db: Session = Depends(get_db), current_doctor = Depends(get_current_doctor)):
    if current_doctor.id != doctor_id:
        raise prohibido("Solo puedes ver tu propia agenda")
    citas = db.query(Cita).filter(Cita.doctor_id == doctor_id).all()
    return [map_cita(c) for c in citas]

@router.get("/paciente/{patient_id}")
def listar_citas_paciente(patient_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    exigir_doctor_o_mismo_paciente(current_user, patient_id)
    citas = db.query(Cita).filter(Cita.paciente_id == patient_id).all()
    return [map_cita(c) for c in citas]

@router.get("/{cita_id}")
def obtener_cita(cita_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    exigir_participante_de_cita(current_user, cita)
    return map_cita(cita)

@router.post("/")
def crear_cita(payload: CitaCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Un paciente solo agenda citas para sí mismo; un médico solo en su propia agenda
    if es_paciente(current_user) and payload.paciente_id != current_user.id:
        raise prohibido("Solo puedes agendar citas a tu nombre")
    if es_doctor(current_user) and payload.doctor_id != current_user.id:
        raise prohibido("Solo puedes agendar citas en tu propia agenda")
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
    exigir_participante_de_cita(current_user, cita)
    # El médico y el paciente de una cita no se cambian por esta vía
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
    exigir_participante_de_cita(current_user, cita)

    cita.estado = payload.estado
    db.commit()
    db.refresh(cita)
    return map_cita(cita)

@router.delete("/{cita_id}")
def eliminar_cita(cita_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    exigir_participante_de_cita(current_user, cita)
    db.delete(cita)
    db.commit()
    return {"mensaje": "Cita eliminada"}