<p align="center">
  <a href="https://github.com/Nakusuo"><img src="https://raw.githubusercontent.com/Nakusuo/Nakusuo/main/assets/covers/Backend-ClinicaBiometrica.svg" width="100%" alt="Backend-ClinicaBiometrica — Nakusu"/></a>
</p>

# Backend Clínico - Plataforma de Telemedicina Integrada

Backend desarrollado con **FastAPI** y **PostgreSQL** para la gestión de pacientes, doctores, citas y expedientes médicos.

## Tecnologías utilizadas

* Python 3.12+
* FastAPI
* PostgreSQL
* SQLAlchemy
* JWT Authentication
* Swagger UI

---

## Estructura del proyecto

```text
backend-clinico/
│
├── app/
│   ├── main.py
│   ├── db/
│   ├── routers/
│   ├── models/
│   ├── schemas/
│   ├── core/
│   └── requirements.txt
│
├── migrations/          # Esquema de la base (Alembic)
├── tests/
├── alembic.ini
├── requirements-dev.txt
├── .env.example
└── README.md
```

---

## Instalación

### 1. Clonar repositorio

```bash
git clone https://github.com/Nakusuo/Backend-ClinicaBiometrica
cd backend-clinico
```

### 2. Crear entorno virtual

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/Mac:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r app/requirements.txt
```
### 4. Configuración del archivo .env

Crear un archivo `.env` en la raíz del proyecto tomando como referencia `.env.example`.


### 5. Configuración de PostgreSQL

  1. Instalar PostgreSQL.
  2. Crear una base de datos llamada:

  ```sql
  CREATE DATABASE telemedicina;
  ```

  3. Configurar el usuario y contraseña de PostgreSQL en el archivo .env.

---

## Ejecutar el proyecto

Desde la raíz del proyecto ejecutar:

```bash
uvicorn app.main:app --reload
```

Si todo funciona correctamente aparecerá un mensaje similar a:

```text
Uvicorn running on http://127.0.0.1:8000
```

Al arrancar, la API aplica sola las migraciones pendientes (`AUTO_MIGRATE=true`).

---

## Migraciones de base de datos

El esquema vive en `migrations/` (Alembic). Para aplicarlas a mano:

```bash
python -m app.db.migrar
```

Si cambias un modelo, genera la migración y revísala antes de subirla:

```bash
alembic revision --autogenerate -m "describe el cambio"
alembic upgrade head
```

Las bases creadas con versiones anteriores (sin Alembic) se reconocen solas: se marcan como
migración inicial sin tocar los datos.

---

## Pruebas

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
```

Comprueban que cada usuario solo accede a lo suyo (pacientes, citas, expedientes, llamadas, WebSocket),
que el login facial no se puede burlar, que la API no inventa datos clínicos y que las migraciones
coinciden con los modelos. GitHub Actions corre lo mismo en cada PR, más las migraciones en PostgreSQL
y el build de la imagen Docker.

## Acceso a Swagger

Una vez iniciado el servidor, abrir en el navegador:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

---

## Endpoints disponibles

### Auth

* POST /api/auth/login
* POST /api/auth/facial-login
* POST /api/auth/register-doctor
* POST /api/auth/register-patient

### Pacientes

* GET /api/pacientes
* GET /api/pacientes/{id}
* POST /api/pacientes
* PUT /api/pacientes/{id}
* DELETE /api/pacientes/{id}
* POST /api/pacientes/{id}/biometria (el propio paciente)

### Doctores

* GET /api/doctores
* GET /api/doctores/{id}
* POST /api/doctores
* PUT /api/doctores/{id}
* DELETE /api/doctores/{id}
* POST /api/doctores/{id}/activar (aprobar un médico registrado)
* POST /api/doctores/{id}/biometria (el propio médico)

### Citas

* GET /api/citas
* GET /api/citas/{id}
* POST /api/citas
* PUT /api/citas/{id}
* DELETE /api/citas/{id}

### Expedientes

* GET /api/expedientes
* GET /api/expedientes/recientes (últimas consultas del médico)
* GET /api/expedientes/{id}
* POST /api/expedientes
* PUT /api/expedientes/{id}
* DELETE /api/expedientes/{id}

### Webhooks

* POST /api/webhooks/citas
* POST /api/webhooks/asterisk-event

Los webhooks exigen el header `X-Webhook-Token`.

---

## Estado actual

✅ Estructura inicial FastAPI configurada

✅ Swagger/OpenAPI habilitado

✅ Routers definidos

🔄 Pendiente: integración PostgreSQL

🔄 Pendiente: modelos SQLAlchemy

🔄 Pendiente: autenticación JWT completa

🔄 Pendiente: CRUD funcional
