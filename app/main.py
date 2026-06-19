from fastapi import FastAPI
from app.routers import (
    auth,
    pacientes,
    doctores,
    citas,
    expedientes,
    webhooks
)

app = FastAPI(
    title="API Clínica Telemedicina",
    version="1.0.0",
    description="Backend clínico para la plataforma de telemedicina"
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])

app.include_router(pacientes.router, prefix="/api/pacientes", tags=["Pacientes"])

app.include_router(doctores.router, prefix="/api/doctores", tags=["Doctores"])

app.include_router(citas.router, prefix="/api/citas", tags=["Citas"])

app.include_router(expedientes.router, prefix="/api/expedientes", tags=["Expedientes"])

app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])

@app.get("/")
def root():
    return {"message": "API funcionando"}