from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_consultas():
    return {"mensaje": "Listar consultas"}

@router.get("/{consulta_id}")
def obtener_consulta(consulta_id: int):
    return {
        "id": consulta_id,
        "mensaje": "Obtener consulta"
    }

@router.post("/")
def crear_consulta():
    return {"mensaje": "Consulta creada"}

@router.put("/{consulta_id}")
def actualizar_consulta(consulta_id: int):
    return {
        "id": consulta_id,
        "mensaje": "Consulta actualizada"
    }

@router.delete("/{consulta_id}")
def eliminar_consulta(consulta_id: int):
    return {
        "id": consulta_id,
        "mensaje": "Consulta eliminada"
    }