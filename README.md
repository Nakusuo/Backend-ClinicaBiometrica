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
│   └── core/
│
├── requirements.txt
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
pip install -r requirements.txt
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

---

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

### Pacientes

* GET /api/pacientes
* GET /api/pacientes/{id}
* POST /api/pacientes
* PUT /api/pacientes/{id}
* DELETE /api/pacientes/{id}

### Doctores

* GET /api/doctores
* GET /api/doctores/{id}
* POST /api/doctores
* PUT /api/doctores/{id}
* DELETE /api/doctores/{id}

### Citas

* GET /api/citas
* GET /api/citas/{id}
* POST /api/citas
* PUT /api/citas/{id}
* DELETE /api/citas/{id}

### Expedientes

* GET /api/expedientes
* GET /api/expedientes/{id}
* POST /api/expedientes
* PUT /api/expedientes/{id}
* DELETE /api/expedientes/{id}

### Webhooks

* POST /api/webhooks/citas

---

## Estado actual

✅ Estructura inicial FastAPI configurada

✅ Swagger/OpenAPI habilitado

✅ Routers definidos

🔄 Pendiente: integración PostgreSQL

🔄 Pendiente: modelos SQLAlchemy

🔄 Pendiente: autenticación JWT completa

🔄 Pendiente: CRUD funcional
