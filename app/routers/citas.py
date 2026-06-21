from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_citas():
    return {"mensaje": "Listar citas"}

@router.get("/{cita_id}")
def obtener_cita(cita_id: int):
    return {
        "id": cita_id,
        "mensaje": "Obtener cita"
    }

@router.post("/")
def crear_cita():
    return {"mensaje": "Cita creada"}

@router.put("/{cita_id}")
def actualizar_cita(cita_id: int):
    return {
        "id": cita_id,
        "mensaje": "Cita actualizada"
    }

@router.delete("/{cita_id}")
def eliminar_cita(cita_id: int):
    return {
        "id": cita_id,
        "mensaje": "Cita eliminada"
    }