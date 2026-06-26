from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import json

from app.db.database import Base, engine, SessionLocal
from app.db.seeder import seed_db
from app.core.config import settings
from app.routers import (
    auth,
    pacientes,
    doctores,
    citas,
    expedientes,
    webhooks,
    llamadas
)

# Importamos todos los modelos para que Base.metadata los reconozca al crear las tablas
from app.models.doctor import Doctor
from app.models.paciente import Paciente
from app.models.cita import Cita
from app.models.expediente import Expediente
from app.models.consulta import Consulta
from app.models.receta import Receta
from app.models.examen import Examen
from app.models.llamada import Llamada

app = FastAPI(
    title="API Clínica Telemedicina",
    version="1.0.0",
    description="Backend clínico para la plataforma de telemedicina"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Evento de inicio del servidor para crear tablas y poblar datos iniciales
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()

# Orquestador/Manager de conexiones WebSocket para señalización WebRTC
class ConnectionManager:
    def __init__(self):
        # Almacena las conexiones en formato "role:user_id" -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, role: str, user_id: str):
        await websocket.accept()
        key = f"{role}:{user_id}"
        self.active_connections[key] = websocket
        print(f"WS Conectado: {key}. Conexiones activas: {len(self.active_connections)}")

    def disconnect(self, role: str, user_id: str):
        key = f"{role}:{user_id}"
        if key in self.active_connections:
            del self.active_connections[key]
            print(f"WS Desconectado: {key}. Conexiones activas: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, role: str, user_id: str):
        key = f"{role}:{user_id}"
        websocket = self.active_connections.get(key)
        if websocket:
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error al enviar mensaje a {key}: {e}")
                self.disconnect(role, user_id)

manager = ConnectionManager()

@app.websocket("/ws/{role}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, role: str, user_id: str):
    await manager.connect(websocket, role, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            print(f"WS Recibido de {role}:{user_id} - Tipo: {data.get('type')}")
            
            target_role = data.get("target_role")
            target_id = data.get("target_id")
            
            if target_role and target_id:
                # Reenviar el mensaje de señalización al cliente destino
                forward_msg = {
                    "sender_role": role,
                    "sender_id": user_id,
                    "type": data.get("type"),
                    "data": data.get("data")
                }
                await manager.send_personal_message(forward_msg, target_role, str(target_id))
    except WebSocketDisconnect:
        manager.disconnect(role, user_id)
    except Exception as e:
        print(f"Error en WebSocket para {role}:{user_id}: {e}")
        manager.disconnect(role, user_id)

# Inclusión de Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(pacientes.router, prefix="/api/pacientes", tags=["Pacientes"])
app.include_router(doctores.router, prefix="/api/doctores", tags=["Doctores"])
app.include_router(citas.router, prefix="/api/citas", tags=["Citas"])
app.include_router(expedientes.router, prefix="/api/expedientes", tags=["Expedientes"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(llamadas.router, prefix="/api/llamadas", tags=["Llamadas"])

@app.get("/")
def root():
    return {"message": "API funcionando"}
