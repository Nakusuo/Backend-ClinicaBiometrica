from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.doctor import Doctor
from app.models.paciente import Paciente

SECRET_KEY = "telemedicina2026"
ALGORITHM = "HS256"

security_scheme = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({
        "exp": expire
    })
    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        rol: str = payload.get("rol")
        if email is None or rol is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if rol == "doctor":
        user = db.query(Doctor).filter(Doctor.correo == email).first()
    elif rol == "paciente":
        user = db.query(Paciente).filter(Paciente.correo == email).first()
    else:
        raise credentials_exception

    if user is None:
        raise credentials_exception
    return user

def get_current_doctor(current_user = Depends(get_current_user)):
    rol = getattr(current_user, "rol", None)
    if rol != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación permitida únicamente para médicos"
        )
    return current_user

def get_current_patient(current_user = Depends(get_current_user)):
    rol = getattr(current_user, "rol", None)
    if rol == "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación permitida únicamente para pacientes"
        )
    return current_user