from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.doctor import Doctor
from app.schemas.auth import FacialLoginRequest
from app.core.biometria import verificar_similitud_facial
from app.core.security import create_access_token

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/facial-login")
def facial_login(payload: FacialLoginRequest, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.correo == payload.correo).first()

    if not doctor or not doctor.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El médico no está registrado o está inactivo."
        )

    if not doctor.embedding_facial:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El médico no cuenta con un registro biométrico inicial."
        )

    es_valido = verificar_similitud_facial(payload.embedding_facial, str(doctor.embedding_facial))

    if not es_valido:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación facial fallida. Rostro no coincide."
        )

    token_data = {
        "sub": doctor.correo,
        "rol": doctor.rol,
        "doctor_id": doctor.id
    }
    access_token = create_access_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "doctor": {
            "nombres": doctor.nombres,
            "apellidos": doctor.apellidos,
            "especialidad": doctor.especialidad
        }
    }