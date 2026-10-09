import pytest
from starlette.websockets import WebSocketDisconnect

from tests.conftest import ROSTRO_DOCTOR, ROSTRO_PACIENTE_A


# ---------- Sin token no se entra a nada protegido ----------

@pytest.mark.parametrize("metodo,ruta", [
    ("get", "/api/doctores/"),
    ("post", "/api/doctores/1/biometria"),
    ("delete", "/api/doctores/1"),
    ("get", "/api/pacientes/1"),
    ("get", "/api/citas/"),
    ("get", "/api/expedientes/paciente/1"),
    ("post", "/api/llamadas/1/aceptar"),
    ("get", "/api/llamadas/"),
])
def test_sin_token_responde_401(client, datos, metodo, ruta):
    r = getattr(client, metodo)(ruta)
    assert r.status_code == 401


def test_token_falso_responde_401(client, datos):
    r = client.get("/api/citas/", headers={"Authorization": "Bearer no-es-un-jwt"})
    assert r.status_code == 401


# ---------- Doctores ----------

def test_nadie_reemplaza_el_rostro_de_otro_medico(client, datos, h_paciente_a):
    r = client.post(f"/api/doctores/{datos['doctor']}/biometria", json={"embedding": [0.9] * 128}, headers=h_paciente_a)
    assert r.status_code == 403


def test_medico_solo_edita_su_propia_biometria(client, datos, h_doctor):
    r = client.post(f"/api/doctores/{datos['pendiente']}/biometria", json={"embedding": [0.9] * 128}, headers=h_doctor)
    assert r.status_code == 403
    r = client.post(f"/api/doctores/{datos['doctor']}/biometria", json={"embedding": [0.9] * 128}, headers=h_doctor)
    assert r.status_code == 200


def test_registro_de_medico_queda_pendiente_y_no_puede_entrar(client, datos, h_doctor):
    r = client.post("/api/auth/register-doctor", json={
        "nombre": "Nuevo Medico", "email": "nuevo@clinica.pe", "especialidad": "X", "cedula": "1",
        "telefono": "1", "password": "clave-segura", "faceEmbedding": [0.7] * 128,
    })
    assert r.status_code == 200
    assert r.json()["pendiente_aprobacion"] is True
    nuevo_id = r.json()["id"]

    r = client.post("/api/auth/login", json={"correo": "nuevo@clinica.pe", "password": "clave-segura", "role": "doctor"})
    assert r.status_code == 403

    # Un médico activo lo aprueba y ya puede entrar
    assert client.post(f"/api/doctores/{nuevo_id}/activar", headers=h_doctor).status_code == 200
    r = client.post("/api/auth/login", json={"correo": "nuevo@clinica.pe", "password": "clave-segura", "role": "doctor"})
    assert r.status_code == 200


def test_paciente_no_puede_activar_medicos(client, datos, h_paciente_a):
    r = client.post(f"/api/doctores/{datos['pendiente']}/activar", headers=h_paciente_a)
    assert r.status_code == 403


# ---------- Pacientes, citas y expedientes ----------

def test_paciente_no_ve_datos_de_otro_paciente(client, datos, h_paciente_b):
    a = datos["paciente_a"]
    assert client.get(f"/api/pacientes/{a}", headers=h_paciente_b).status_code == 403
    assert client.get(f"/api/pacientes/{a}/expediente", headers=h_paciente_b).status_code == 403
    assert client.get(f"/api/expedientes/paciente/{a}", headers=h_paciente_b).status_code == 403
    assert client.get(f"/api/citas/paciente/{a}", headers=h_paciente_b).status_code == 403
    assert client.get(f"/api/citas/{datos['cita']}", headers=h_paciente_b).status_code == 403


def test_paciente_no_modifica_ni_borra_lo_ajeno(client, datos, h_paciente_b):
    a = datos["paciente_a"]
    r = client.put(f"/api/pacientes/{a}", headers=h_paciente_b, json={
        "dni": "0", "nombre": "x", "apellido": "x", "telefono": "x", "email": "x@x.pe", "fechaNacimiento": "2000-01-01",
    })
    assert r.status_code == 403
    assert client.delete(f"/api/citas/{datos['cita']}", headers=h_paciente_b).status_code == 403


def test_paciente_ve_lo_suyo(client, datos, h_paciente_a):
    a = datos["paciente_a"]
    assert client.get(f"/api/pacientes/{a}", headers=h_paciente_a).status_code == 200
    r = client.get(f"/api/citas/paciente/{a}", headers=h_paciente_a)
    assert r.status_code == 200 and len(r.json()) == 1
    assert client.get(f"/api/citas/{datos['cita']}", headers=h_paciente_a).status_code == 200


def test_listar_citas_devuelve_solo_las_propias(client, datos, h_paciente_b, h_doctor):
    assert client.get("/api/citas/", headers=h_paciente_b).json() == []
    assert len(client.get("/api/citas/", headers=h_doctor).json()) == 1


