from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_examenes():
    return {"mensaje": "Listar exámenes"}

@router.get("/{examen_id}")
def obtener_examen(examen_id: int):
    return {
        "id": examen_id,
        "mensaje": "Obtener examen"
    }

@router.post("/")
def crear_examen():
    return {"mensaje": "Examen creado"}

@router.put("/{examen_id}")
def actualizar_examen(examen_id: int):
    return {
        "id": examen_id,
        "mensaje": "Examen actualizado"
    }

@router.delete("/{examen_id}")
def eliminar_examen(examen_id: int):
    return {
        "id": examen_id,
        "mensaje": "Examen eliminado"
    }