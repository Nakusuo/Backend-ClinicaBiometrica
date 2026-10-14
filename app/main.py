import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status

from app.db.database import SessionLocal
from app.db.seeder import seed_db
from app.db.migrar import migrar
from app.core.config import settings
from app.core.security import obtener_usuario_desde_token, rol_de
from app.core.ws_manager import manager
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    auth,
    pacientes,
    doctores,
    citas,
    expedientes,
    webhooks,
    llamadas,
    freepbx
)

# Registra todos los modelos en Base.metadata
import app.models  # noqa: F401

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("telemedicina")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.auto_migrate:
        migrar()
    if settings.seed_demo_data:
        db = SessionLocal()
        try:
            seed_db(db)
        finally:
            db.close()
    yield


app = FastAPI(
    title="API Clínica Telemedicina",
    version="1.0.0",
    description="Backend clínico para la plataforma de telemedicina",
    lifespan=lifespan,
)

# Configuración de CORS. La sesión viaja en el header Authorization, no en cookies,
# así que no hace falta allow_credentials (y no se puede combinar con "*").
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Segundos que tiene el cliente para enviar {"type": "auth", "token": "<JWT>"} tras conectarse
WS_AUTH_TIMEOUT = 10

# El cliente se conecta a /ws/{role}/{user_id} y su primer mensaje debe ser
# {"type": "auth", "token": "<JWT>"}. El token no va en la URL para que no quede en los logs
# de acceso de uvicorn/Nginx. El rol y el id deben coincidir con el dueño del token.
@app.websocket("/ws/{role}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, role: str, user_id: str):
    await websocket.accept()
    try:
        auth = await asyncio.wait_for(websocket.receive_json(), timeout=WS_AUTH_TIMEOUT)
    except (asyncio.TimeoutError, WebSocketDisconnect, ValueError):
        auth = None

    token = auth.get("token") if isinstance(auth, dict) and auth.get("type") == "auth" else None
    user = None
    if isinstance(token, str):
        db = SessionLocal()
        try:
            user = obtener_usuario_desde_token(token, db)
        finally:
            db.close()

    if user is None or rol_de(user) != role or str(user.id) != user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    manager.register(websocket, role, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            logger.debug("WS recibido de %s:%s - tipo %s", role, user_id, data.get("type"))

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
        manager.disconnect(role, user_id, websocket)
    except Exception as e:
        logger.warning("Error en WebSocket para %s:%s: %s", role, user_id, e)
        manager.disconnect(role, user_id, websocket)

# Inclusión de Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(pacientes.router, prefix="/api/pacientes", tags=["Pacientes"])
app.include_router(doctores.router, prefix="/api/doctores", tags=["Doctores"])
app.include_router(citas.router, prefix="/api/citas", tags=["Citas"])
app.include_router(expedientes.router, prefix="/api/expedientes", tags=["Expedientes"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(llamadas.router, prefix="/api/llamadas", tags=["Llamadas"])
app.include_router(freepbx.router, prefix="/api/freepbx", tags=["FreePBX"])

@app.get("/")
def root():
    return {"message": "API funcionando"}
