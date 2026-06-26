from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import SessionLocal
from app.models.cita import Cita
from app.models.paciente import Paciente
from app.models.doctor import Doctor
from app.models.llamada import Llamada
from datetime import datetime
from app.core.security import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SolicitarLlamadaRequest(BaseModel):
    paciente_id: int
    cita_id: int

@router.post("/solicitar")
async def solicitar_llamada(payload: SolicitarLlamadaRequest, db: Session = Depends(get_db)):
    cita = db.query(Cita).filter(Cita.id == payload.cita_id).first()
    paciente = db.query(Paciente).filter(Paciente.id == payload.paciente_id).first()

    if not cita or not paciente:
        raise HTTPException(status_code=404, detail="Cita o Paciente no encontrado")

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
            start_time=datetime.utcnow()
        )
        db.add(llamada)
        db.commit()

    # Notificar al doctor en tiempo real vía WebSocket
    from app.main import manager
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
async def aceptar_llamada(cita_id: int, db: Session = Depends(get_db)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    cita.estado = "en_curso"
    db.commit()

    # Actualizar estado de auditoría de la llamada
    llamada = db.query(Llamada).filter(Llamada.cita_id == cita_id).first()
    if llamada:
        llamada.estado = "activa"
        llamada.start_time = datetime.utcnow() # Marcar el inicio real al aceptar
        db.commit()

    # Notificar al paciente que el doctor aceptó
    from app.main import manager
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
async def terminar_llamada(cita_id: int, db: Session = Depends(get_db)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    cita.estado = "finalizada"
    db.commit()

    # Calcular duración y finalizar auditoría
    llamada = db.query(Llamada).filter(Llamada.cita_id == cita_id).first()
    if llamada:
        llamada.estado = "terminada"
        llamada.end_time = datetime.utcnow()
        if llamada.start_time:
            duracion_segundos = int((llamada.end_time - llamada.start_time).total_seconds())
            llamada.duracion = duracion_segundos
        db.commit()

    # Notificar desconexión
    from app.main import manager
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
    llamadas = db.query(Llamada).order_by(Llamada.id.desc()).all()
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

