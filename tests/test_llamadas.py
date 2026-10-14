from datetime import timedelta

from app.db.database import SessionLocal
from app.models.llamada import Llamada


def test_terminar_llamada_guarda_la_duracion(client, datos, h_doctor, h_paciente_a):
    # RF-18
    cita = datos["cita"]
    assert client.post("/api/llamadas/solicitar", headers=h_paciente_a,
                       json={"paciente_id": datos["paciente_a"], "cita_id": cita}).status_code == 200
    assert client.post(f"/api/llamadas/{cita}/aceptar", headers=h_doctor).status_code == 200

    # Simula 90 s de llamada adelantando el inicio
    db = SessionLocal()
    llamada = db.query(Llamada).filter(Llamada.cita_id == cita).first()
    llamada.start_time = llamada.start_time - timedelta(seconds=90)
    db.commit()
    db.close()

    assert client.post(f"/api/llamadas/{cita}/terminar", headers=h_doctor).status_code == 200
    db = SessionLocal()
    llamada = db.query(Llamada).filter(Llamada.cita_id == cita).first()
    db.close()
    assert llamada.estado == "terminada"
    assert 90 <= llamada.duracion <= 95
