from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.expediente import Expediente
from app.models.consulta import Consulta
from app.models.receta import Receta
from app.schemas.expediente import ExpedienteCreate
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def map_expediente_from_consulta(e: Expediente, c: Consulta, r: Receta) -> dict:
    fecha_str = ""
    if c and c.fecha_consulta:
        if isinstance(c.fecha_consulta, str):
            fecha_str = c.fecha_consulta
        else:
            fecha_str = c.fecha_consulta.strftime("%Y-%m-%d")
            
    return {
        "id": c.id if c else e.id,
        "paciente_id": e.paciente_id,
        "patientId": e.paciente_id,
        "doctor_id": c.doctor_id if c else None,
        "doctorId": c.doctor_id if c else None,
        "historial": e.historial_resumido,
        "diagnostico": c.diagnostico_principal if c else "Sin diagnóstico previo",
        "tratamiento": r.nombre_medicamento if r else "Sin tratamiento registrado",
        "notas": c.notas_doctor if c else "No se encontraron notas.",
        "observaciones": c.notas_doctor if c else "No se encontraron notas.",
        "fecha": fecha_str,
        "updated_at": c.updated_at if c else e.updated_at
    }

@router.get("/")
def listar_expedientes(db: Session = Depends(get_db)):
    expedientes = db.query(Expediente).all()
    results = []
    for e in expedientes:
        consulta = db.query(Consulta).filter(Consulta.expediente_id == e.id).order_by(Consulta.id.desc()).first()
        receta = db.query(Receta).filter(Receta.consulta_id == consulta.id).first() if consulta else None
        results.append(map_expediente_from_consulta(e, consulta, receta))
    return results

@router.get("/paciente/{paciente_id}")
def obtener_expedientes_paciente(paciente_id: int, db: Session = Depends(get_db)):
    expediente = db.query(Expediente).filter(Expediente.paciente_id == paciente_id).first()
    if not expediente:
        return []
    
    consultas = db.query(Consulta).filter(Consulta.expediente_id == expediente.id).order_by(Consulta.id.desc()).all()
    results = []
    for c in consultas:
        receta = db.query(Receta).filter(Receta.consulta_id == c.id).first()
        results.append(map_expediente_from_consulta(expediente, c, receta))
        
    return results

@router.get("/{expediente_id}")
def obtener_expediente(expediente_id: int, db: Session = Depends(get_db)):
    # En la nueva bd, el id recibido puede representar el id de la consulta
    consulta = db.query(Consulta).filter(Consulta.id == expediente_id).first()
    if consulta:
        expediente = db.query(Expediente).filter(Expediente.id == consulta.expediente_id).first()
        receta = db.query(Receta).filter(Receta.consulta_id == consulta.id).first()
        return map_expediente_from_consulta(expediente, consulta, receta)
        
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    
    consulta = db.query(Consulta).filter(Consulta.expediente_id == expediente.id).order_by(Consulta.id.desc()).first()
    receta = db.query(Receta).filter(Receta.consulta_id == consulta.id).first() if consulta else None
    return map_expediente_from_consulta(expediente, consulta, receta)

@router.post("/")
def crear_expediente(payload: ExpedienteCreate, db: Session = Depends(get_db)):
    p_id = payload.patientId or payload.paciente_id
    d_id = payload.doctorId or payload.doctor_id
    
    # 1. Obtener o crear expediente principal
    expediente = db.query(Expediente).filter(Expediente.paciente_id == p_id).first()
    if not expediente:
        expediente = Expediente(
            paciente_id=p_id,
            alergias_conocidas="Ninguna",
            padecimientos_cronicos="Ninguno",
            grupo_sanguineo="O",
            factor_rh="+",
            historial_resumido=payload.historial or "Expediente abierto."
        )
        db.add(expediente)
        db.flush()
        
    # 2. Registrar la consulta clínica
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
    
    # 3. Registrar receta médica
    receta = Receta(
        consulta_id=consulta.id,
        paciente_id=p_id,
        doctor_id=d_id,
        nombre_medicamento=payload.tratamiento,
        concentracion="según receta",
        presentacion="tabletas",
        dosis="según indicación",
        frecuencia="cada 8 horas",
        duracion_tratamiento="7 días",
        indicaciones_especiales="Tomar con agua."
    )
    db.add(receta)
    db.commit()
    db.refresh(consulta)
    db.refresh(receta)
    
    return map_expediente_from_consulta(expediente, consulta, receta)

@router.put("/{expediente_id}")
def actualizar_expediente(expediente_id: int, payload: ExpedienteCreate, db: Session = Depends(get_db)):
    # Buscamos si el id corresponde a la consulta (que representa el registro clínico en el front)
    consulta = db.query(Consulta).filter(Consulta.id == expediente_id).first()
    if consulta:
        consulta.diagnostico_principal = payload.diagnostico
        consulta.notas_doctor = payload.observaciones or payload.notas
        
        receta = db.query(Receta).filter(Receta.consulta_id == consulta.id).first()
        if receta:
            receta.nombre_medicamento = payload.tratamiento
        else:
            p_id = payload.patientId or payload.paciente_id
            d_id = payload.doctorId or payload.doctor_id
            receta = Receta(
                consulta_id=consulta.id,
                paciente_id=p_id,
                doctor_id=d_id,
                nombre_medicamento=payload.tratamiento
            )
            db.add(receta)
            
        db.commit()
        expediente = db.query(Expediente).filter(Expediente.id == consulta.expediente_id).first()
        return map_expediente_from_consulta(expediente, consulta, receta)
        
    raise HTTPException(status_code=404, detail="Registro clínico no encontrado")

@router.delete("/{expediente_id}")
def eliminar_expediente(expediente_id: int, db: Session = Depends(get_db)):
    consulta = db.query(Consulta).filter(Consulta.id == expediente_id).first()
    if consulta:
        db.delete(consulta)
        db.commit()
        return {"mensaje": "Registro clínico eliminado"}
        
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    db.delete(expediente)
    db.commit()
    return {"mensaje": "Expediente eliminado"}