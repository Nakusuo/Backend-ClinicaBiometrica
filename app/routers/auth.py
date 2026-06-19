from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
def login():
    return {
        "access_token": "token_prueba",
        "token_type": "bearer"
    }