def test_medico_no_ve_agenda_de_otro_medico(client, datos, h_doctor):
    assert client.get(f"/api/citas/doctor/{datos['pendiente']}", headers=h_doctor).status_code == 403
    assert client.get(f"/api/citas/doctor/{datos['doctor']}", headers=h_doctor).status_code == 200


def test_paciente_no_agenda_a_nombre_de_otro(client, datos, h_paciente_b):
    r = client.post("/api/citas/", headers=h_paciente_b, json={
        "paciente_id": datos["paciente_a"], "doctor_id": datos["doctor"], "fecha": "2026-10-11", "hora": "09:00",
    })
    assert r.status_code == 403


def test_expediente_lo_firma_el_medico_del_token(client, datos, h_doctor):
    r = client.post("/api/expedientes/", headers=h_doctor, json={
        "patientId": datos["paciente_a"], "doctorId": datos["pendiente"],
        "diagnostico": "Dx", "tratamiento": "Tx", "observaciones": "Obs",
    })
    assert r.status_code == 200, r.text
    assert r.json()["doctor_id"] == datos["doctor"]


# ---------- Llamadas ----------

def test_llamadas_solo_entre_participantes(client, datos, h_paciente_a, h_paciente_b, h_doctor):
    cita = datos["cita"]
    r = client.post("/api/llamadas/solicitar", headers=h_paciente_b,
                    json={"paciente_id": datos["paciente_a"], "cita_id": cita})
    assert r.status_code == 403
    r = client.post("/api/llamadas/solicitar", headers=h_paciente_a,
                    json={"paciente_id": datos["paciente_a"], "cita_id": cita})
    assert r.status_code == 200
    assert client.post(f"/api/llamadas/{cita}/aceptar", headers=h_paciente_a).status_code == 403
    assert client.post(f"/api/llamadas/{cita}/aceptar", headers=h_doctor).status_code == 200
    assert client.post(f"/api/llamadas/{cita}/terminar", headers=h_paciente_b).status_code == 403


# ---------- Login facial ----------

def test_login_facial_correcto(client, datos):
    r = client.post("/api/auth/facial-login",
                    json={"correo": "pia@mail.pe", "embedding_facial": ROSTRO_PACIENTE_A, "role": "paciente"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_facial_rechaza_vector_de_un_solo_valor(client, datos):
    # Antes numpy "estiraba" [x] a 128 valores y la comparación se podía burlar
    r = client.post("/api/auth/facial-login",
                    json={"correo": "ana@clinica.pe", "embedding_facial": [ROSTRO_DOCTOR[0]], "role": "doctor"})
    assert r.status_code == 422


def test_login_facial_no_revela_si_el_correo_existe(client, datos):
    otro_rostro = [0.9] * 128
    existe = client.post("/api/auth/facial-login", json={"correo": "ana@clinica.pe", "embedding_facial": otro_rostro})
    no_existe = client.post("/api/auth/facial-login", json={"correo": "nadie@clinica.pe", "embedding_facial": otro_rostro})
    sin_rostro = client.post("/api/auth/facial-login", json={"correo": "beto@mail.pe", "embedding_facial": otro_rostro})
    assert existe.status_code == no_existe.status_code == sin_rostro.status_code == 401
    assert existe.json() == no_existe.json() == sin_rostro.json()


def test_login_facial_respeta_el_rol(client, datos):
    # El correo del médico no sirve para entrar como paciente
    r = client.post("/api/auth/facial-login",
                    json={"correo": "ana@clinica.pe", "embedding_facial": ROSTRO_DOCTOR, "role": "paciente"})
    assert r.status_code == 401


# ---------- Webhooks ----------

def test_webhooks_exigen_token(client, datos):
    cuerpo = {"paciente_dni": "11111111", "doctor_cedula": "x", "fecha": "2026-10-10", "hora": "10:00", "motivo": "m"}
    assert client.post("/api/webhooks/citas", json=cuerpo).status_code == 401
    evento = {"event": "ringing", "caller_id": "11111111", "exten": "100"}
    assert client.post("/api/webhooks/asterisk-event", json=evento).status_code == 401
    r = client.post("/api/webhooks/asterisk-event", json=evento, headers={"X-Webhook-Token": "token-webhook-pruebas"})
    assert r.status_code == 200


# ---------- WebSocket ----------

def test_websocket_sin_token_se_cierra(client, datos):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/ws/doctor/{datos['doctor']}") as ws:
            ws.receive_json()


def test_websocket_no_permite_suplantar_a_otro_usuario(client, datos, h_paciente_a):
    token = h_paciente_a["Authorization"].split()[1]
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/ws/doctor/{datos['doctor']}?token={token}") as ws:
            ws.receive_json()


def test_websocket_con_token_propio_conecta(client, datos, h_doctor):
    token = h_doctor["Authorization"].split()[1]
    with client.websocket_connect(f"/ws/doctor/{datos['doctor']}?token={token}") as ws:
        ws.send_json({"type": "ping"})
