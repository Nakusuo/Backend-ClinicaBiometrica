from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_pacientes():
    return {"mensaje": "Listar pacientes"}

@router.get("/{paciente_id}")
def obtener_paciente(paciente_id: int):
    return {"id": paciente_id}

@router.post("/")
def crear_paciente():
    return {"mensaje": "Paciente creado"}

@router.put("/{paciente_id}")
def actualizar_paciente(paciente_id: int):
    return {"mensaje": "Paciente actualizado"}

@router.delete("/{paciente_id}")
def eliminar_paciente(paciente_id: int):
    return {"mensaje": "Paciente eliminado"}

@router.get("/{paciente_id}/expediente")
def obtener_expediente_paciente(paciente_id: int):
    return {
        "paciente_id": paciente_id,
        "mensaje": "Expediente del paciente"
    }

@router.put("/{paciente_id}/expediente")
def actualizar_expediente_paciente(paciente_id: int):
    return {
        "paciente_id": paciente_id,
        "mensaje": "Expediente actualizado"
    }