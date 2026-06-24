from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.paciente import Paciente
from app.models.expediente import Expediente
from app.models.consulta import Consulta
from app.models.receta import Receta
from app.schemas.paciente import PacienteCreate
from app.schemas.expediente import ExpedienteCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def map_paciente(p: Paciente) -> dict:
    if not p:
        return None
    return {
        "id": p.id,
        "dni": p.dni,
        "nombres": p.nombres,
        "apellidos": p.apellidos,
        "nombre": p.nombres,      # Compatibilidad con Angular
        "apellido": p.apellidos,  # Compatibilidad con Angular
        "telefono": p.telefono,
        "correo": p.correo,
        "email": p.correo,        # Compatibilidad con Angular
        "fecha_nacimiento": p.fecha_nacimiento,
        "fechaNacimiento": p.fecha_nacimiento,  # Compatibilidad con Angular
        "direccion": p.direccion,
        "created_at": p.created_at
    }

from app.core.security import get_current_doctor, get_current_user, get_current_patient

@router.get("/")
def listar_pacientes(db: Session = Depends(get_db), current_doctor = Depends(get_current_doctor)):
    pacientes = db.query(Paciente).all()
    return [map_paciente(p) for p in pacientes]

@router.get("/search")
def buscar_pacientes(
    query: str = None,
    nombre: str = None,
    dni: str = None,
    db: Session = Depends(get_db),
    current_doctor = Depends(get_current_doctor)
):
    db_query = db.query(Paciente)
    
    if query:
        search_pattern = f"%{query}%"
        db_query = db_query.filter(
            (Paciente.dni == query) |
            (Paciente.nombres.ilike(search_pattern)) |
            (Paciente.apellidos.ilike(search_pattern))
        )
    else:
        if dni:
            db_query = db_query.filter(Paciente.dni == dni)
        if nombre:
            search_pattern = f"%{nombre}%"
            db_query = db_query.filter(
                (Paciente.nombres.ilike(search_pattern)) |
                (Paciente.apellidos.ilike(search_pattern))
            )
            
    if not query and not dni and not nombre:
        return []
        
    pacientes = db_query.all()
    return [map_paciente(p) for p in pacientes]

@router.get("/{paciente_id}")
def obtener_paciente(paciente_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return map_paciente(paciente)

@router.post("/")
def crear_paciente(payload: PacienteCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = db.query(Paciente).filter(Paciente.dni == payload.dni).first()
    if existing:
        return map_paciente(existing)

    paciente = Paciente(
        dni=payload.dni,
        nombres=payload.nombre,
        apellidos=payload.apellido,
        telefono=payload.telefono,
        correo=payload.email,
        fecha_nacimiento=payload.fechaNacimiento,
        direccion=payload.direccion or ""
    )
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    return map_paciente(paciente)

@router.put("/{paciente_id}")
def actualizar_paciente(paciente_id: int, payload: PacienteCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    paciente.dni = payload.dni
    paciente.nombres = payload.nombre
    paciente.apellidos = payload.apellido
    paciente.telefono = payload.telefono
    paciente.correo = payload.email
    paciente.fecha_nacimiento = payload.fechaNacimiento
    paciente.direccion = payload.direccion or ""
    
    db.commit()
    db.refresh(paciente)
    return map_paciente(paciente)

@router.delete("/{paciente_id}")
def eliminar_paciente(paciente_id: int, db: Session = Depends(get_db), current_doctor = Depends(get_current_doctor)):
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    db.delete(paciente)
    db.commit()
    return {"mensaje": "Paciente eliminado"}

# Adaptación del endpoint de expediente clínico por ID de paciente
@router.get("/{paciente_id}/expediente")
def obtener_expediente_paciente(paciente_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    expediente = db.query(Expediente).filter(Expediente.paciente_id == paciente_id).first()
    if not expediente:
        return {
            "paciente_id": paciente_id,
            "patientId": paciente_id,
            "diagnostico": "Sin diagnóstico previo",
            "tratamiento": "Sin tratamiento registrado",
            "observaciones": "No se encontraron registros clínicos.",
            "notas": "No se encontraron registros clínicos.",
            "fecha": ""
        }
        
    consulta = db.query(Consulta).filter(Consulta.expediente_id == expediente.id).order_by(Consulta.id.desc()).first()
    receta = db.query(Receta).filter(Receta.consulta_id == consulta.id).first() if consulta else None
    
    fecha_str = ""
    if consulta and consulta.fecha_consulta:
        if isinstance(consulta.fecha_consulta, str):
            fecha_str = consulta.fecha_consulta
        else:
            fecha_str = consulta.fecha_consulta.strftime("%Y-%m-%d")
            
    return {
        "id": expediente.id,
        "paciente_id": paciente_id,
        "patientId": paciente_id,
        "doctor_id": consulta.doctor_id if consulta else None,
        "doctorId": consulta.doctor_id if consulta else None,
        "historial": expediente.historial_resumido,
        "diagnostico": consulta.diagnostico_principal if consulta else "Sin diagnóstico previo",
        "tratamiento": receta.nombre_medicamento if receta else "Sin tratamiento registrado",
        "notas": consulta.notas_doctor if consulta else "No se encontraron notas clínicas.",
        "observaciones": consulta.notas_doctor if consulta else "No se encontraron notas clínicas.",
        "fecha": fecha_str
    }

@router.put("/{paciente_id}/expediente")
def actualizar_expediente_paciente(paciente_id: int, payload: ExpedienteCreate, db: Session = Depends(get_db), current_doctor = Depends(get_current_doctor)):
    p_id = payload.patientId or paciente_id
    d_id = payload.doctorId or payload.doctor_id
    
    expediente = db.query(Expediente).filter(Expediente.paciente_id == p_id).first()
    if not expediente:
        expediente = Expediente(
            paciente_id=p_id,
            alergias_conocidas="Ninguna",
            padecimientos_cronicos="Ninguno",
            grupo_sanguineo="O",
            factor_rh="+"
        )
        db.add(expediente)
        db.flush()

    # Registrar nueva consulta
    consulta = Consulta(
        expediente_id=expediente.id,
        doctor_id=d_id,
        motivo_consulta="Consulta de Telemedicina",
        sintomas="Consulta general",
        diagnostico_principal=payload.diagnostico,
        notas_doctor=payload.observaciones or payload.notas,
        tipo_consulta="General",
        estado="completada"
    )
    db.add(consulta)
    db.flush()

    # Registrar nueva receta
    receta = Receta(
        consulta_id=consulta.id,
        paciente_id=p_id,
        doctor_id=d_id,
        nombre_medicamento=payload.tratamiento,
        concentracion="según receta",
        presentacion="tabletas",
        dosis="según indicación",
        frecuencia="cada 8 horas",
        duracion_tratamiento="7 días"
    )
    db.add(receta)
    db.commit()
    
    return {"mensaje": "Expediente actualizado exitosamente"}