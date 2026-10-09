"""La API no debe inventar datos clínicos y debe validar lo que guarda."""
from datetime import date

from app.core.tiempo import calcular_edad
from app.db.database import SessionLocal
from app.models.paciente import Paciente
from app.models.receta import Receta
from app.models.expediente import Expediente


def test_calcular_edad():
    hoy = date(2026, 10, 9)
    assert calcular_edad("1995-10-20", hoy) == 30  # aún no cumple
    assert calcular_edad("1995-10-09", hoy) == 31  # cumple hoy
    assert calcular_edad(None, hoy) is None
    assert calcular_edad("20/10/1995", hoy) is None


def test_cita_muestra_edad_real_o_nada(client, datos, h_doctor):
    db = SessionLocal()
    db.query(Paciente).filter(Paciente.id == datos["paciente_a"]).update({"fecha_nacimiento": None})
    db.commit()
    db.close()
    cita = client.get(f"/api/citas/{datos['cita']}", headers=h_doctor).json()
    # Antes devolvía 30 por defecto
    assert cita["age"] is None
    assert cita["doctorName"] == "Ana Ruiz"


def test_expediente_nuevo_no_inventa_alergias_ni_posologia(client, datos, h_doctor):
    r = client.post("/api/expedientes/", headers=h_doctor, json={
        "patientId": datos["paciente_b"], "diagnostico": "Faringitis", "tratamiento": "Ibuprofeno",
    })
    assert r.status_code == 200, r.text
    db = SessionLocal()
    exp = db.query(Expediente).filter(Expediente.paciente_id == datos["paciente_b"]).one()
    receta = db.query(Receta).filter(Receta.paciente_id == datos["paciente_b"]).one()
    db.close()
    assert exp.alergias_conocidas is None and exp.grupo_sanguineo is None
    assert receta.frecuencia is None and receta.duracion_tratamiento is None


def test_paciente_incluye_resumen_clinico_real(client, datos, h_doctor):
    db = SessionLocal()
    db.add(Expediente(paciente_id=datos["paciente_a"], grupo_sanguineo="A", factor_rh="-", alergias_conocidas="Penicilina"))
    db.commit()
    db.close()
    a = client.get(f"/api/pacientes/{datos['paciente_a']}", headers=h_doctor).json()
    assert a["grupoSanguineo"] == "A-" and a["alergias"] == "Penicilina"
    b = client.get(f"/api/pacientes/{datos['paciente_b']}", headers=h_doctor).json()
    assert b["grupoSanguineo"] is None and b["alergias"] is None


def _registro(fecha):
    return {"nombre": "Ana", "apellido": "Q", "dni": "33333333", "email": "anaq@mail.pe", "telefono": "1",
            "fechaNacimiento": fecha, "password": "clave-segura"}


def test_registro_valida_fecha_de_nacimiento(client, datos):
    assert client.post("/api/auth/register-patient", json=_registro("20/10/1995")).status_code == 422
    assert client.post("/api/auth/register-patient", json=_registro("2999-01-01")).status_code == 422


def test_fecha_con_hora_se_guarda_como_dia(client, datos, h_doctor):
    # El datepicker de Angular envía la fecha completa con hora
    r = client.post("/api/pacientes/", headers=h_doctor, json={
        "nombre": "Leo", "apellido": "M", "dni": "44444444", "fechaNacimiento": "1990-03-04T05:00:00.000Z",
    })
    assert r.status_code == 200, r.text
    assert r.json()["fechaNacimiento"] == "1990-03-04"


def test_paciente_registra_su_propio_rostro(client, datos, h_paciente_b, h_paciente_a):
    r = client.post(f"/api/pacientes/{datos['paciente_b']}/biometria", headers=h_paciente_a, json={"embedding": [0.4] * 128})
    assert r.status_code == 403
    r = client.post(f"/api/pacientes/{datos['paciente_b']}/biometria", headers=h_paciente_b, json={"embedding": [0.4] * 128})
    assert r.status_code == 200
    r = client.post("/api/auth/facial-login", json={"correo": "beto@mail.pe", "embedding_facial": [0.4] * 128, "role": "paciente"})
    assert r.status_code == 200


def test_consultas_recientes_solo_del_medico(client, datos, h_doctor, h_paciente_a):
    client.post("/api/expedientes/", headers=h_doctor, json={
        "patientId": datos["paciente_a"], "diagnostico": "Control", "tratamiento": "Ninguno",
    })
    r = client.get("/api/expedientes/recientes", headers=h_doctor)
    assert r.status_code == 200
    assert [x["diagnostico"] for x in r.json()] == ["Control"]
    assert r.json()[0]["patientName"] == "Pía A"
    assert client.get("/api/expedientes/recientes", headers=h_paciente_a).status_code == 403
