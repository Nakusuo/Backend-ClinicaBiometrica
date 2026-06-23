from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_recetas():
    return {"mensaje": "Listar recetas"}

@router.get("/{receta_id}")
def obtener_receta(receta_id: int):
    return {
        "id": receta_id,
        "mensaje": "Obtener receta"
    }

@router.post("/")
def crear_receta():
    return {"mensaje": "Receta creada"}

@router.put("/{receta_id}")
def actualizar_receta(receta_id: int):
    return {
        "id": receta_id,
        "mensaje": "Receta actualizada"
    }

@router.delete("/{receta_id}")
def eliminar_receta(receta_id: int):
    return {
        "id": receta_id,
        "mensaje": "Receta eliminada"
    }