# Guia definitiva gratis: Backend, Frontend, PostgreSQL, FreePBX y MariaDB

Objetivo: montar una arquitectura funcional para laboratorio/tesis usando solo herramientas gratis o free tier.

```text
Frontend Angular
  -> Backend FastAPI
      -> PostgreSQL clinico
      -> MariaDB de FreePBX, solo lectura
FreePBX/Asterisk
  -> MariaDB interna de FreePBX
  -> Webhook al Backend
```

Regla principal: el navegador nunca debe conectarse directo a PostgreSQL, MariaDB ni FreePBX. El backend es la capa de control.

## 0. Que es gratis y que no

Gratis:

- Ubuntu Server en VirtualBox.
- Docker y Docker Compose.
- FreePBX/Asterisk con modulos open source.
- WireGuard para cifrar trafico entre servidores.
- Cloudflare DNS y Cloudflare Tunnel para web/API HTTP/HTTPS.

Evitar si quieres mantener todo gratis:

- Cloudflare Spectrum para SIP/RTP.
- Modulos comerciales de FreePBX.
- Troncales SIP reales pagadas.
- VPS o dominio pagado, si no son necesarios.

## 1. Maquinas recomendadas

Para que sea ordenado, usa dos VMs si puedes:

```text
VM 1: Ubuntu Server
- Backend FastAPI
- PostgreSQL
- Frontend Angular servido por Nginx

VM 2: FreePBX
- Asterisk
- MariaDB interna de FreePBX
```

Si solo tienes una VM, tambien se puede, pero FreePBX suele estar mejor separado.

Nota: FreePBX 17 esta orientado a Debian. Para no complicarte, usa una VM separada con FreePBX/Debian o una ISO/instalador recomendado por FreePBX. Tu Ubuntu Server queda para la web y el backend.

## 2. Corregir hora de Ubuntu Server

Si aparece este error:

```text
Release file ... is not valid yet
```

Corrige la hora:

```bash
date
timedatectl
sudo timedatectl set-timezone America/Lima
sudo timedatectl set-ntp true
sudo systemctl restart systemd-timesyncd
timedatectl
sudo apt update
```

Si sigue fallando, coloca la hora manual:

```bash
sudo timedatectl set-ntp false
sudo timedatectl set-time "2026-06-25 11:30:00"
sudo apt update
```

Cambia la fecha/hora por la real.

## 3. Instalar Docker en Ubuntu Server

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
docker --version
docker compose version
```

Para usar Docker sin `sudo`:

```bash
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world
```

## 4. Subir el backend al Ubuntu Server

Desde tu PC Windows puedes usar Git o copiar la carpeta.

Opcion con Git:

```bash
git clone URL_DE_TU_REPO Backend-ClinicaBiometrica
cd Backend-ClinicaBiometrica
```

Opcion copiando por SCP desde Windows PowerShell:

```powershell
scp -r C:\Users\Lenovo\Desktop\Backend-ClinicaBiometrica vboxuser@IP_UBUNTU:/home/vboxuser/
```

En Ubuntu:

```bash
cd ~/Backend-ClinicaBiometrica
cp .env.example .env
nano .env
```

Configura `.env`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=una_clave_fuerte
POSTGRES_DB=telemedicina

SECRET_KEY=otra_clave_larga_y_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

CORS_ORIGINS=http://IP_UBUNTU,http://localhost:4200

ASTERISK_WEBHOOK_TOKEN=token_largo_para_freepbx

FREEPBX_DB_HOST=IP_FREEPBX
FREEPBX_DB_PORT=3306
FREEPBX_DB_USER=telemedicina_ro
FREEPBX_DB_PASSWORD=clave_solo_lectura
FREEPBX_DB_NAME=asteriskcdrdb
```

Levanta backend y PostgreSQL:

```bash
docker compose up -d --build
docker compose logs -f web
```

Prueba:

```text
http://IP_UBUNTU:8000/docs
```

## 5. PostgreSQL clinico

Tu backend ya usa PostgreSQL con Docker:

```text
Backend FastAPI -> PostgreSQL
```

En `docker-compose.yml`, PostgreSQL queda expuesto solo localmente:

```text
127.0.0.1:5432:5432
```

Eso evita exponer la base clinica a la red.

Comandos utiles:

```bash
docker compose ps
docker compose logs db
docker exec -it telemedicina_db psql -U postgres -d telemedicina
```

## 6. FreePBX y MariaDB

FreePBX maneja internamente Asterisk y MariaDB.

```text
FreePBX/Asterisk <-> MariaDB FreePBX
```

No conectes el frontend a MariaDB. El backend consulta MariaDB con usuario de solo lectura.

En la VM de FreePBX, crea un usuario MariaDB de solo lectura. El nombre de la base de CDR normalmente es `asteriskcdrdb`.

```bash
sudo mysql
```

Dentro de MariaDB:

```sql
CREATE USER 'telemedicina_ro'@'IP_UBUNTU' IDENTIFIED BY 'clave_solo_lectura';
GRANT SELECT ON asteriskcdrdb.* TO 'telemedicina_ro'@'IP_UBUNTU';
FLUSH PRIVILEGES;
EXIT;
```

Si estas en laboratorio y las IP cambian mucho, puedes usar temporalmente:

```sql
CREATE USER 'telemedicina_ro'@'%' IDENTIFIED BY 'clave_solo_lectura';
GRANT SELECT ON asteriskcdrdb.* TO 'telemedicina_ro'@'%';
FLUSH PRIVILEGES;
```

Pero para defensa final es mejor limitar por IP.

Prueba desde Ubuntu Server:

