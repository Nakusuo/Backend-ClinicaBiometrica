from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_expedientes():
    return {"mensaje": "Listar expedientes"}

@router.get("/{expediente_id}")
def obtener_expediente(expediente_id: int):
    return {
        "id": expediente_id,
        "mensaje": "Obtener expediente"
    }

@router.post("/")
def crear_expediente():
    return {"mensaje": "Expediente creado"}

@router.put("/{expediente_id}")
def actualizar_expediente(expediente_id: int):
    return {
        "id": expediente_id,
        "mensaje": "Expediente actualizado"
    }

@router.delete("/{expediente_id}")
def eliminar_expediente(expediente_id: int):
    return {
        "id": expediente_id,
        "mensaje": "Expediente eliminado"
    }