from fastapi import APIRouter

router = APIRouter()

@router.post("/citas")
def webhook_citas():
    return {
        "mensaje": "Webhook de citas recibido"
    }