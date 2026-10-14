"""Pruebas de aceptación por API (docs/cmmi/verificacion-validacion.md).

Cubre los escenarios que no necesitan cámara, audio ni un celular. PA-03, PA-08 y PA-11
se ejecutan a mano. Corre contra una API levantada con SEED_DEMO_DATA=true y
DOCTOR_REQUIRES_APPROVAL=true:

    python scripts/aceptacion_api.py [http://localhost:8000]
"""
import sys
import time
from datetime import date, timedelta

import httpx

API = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/") + "/api"
SUFIJO = str(int(time.time()))[-6:]
# Un día futuro distinto en cada ejecución para poder repetir el script sobre la misma base
DIA = (date.today() + timedelta(days=2 + int(SUFIJO) % 300)).isoformat()
http = httpx.Client(base_url=API, timeout=10)
resultados: list[tuple[str, bool, str]] = []


def caso(pa: str, descripcion: str):
    def decorador(funcion):
        try:
            funcion()
            resultados.append((pa, True, descripcion))
        except AssertionError as e:
            resultados.append((pa, False, f"{descripcion} — {e}"))
        return funcion
    return decorador


def login(correo, password, rol):
    r = http.post("/auth/login", json={"correo": correo, "password": password, "role": rol})
    assert r.status_code == 200, f"login {correo}: {r.status_code}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


doctor = login("doctor@email.com", "password123", "doctor")
maria = login("maria@email.com", "password123", "paciente")
estado = {}


@caso("PA-01", "Registrar paciente nuevo y entrar")
def _():
    correo = f"pa01.{SUFIJO}@mail.pe"
    r = http.post("/auth/register-patient", json={
        "nombre": "Ana", "apellido": "Prueba", "dni": SUFIJO.rjust(8, "0"), "email": correo,
        "telefono": "999000111", "fechaNacimiento": "1990-05-01", "password": "clave-segura-1",
    })
    assert r.status_code == 200, f"registro {r.status_code} {r.text[:120]}"
    estado["nuevo_id"] = r.json()["id"]
    estado["nuevo"] = login(correo, "clave-segura-1", "paciente")


@caso("PA-02", "Médico nuevo queda pendiente hasta que otro lo activa")
def _():
    correo = f"pa02.{SUFIJO}@clinica.pe"
    r = http.post("/auth/register-doctor", json={
        "nombre": "Luis Prueba", "email": correo, "especialidad": "Pediatría", "cedula": f"CMP{SUFIJO}",
        "telefono": "999000222", "password": "clave-segura-2", "faceEmbedding": [0.1] * 128,
    })
    assert r.status_code == 200, f"registro {r.status_code} {r.text[:120]}"
    nuevo_id = r.json()["id"]
    bloqueado = http.post("/auth/login", json={"correo": correo, "password": "clave-segura-2", "role": "doctor"})
    assert bloqueado.status_code in (401, 403), f"entró sin aprobación ({bloqueado.status_code})"
    assert http.post(f"/doctores/{nuevo_id}/activar", headers=doctor).status_code == 200, "no se pudo activar"
    login(correo, "clave-segura-2", "doctor")


@caso("PA-04", "Cada rol solo usa la API de su lado")
def _():
    assert http.get("/pacientes/", headers=maria).status_code == 403, "paciente lista pacientes"
    assert http.get("/pacientes/", headers=doctor).status_code == 200, "médico no lista pacientes"


@caso("PA-05", "Agendar y rechazar el mismo horario")
def _():
    cita = {"doctor_id": 1, "fecha": DIA, "hora": "10:00 AM", "motivo": "Aceptación"}
    r = http.post("/citas/", headers=maria, json={**cita, "paciente_id": 1})
    assert r.status_code == 200, f"primera cita {r.status_code} {r.text[:120]}"
    estado["cita"] = r.json()["id"]
    assert "nuevo" in estado, "PA-01 no creó el segundo paciente"
    r2 = http.post("/citas/", headers=estado["nuevo"], json={**cita, "paciente_id": estado["nuevo_id"]})
    assert r2.status_code == 409, f"segunda cita en el mismo horario: {r2.status_code}"


@caso("PA-06", "El médico ve hoy y todas sus citas")
def _():
    citas = http.get("/citas/doctor/1", headers=doctor).json()
    fechas = {c["fecha"] for c in citas}
    assert date.today().isoformat() in fechas, "no hay citas de hoy"
    assert DIA in fechas, "no aparece la cita de mañana"


@caso("PA-07", "Reprogramar y cancelar")
def _():
    cita = estado["cita"]
    r = http.put(f"/citas/{cita}", headers=maria, json={
        "paciente_id": 1, "doctor_id": 1, "fecha": DIA, "hora": "11:30 AM", "motivo": "Aceptación"})
    assert r.status_code == 200 and r.json()["hora"] == "11:30 AM", f"reprogramar {r.status_code}"
    r = http.patch(f"/citas/{cita}/estado", headers=maria, json={"estado": "cancelada"})
    assert r.status_code == 200 and r.json()["estado"] == "cancelada", f"cancelar {r.status_code}"
    r = http.post("/citas/", headers=maria, json={
        "paciente_id": 1, "doctor_id": 1, "fecha": DIA, "hora": "11:30 AM", "motivo": "Reuso"})
    assert r.status_code == 200, f"el horario cancelado no quedó libre ({r.status_code})"


@caso("PA-09", "El médico registra la consulta y el paciente la ve")
def _():
    r = http.post("/expedientes/", headers=doctor, json={
        "paciente_id": 1, "diagnostico": "Rinitis alérgica", "tratamiento": "Loratadina 10 mg"})
    assert r.status_code == 200, f"crear expediente {r.status_code} {r.text[:120]}"
    propios = http.get("/expedientes/paciente/1", headers=maria)
    assert propios.status_code == 200, f"paciente no ve su expediente ({propios.status_code})"
    assert "Rinitis alérgica" in propios.text, "la consulta no aparece"


@caso("PA-10", "Un paciente no ve el expediente de otro")
def _():
    otro = http.get("/pacientes/", headers=doctor).json()
    ajeno = next((p["id"] for p in otro if p["id"] != 1), None)
    assert ajeno, "no hay otro paciente para probar"
    assert http.get(f"/expedientes/paciente/{ajeno}", headers=maria).status_code == 403, "vio un expediente ajeno"


ok = sum(1 for _, paso, _ in resultados if paso)
print("| ID | Resultado | Escenario |\n|---|---|---|")
for pa, paso, texto in resultados:
    print(f"| {pa} | {'✅' if paso else '❌'} | {texto} |")
print(f"\n{ok}/{len(resultados)} escenarios pasan. PA-03, PA-08 y PA-11 se ejecutan a mano.")
sys.exit(0 if ok == len(resultados) else 1)
