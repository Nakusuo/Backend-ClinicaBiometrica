from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.doctor import Doctor
from app.models.paciente import Paciente
from app.schemas.auth import FacialLoginRequest, DoctorRegisterRequest, PatientRegisterRequest
from app.core.biometria import verificar_similitud_facial
from app.core.security import create_access_token
import bcrypt
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

@router.post("/register-doctor")
def register_doctor(payload: DoctorRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Doctor).filter(Doctor.correo == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya se encuentra registrado.")

    nombres_part = payload.nombre.split(" ", 1)
    nombres = nombres_part[0]
    apellidos = nombres_part[1] if len(nombres_part) > 1 else ""

    doctor = Doctor(
        nombres=nombres,
        apellidos=apellidos,
        correo=payload.email,
        especialidad=payload.especialidad,
        cedula=payload.cedula,
        telefono=payload.telefono,
        password_hash=hash_password(payload.password),
        embedding_facial=json.dumps(payload.faceEmbedding),
        rol="doctor",
        activo=True
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return {"mensaje": "Doctor registrado exitosamente", "id": doctor.id}

@router.post("/register-patient")
def register_patient(payload: PatientRegisterRequest, db: Session = Depends(get_db)):
    existing_dni = db.query(Paciente).filter(Paciente.dni == payload.dni).first()
    if existing_dni:
        raise HTTPException(status_code=400, detail="El DNI ya se encuentra registrado.")

    existing_email = db.query(Paciente).filter(Paciente.correo == payload.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="El correo ya se encuentra registrado.")

    embedding_str = json.dumps(payload.faceEmbedding) if payload.faceEmbedding else None

    paciente = Paciente(
        dni=payload.dni,
        nombres=payload.nombre,
        apellidos=payload.apellido,
        telefono=payload.telefono,
        correo=payload.email,
        fecha_nacimiento=payload.fechaNacimiento,
        direccion="",
        password_hash=hash_password(payload.password),
        embedding_facial=embedding_str
    )
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    return {"mensaje": "Paciente registrado exitosamente", "id": paciente.id}

@router.post("/facial-login")
def facial_login(payload: FacialLoginRequest, db: Session = Depends(get_db)):
    # 1. Buscar en Doctores primero
    doctor = db.query(Doctor).filter(Doctor.correo == payload.correo).first()
    
    if doctor:
        if not doctor.activo:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="El médico está inactivo.")
        if not doctor.embedding_facial:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El médico no cuenta con registro biométrico.")

        es_valido = verificar_similitud_facial(payload.embedding_facial, doctor.embedding_facial)
        if not es_valido:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticación biométrica fallida.")

        token_data = {"sub": doctor.correo, "rol": "doctor", "doctor_id": doctor.id}
        token = create_access_token(data=token_data)

        return {
            "access_token": token,
            "token_type": "bearer",
            "doctor": {
                "id": doctor.id,
                "nombre": doctor.nombres,
                "apellido": doctor.apellidos,
                "nombres": doctor.nombres,
                "apellidos": doctor.apellidos,
                "especialidad": doctor.especialidad,
                "email": doctor.correo,
                "correo": doctor.correo,
                "telefono": doctor.telefono
            }
        }

    # 2. Si no es doctor, buscar en Pacientes
    paciente = db.query(Paciente).filter(Paciente.correo == payload.correo).first()
    if paciente:
        if not paciente.embedding_facial:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El paciente no cuenta con registro biométrico.")

        es_valido = verificar_similitud_facial(payload.embedding_facial, paciente.embedding_facial)
        if not es_valido:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticación biométrica fallida.")

        token_data = {"sub": paciente.correo, "rol": "paciente", "patient_id": paciente.id}
        token = create_access_token(data=token_data)

        return {
            "access_token": token,
            "token_type": "bearer",
            "patient": {
                "id": paciente.id,
                "nombre": paciente.nombres,
                "apellido": paciente.apellidos,
                "nombres": paciente.nombres,
                "apellidos": paciente.apellidos,
                "dni": paciente.dni,
                "email": paciente.correo,
                "correo": paciente.correo,
                "telefono": paciente.telefono,
                "fechaNacimiento": paciente.fecha_nacimiento,
                "fecha_nacimiento": paciente.fecha_nacimiento,
                "direccion": paciente.direccion
            }
        }

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no registrado en el sistema.")