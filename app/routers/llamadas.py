from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_llamadas():
    return {"mensaje": "Listar llamadas"}

@router.get("/{llamada_id}")
def obtener_llamada(llamada_id: int):
    return {
        "id": llamada_id,
        "mensaje": "Obtener llamada"
    }

@router.post("/")
def crear_llamada():
    return {"mensaje": "Llamada creada"}

@router.put("/{llamada_id}")
def actualizar_llamada(llamada_id: int):
    return {
        "id": llamada_id,
        "mensaje": "Llamada actualizada"
    }

@router.delete("/{llamada_id}")
def eliminar_llamada(llamada_id: int):
    return {
        "id": llamada_id,
        "mensaje": "Llamada eliminada"
    }