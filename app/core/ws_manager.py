from typing import Dict
from fastapi import WebSocket


# Orquestador/Manager de conexiones WebSocket para señalización WebRTC.
# Vive en su propio módulo para que los routers no tengan que importar app.main.
class ConnectionManager:
    def __init__(self):
        # Almacena las conexiones en formato "role:user_id" -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

    def register(self, websocket: WebSocket, role: str, user_id: str):
        """Guarda un socket ya aceptado y autenticado."""
        key = f"{role}:{user_id}"
        self.active_connections[key] = websocket
        print(f"WS Conectado: {key}. Conexiones activas: {len(self.active_connections)}")

    def disconnect(self, role: str, user_id: str, websocket: WebSocket | None = None):
        key = f"{role}:{user_id}"
        # Si el usuario abrió otra pestaña, no borrar la conexión nueva al cerrar la vieja
        if websocket is not None and self.active_connections.get(key) is not websocket:
            return
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
