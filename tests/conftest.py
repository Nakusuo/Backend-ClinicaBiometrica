import os
import tempfile

# La configuración se lee al importar app.*, así que el entorno va antes de cualquier import
_db_dir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_db_dir}/test.db"
os.environ["SECRET_KEY"] = "clave-de-pruebas-suficientemente-larga-123456"
os.environ["ASTERISK_WEBHOOK_TOKEN"] = "token-webhook-pruebas"
os.environ["SEED_DEMO_DATA"] = "false"
os.environ["DOCTOR_REQUIRES_APPROVAL"] = "true"
os.environ["ENVIRONMENT"] = "development"
# Los tests crean las tablas con create_all; las migraciones se prueban en test_migraciones.py
os.environ["AUTO_MIGRATE"] = "false"

import json  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.db.database import Base, engine, SessionLocal  # noqa: E402
from app.models.doctor import Doctor  # noqa: E402
from app.models.paciente import Paciente  # noqa: E402
from app.models.cita import Cita  # noqa: E402
from app.routers.auth import hash_password  # noqa: E402

ROSTRO_DOCTOR = [0.05] * 128
ROSTRO_PACIENTE_A = [0.3] * 128


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def datos(client):
    """Un médico activo, uno pendiente, dos pacientes y una cita del paciente A."""
    db = SessionLocal()
    doctor = Doctor(nombres="Ana", apellidos="Ruiz", correo="ana@clinica.pe", password_hash=hash_password("clave-doctor"),
                    embedding_facial=json.dumps(ROSTRO_DOCTOR), rol="doctor", activo=True)
    pendiente = Doctor(nombres="Luis", apellidos="Paz", correo="luis@clinica.pe", password_hash=hash_password("clave-luis"),
                       rol="doctor", activo=False)
    paciente_a = Paciente(dni="11111111", nombres="Pía", apellidos="A", correo="pia@mail.pe",
                          password_hash=hash_password("clave-pia"), embedding_facial=json.dumps(ROSTRO_PACIENTE_A))
    paciente_b = Paciente(dni="22222222", nombres="Beto", apellidos="B", correo="beto@mail.pe",
                          password_hash=hash_password("clave-beto"))
    db.add_all([doctor, pendiente, paciente_a, paciente_b])
    db.flush()
    cita = Cita(paciente_id=paciente_a.id, doctor_id=doctor.id, fecha="2026-10-10", hora="10:00", motivo="Control")
    db.add(cita)
    db.commit()
    ids = {"doctor": doctor.id, "pendiente": pendiente.id, "paciente_a": paciente_a.id,
           "paciente_b": paciente_b.id, "cita": cita.id}
    db.close()
    return ids


def login(client, correo, password, role):
    r = client.post("/api/auth/login", json={"correo": correo, "password": password, "role": role})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def h_doctor(client, datos):
    return login(client, "ana@clinica.pe", "clave-doctor", "doctor")


@pytest.fixture()
def h_paciente_a(client, datos):
    return login(client, "pia@mail.pe", "clave-pia", "paciente")


@pytest.fixture()
def h_paciente_b(client, datos):
    return login(client, "beto@mail.pe", "clave-beto", "paciente")
