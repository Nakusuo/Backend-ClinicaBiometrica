from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.database import SessionLocal
from app.models.cita import Cita
from app.models.llamada import Llamada
from app.models.paciente import Paciente
from app.models.doctor import Doctor
from datetime import datetime
from app.core.config import settings

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class WebhookCitaPayload(BaseModel):
    cita_id: Optional[int] = None
    paciente_dni: str
    doctor_cedula: str
    fecha: str
    hora: str
    motivo: str
    estado: Optional[str] = "programada"

class AsteriskEventPayload(BaseModel):
    event: str  # ringing, answered, hangup
    caller_id: str  # DNI or phone of the patient
    exten: str  # extension/id of the doctor
    room_id: Optional[str] = None
    duration: Optional[int] = 0

@router.post("/citas")
def webhook_citas(payload: WebhookCitaPayload, db: Session = Depends(get_db)):
    # Find patient
    paciente = db.query(Paciente).filter(Paciente.dni == payload.paciente_dni).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado con el DNI proveído.")

    # Find doctor
    doctor = db.query(Doctor).filter(Doctor.cedula == payload.doctor_cedula).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado con la cédula proveída.")

    # Check if appointment exists
    cita = None
    if payload.cita_id:
        cita = db.query(Cita).filter(Cita.id == payload.cita_id).first()
    
    if cita:
        cita.fecha = payload.fecha
        cita.hora = payload.hora
        cita.motivo = payload.motivo
        cita.estado = payload.estado
    else:
        cita = Cita(
            paciente_id=paciente.id,
            doctor_id=doctor.id,
            fecha=payload.fecha,
            hora=payload.hora,
            motivo=payload.motivo,
            estado=payload.estado
        )
        db.add(cita)
    
    db.commit()
    db.refresh(cita)
    return {
        "status": "procesado",
        "mensaje": "Webhook de cita procesado exitosamente",
        "cita_id": cita.id
    }

@router.post("/asterisk-event")
async def webhook_asterisk_event(
    payload: AsteriskEventPayload,
    db: Session = Depends(get_db),
    x_webhook_token: Optional[str] = Header(default=None),
):
    if settings.asterisk_webhook_token and x_webhook_token != settings.asterisk_webhook_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de webhook inválido.")

    # 1. Search for patient by phone or DNI
    paciente = db.query(Paciente).filter(
        (Paciente.dni == payload.caller_id) | 
        (Paciente.telefono == payload.caller_id)
    ).first()
    
    # 2. Search for doctor by phone or cedula
    doctor = db.query(Doctor).filter(
        (Doctor.cedula == payload.exten) | 
        (Doctor.telefono == payload.exten)
    ).first()

    # Find active or last call
    llamada = None
    if paciente and doctor:
        llamada = db.query(Llamada).filter(
            Llamada.paciente_id == paciente.id,
            Llamada.doctor_id == doctor.id
        ).order_by(Llamada.id.desc()).first()

    status_mapping = {
        "ringing": "esperando",
        "answered": "activa",
        "hangup": "terminada"
    }

    current_status = status_mapping.get(payload.event.lower(), "esperando")

    if llamada:
        llamada.estado = current_status
        if payload.event == "answered":
            llamada.start_time = datetime.utcnow()
        elif payload.event == "hangup":
            llamada.end_time = datetime.utcnow()
            if payload.duration:
                llamada.duracion = payload.duration
            elif llamada.start_time:
                llamada.duracion = int((llamada.end_time - llamada.start_time).total_seconds())
        db.commit()
        db.refresh(llamada)

    # 3. Notify doctor via WebSocket
    from app.main import manager
    if doctor:
        doctor_id_str = str(doctor.id)
        await manager.send_personal_message(
            role="doctor",
            user_id=doctor_id_str,
            message={
                "type": f"asterisk-{payload.event}",
                "sender_role": "asterisk",
                "sender_id": "freepbx",
                "data": {
                    "event": payload.event,
                    "patientName": f"{paciente.nombres} {paciente.apellidos}" if paciente else "Desconocido",
                    "caller_id": payload.caller_id,
                    "exten": payload.exten,
                    "room_id": payload.room_id or (llamada.room_id if llamada else None),
                    "duration": payload.duration
                }
            }
        )

    return {
        "status": "procesado",
        "evento": payload.event,
        "llamada_id": llamada.id if llamada else None
    }
