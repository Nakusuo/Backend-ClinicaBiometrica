# Despliegue en Ubuntu Server

Esta arquitectura funciona bien para el proyecto:

```text
Frontend <-> Backend FastAPI <-> PostgreSQL
FreePBX/Asterisk -> Backend FastAPI
FreePBX/Asterisk <-> MariaDB interna de FreePBX
```

El frontend no deberia conectarse directo a PostgreSQL, MariaDB ni FreePBX.

## 1. Preparar el servidor

Instala Docker y el plugin de Compose:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
```

## 2. Configurar variables

Copia `.env.example` a `.env` y cambia al menos:

```env
POSTGRES_PASSWORD=una-clave-fuerte
SECRET_KEY=otra-clave-larga-y-secreta
CORS_ORIGINS=https://tu-frontend.com,http://IP_DEL_SERVIDOR
```

Si el frontend esta servido desde el mismo dominio con Nginx, usa ese dominio en `CORS_ORIGINS`.

## 3. Levantar backend y PostgreSQL

Desde la raiz del backend:

```bash
docker compose up -d --build
docker compose logs -f web
```

La API queda en:

```text
http://IP_DEL_SERVIDOR:8000/docs
```

PostgreSQL queda publicado solo en `127.0.0.1:5432`, no hacia internet.

## 4. Frontend

Configura el frontend para consumir:

```text
http://IP_DEL_SERVIDOR:8000
ws://IP_DEL_SERVIDOR:8000/ws/{role}/{user_id}
```

Si usas HTTPS con dominio, cambia a:

```text
https://tu-dominio.com
wss://tu-dominio.com/ws/{role}/{user_id}
```

## 5. Nginx

Puedes usar `deploy/nginx-api.conf.example` como base para publicar la API con dominio y mantener WebSocket funcionando.

Despues de copiarlo a `/etc/nginx/sites-available/`, cambia `tu-dominio.com` por tu dominio real.

## 6. FreePBX / Asterisk

FreePBX debe enviar eventos al backend:

```text
POST http://IP_DEL_SERVIDOR:8000/api/webhooks/asterisk-event
```

MariaDB queda como base interna de FreePBX. No conectes PostgreSQL con MariaDB directamente salvo que luego implementes una sincronizacion especifica.
