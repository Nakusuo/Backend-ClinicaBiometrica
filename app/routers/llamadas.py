from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.models.cita import Cita
from app.models.llamada import Llamada
from app.core.tiempo import ahora_utc
from app.core.security import (
    get_current_user,
    get_current_doctor,
    get_current_patient,
    es_doctor,
    prohibido,
    exigir_participante_de_cita,
)
from app.core.ws_manager import manager

router = APIRouter()

class SolicitarLlamadaRequest(BaseModel):
    paciente_id: int
    cita_id: int

@router.post("/solicitar")
async def solicitar_llamada(payload: SolicitarLlamadaRequest, db: Session = Depends(get_db), current_patient = Depends(get_current_patient)):
    if payload.paciente_id != current_patient.id:
        raise prohibido("Solo puedes solicitar llamadas a tu nombre")

    cita = db.query(Cita).filter(Cita.id == payload.cita_id).first()
    paciente = current_patient

    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    exigir_participante_de_cita(current_patient, cita)

    cita.estado = "en_curso"
    db.commit()

    # Registrar el inicio de la llamada en la base de datos (Auditoría WebRTC)
    llamada = db.query(Llamada).filter(Llamada.cita_id == payload.cita_id).first()
    if not llamada:
        llamada = Llamada(
            cita_id=payload.cita_id,
            paciente_id=payload.paciente_id,
            doctor_id=cita.doctor_id,
            room_id=f"room_{payload.cita_id}",
            estado="esperando",
            start_time=ahora_utc()
        )
        db.add(llamada)
        db.commit()

    # Notificar al doctor en tiempo real vía WebSocket
    doctor_id_str = str(cita.doctor_id)
    await manager.send_personal_message(
        role="doctor",
        user_id=doctor_id_str,
        message={
            "type": "call-request",
            "sender_role": "paciente",
            "sender_id": str(payload.paciente_id),
            "data": {
                "appointmentId": payload.cita_id,
                "patientName": f"{paciente.nombres} {paciente.apellidos}",
                "patientId": payload.paciente_id,
                "reason": cita.motivo or "Consulta de Telemedicina"
            }
        }
    )

    return {
        "status": "solicitada",
        "cita_id": payload.cita_id,
        "doctor_id": cita.doctor_id,
        "mensaje": "Llamada solicitada al médico"
    }

@router.post("/{cita_id}/aceptar")
async def aceptar_llamada(cita_id: int, db: Session = Depends(get_db), current_doctor = Depends(get_current_doctor)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    exigir_participante_de_cita(current_doctor, cita)

    cita.estado = "en_curso"
    db.commit()

    # Actualizar estado de auditoría de la llamada
    llamada = db.query(Llamada).filter(Llamada.cita_id == cita_id).first()
    if llamada:
        llamada.estado = "activa"
        llamada.start_time = ahora_utc() # Marcar el inicio real al aceptar
        db.commit()

    # Notificar al paciente que el doctor aceptó
    await manager.send_personal_message(
        role="paciente",
        user_id=str(cita.paciente_id),
        message={
            "type": "call-accepted",
            "sender_role": "doctor",
            "sender_id": str(cita.doctor_id),
            "data": {
                "appointmentId": cita_id
            }
        }
    )

    return {
        "status": "en_curso",
        "cita_id": cita_id,
        "mensaje": "Llamada aceptada"
    }

@router.post("/{cita_id}/terminar")
async def terminar_llamada(cita_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    exigir_participante_de_cita(current_user, cita)

    cita.estado = "finalizada"
    db.commit()

    # Calcular duración y finalizar auditoría
    llamada = db.query(Llamada).filter(Llamada.cita_id == cita_id).first()
    if llamada:
        llamada.estado = "terminada"
        llamada.end_time = ahora_utc()
        if llamada.start_time:
            duracion_segundos = int((llamada.end_time - llamada.start_time).total_seconds())
            llamada.duracion = duracion_segundos
        db.commit()

    # Notificar desconexión
    await manager.send_personal_message(
        role="paciente",
        user_id=str(cita.paciente_id),
        message={
            "type": "call-ended",
            "sender_role": "doctor",
            "sender_id": str(cita.doctor_id),
            "data": {
                "appointmentId": cita_id
            }
        }
    )

    await manager.send_personal_message(
        role="doctor",
        user_id=str(cita.doctor_id),
        message={
            "type": "call-ended",
            "sender_role": "paciente",
            "sender_id": str(cita.paciente_id),
            "data": {
                "appointmentId": cita_id
            }
        }
    )

    return {
        "status": "finalizada",
        "cita_id": cita_id,
        "mensaje": "Llamada terminada"
    }

@router.get("/")
def listar_llamadas(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Llamada)
    if es_doctor(current_user):
        query = query.filter(Llamada.doctor_id == current_user.id)
    else:
        query = query.filter(Llamada.paciente_id == current_user.id)
    llamadas = query.order_by(Llamada.id.desc()).all()
    results = []
    for l in llamadas:
        fecha_str = ""
        hora_str = ""
        if l.start_time:
            fecha_str = l.start_time.strftime("%Y-%m-%d")
            hora_str = l.start_time.strftime("%H:%M:%S")
        elif l.created_at:
            fecha_str = l.created_at.strftime("%Y-%m-%d")
            hora_str = l.created_at.strftime("%H:%M:%S")

        paciente_info = None
        if l.paciente:
            paciente_info = f"{l.paciente.nombres} {l.paciente.apellidos}"

        results.append({
            "id": l.id,
            "fecha": fecha_str,
            "hora": hora_str,
            "duracion": l.duracion or 0,
            "paciente": paciente_info,
            "paciente_id": l.paciente_id,
            "doctor_id": l.doctor_id,
            "room_id": l.room_id,
            "estado": l.estado
        })
    return results

