from fastapi import FastAPI
from app.routers import auth

app = FastAPI(
    title="API Clínica Telemedicina",
    version="1.0.0",
    description="Backend clínico para la plataforma de telemedicina"
)

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Auth"]
)

@app.get("/")
def root():
    return {"message": "API funcionando"}