```bash
sudo apt install -y mariadb-client
mysql -h IP_FREEPBX -u telemedicina_ro -p asteriskcdrdb
```

Consulta:

```sql
SELECT calldate, src, dst, disposition, duration
FROM cdr
ORDER BY calldate DESC
LIMIT 5;
```

## 7. Endpoint backend para consultar llamadas de FreePBX

El backend ahora incluye:

```text
GET /api/freepbx/cdr
```

Sirve para consultar CDR de MariaDB/FreePBX desde FastAPI.

Requiere token JWT:

```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://IP_UBUNTU:8000/api/freepbx/cdr?limit=20"
```

Esto cumple la idea:

```text
Backend -> consulta con usuario y password -> MariaDB FreePBX
```

## 8. Webhook de Asterisk/FreePBX hacia backend

El backend tiene:

```text
POST /api/webhooks/asterisk-event
```

Si configuras `ASTERISK_WEBHOOK_TOKEN`, FreePBX/Asterisk debe mandar el header:

```text
X-Webhook-Token: token_largo_para_freepbx
```

Payload de prueba:

```bash
curl -X POST "http://IP_UBUNTU:8000/api/webhooks/asterisk-event" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Token: token_largo_para_freepbx" \
  -d '{
    "event": "ringing",
    "caller_id": "999999999",
    "exten": "1001",
    "room_id": "room_demo",
    "duration": 0
  }'
```

## 9. Cifrado gratis entre Ubuntu y FreePBX

Para laboratorio local, puedes empezar solo con red interna de VirtualBox y firewall.

Para una defensa mas fuerte, usa WireGuard:

```text
Ubuntu Server <-> WireGuard VPN <-> FreePBX
```

Gratis y defendible:

- MariaDB no se expone a internet.
- Solo acepta conexiones desde IP de Ubuntu o IP VPN.
- Usuario MariaDB de solo lectura.
- Webhook con token.
- Nginx/HTTPS para la web.

## 10. Firewall gratis

En Ubuntu Server:

```bash
sudo apt install -y ufw
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
sudo ufw status
```

Cuando uses Nginx, puedes cerrar el puerto 8000 publico:

```bash
sudo ufw delete allow 8000/tcp
```

En FreePBX, no publiques MariaDB a internet. Permite 3306 solo desde Ubuntu o WireGuard.

## 11. Frontend Angular

Tu frontend esta en:

```text
C:\Users\Lenovo\Desktop\Frontend-Biometria
```

Tiene estas URLs:

```ts
apiUrl: 'http://localhost:8000/api'
wsUrl: 'ws://localhost:8000'
```

Para Ubuntu local/laboratorio cambia:

```ts
apiUrl: 'http://IP_UBUNTU:8000/api'
wsUrl: 'ws://IP_UBUNTU:8000'
```

En `dashboard.component.ts` hay un WebSocket fijo:

```ts
const wsUrl = `ws://localhost:8000/ws/doctor/${doctorId}`;
```

Debe quedar usando `environment.wsUrl`:

```ts
const wsUrl = `${environment.wsUrl}/ws/doctor/${doctorId}`;
```

Y arriba importar:

```ts
import { environment } from '../../../environments/environment';
```

Build:

```bash
npm install
npm run build
```

Subir `dist/` a Ubuntu o copiar todo el frontend y compilar alla.

## 12. Servir frontend con Nginx

En Ubuntu:

```bash
sudo apt install -y nginx
sudo mkdir -p /var/www/telemedicina
sudo cp -r dist/* /var/www/telemedicina/
```

Config Nginx simple:

```nginx
server {
    listen 80;
    server_name _;

    root /var/www/telemedicina;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

Con Nginx, el frontend puede usar:

```ts
apiUrl: '/api'
wsUrl: `ws://${window.location.host}`
```

## 13. Cloudflare gratis

Usalo solo para web/API HTTP/HTTPS si tienes dominio:

```text
Usuario -> Cloudflare -> Nginx -> Backend/Frontend
```

Cloudflare Tunnel tambien sirve para publicar web/API sin abrir puertos entrantes.

No uses Cloudflare Spectrum para SIP/RTP si quieres mantener todo gratis. Para telefonia usa red local, firewall o WireGuard.

## 14. Biometria con fotos y vulnerabilidad

Tu backend guarda embeddings faciales y compara distancia.

Prueba academica:

1. Registrar usuario con foto real.
2. Intentar login con otra foto de la misma persona.
3. Documentar si entra o falla.
4. Explicar vulnerabilidad:

```text
La autenticacion facial con foto estatica puede ser vulnerable a ataques de presentacion.
Para produccion se requiere prueba de vida, camara en tiempo real, reto de parpadeo/movimiento o doble factor.
```

## 15. Checklist de defensa

- Frontend no accede directo a bases de datos.
- Backend usa PostgreSQL para datos clinicos.
- FreePBX usa su MariaDB interna.
- Backend consulta MariaDB FreePBX con usuario solo lectura.
- PostgreSQL no esta expuesto publicamente.
- Webhook de Asterisk tiene token.
- Comunicacion sensible puede ir por WireGuard.
- Cloudflare se limita a web/API gratis.
- Biometria con fotos se presenta como prueba de vulnerabilidad, no como seguridad final.

## 16. Frase para explicar arquitectura

> La plataforma web se comunica solo con el backend FastAPI. El backend administra la base clinica PostgreSQL y consulta la base MariaDB de FreePBX mediante un usuario de solo lectura para obtener registros de llamadas. FreePBX mantiene su propia base interna y envia eventos al backend mediante webhooks protegidos con token. Para cifrar la comunicacion entre servidores se propone WireGuard, manteniendo todo con herramientas gratuitas.
