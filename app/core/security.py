import hmac
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.doctor import Doctor
from app.models.paciente import Paciente
from app.core.config import settings

ALGORITHM = settings.algorithm

security_scheme = HTTPBearer(auto_error=False)

def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({
        "exp": expire
    })
    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=ALGORITHM
    )

def obtener_usuario_desde_token(token: str, db: Session):
    """Devuelve el Doctor o Paciente dueño del token, o None si no es válido.

    Se usa tanto en las rutas HTTP como en el WebSocket.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None

    rol = payload.get("rol")
    if rol == "doctor" and payload.get("doctor_id") is not None:
        doctor = db.query(Doctor).filter(Doctor.id == payload["doctor_id"]).first()
        # Un médico desactivado pierde el acceso aunque su token no haya vencido
        if doctor and doctor.activo:
            return doctor
    elif rol == "paciente" and payload.get("patient_id") is not None:
        return db.query(Paciente).filter(Paciente.id == payload["patient_id"]).first()
    return None

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme), db: Session = Depends(get_db)):
    user = obtener_usuario_desde_token(credentials.credentials, db) if credentials else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def es_doctor(user) -> bool:
    return isinstance(user, Doctor)

def es_paciente(user) -> bool:
    return isinstance(user, Paciente)

def rol_de(user) -> str:
    return "doctor" if es_doctor(user) else "paciente"

def prohibido(detalle: str = "No tienes permiso para acceder a este recurso"):
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detalle)

def get_current_doctor(current_user = Depends(get_current_user)):
    if not es_doctor(current_user):
        raise prohibido("Operación permitida únicamente para médicos")
    return current_user

def get_current_patient(current_user = Depends(get_current_user)):
    if not es_paciente(current_user):
        raise prohibido("Operación permitida únicamente para pacientes")
    return current_user

def exigir_doctor_o_mismo_paciente(user, paciente_id: int) -> None:
    """Los médicos ven a cualquier paciente; un paciente solo se ve a sí mismo."""
    if es_doctor(user):
        return
    if es_paciente(user) and user.id == paciente_id:
        return
    raise prohibido()

def exigir_participante_de_cita(user, cita) -> None:
    """Solo el médico y el paciente de la cita pueden verla o modificarla."""
    if es_doctor(user) and cita.doctor_id == user.id:
        return
    if es_paciente(user) and cita.paciente_id == user.id:
        return
    raise prohibido()

def verificar_token_webhook(x_webhook_token: str | None = Header(default=None)) -> None:
    """Los webhooks externos (central telefónica, agenda) deben enviar X-Webhook-Token."""
    esperado = settings.asterisk_webhook_token
    if not esperado:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhooks deshabilitados: falta configurar ASTERISK_WEBHOOK_TOKEN.",
        )
    # compare_digest con str falla si hay caracteres no ASCII; se compara en bytes
    if not x_webhook_token or not hmac.compare_digest(x_webhook_token.encode(), esperado.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de webhook inválido.")
