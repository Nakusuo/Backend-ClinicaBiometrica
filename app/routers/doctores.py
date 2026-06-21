from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_doctores():
    return {"mensaje": "Listar doctores"}

@router.get("/{doctor_id}")
def obtener_doctor(doctor_id: int):
    return {
        "id": doctor_id,
        "mensaje": "Obtener doctor"
    }

@router.post("/")
def crear_doctor():
    return {"mensaje": "Doctor creado"}

@router.put("/{doctor_id}")
def actualizar_doctor(doctor_id: int):
    return {
        "id": doctor_id,
        "mensaje": "Doctor actualizado"
    }

@router.delete("/{doctor_id}")
def eliminar_doctor(doctor_id: int):
    return {
        "id": doctor_id,
        "mensaje": "Doctor eliminado"
    }