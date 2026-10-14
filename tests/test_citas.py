from datetime import date, timedelta

MANANA = (date.today() + timedelta(days=1)).isoformat()
AYER = (date.today() - timedelta(days=1)).isoformat()


def agendar(client, headers, datos, fecha, hora="09:00 AM"):
    return client.post("/api/citas/", headers=headers, json={
        "paciente_id": datos["paciente_a"], "doctor_id": datos["doctor"], "fecha": fecha, "hora": hora, "motivo": "Control",
    })


def test_no_se_agenda_en_el_pasado(client, datos, h_paciente_a):
    assert agendar(client, h_paciente_a, datos, AYER).status_code == 422


def test_no_se_cruza_el_horario_del_medico(client, datos, h_paciente_a):
    assert agendar(client, h_paciente_a, datos, MANANA).status_code == 200
    assert agendar(client, h_paciente_a, datos, MANANA).status_code == 409
    assert agendar(client, h_paciente_a, datos, MANANA, "09:30 AM").status_code == 200


def test_cita_cancelada_libera_el_horario(client, datos, h_paciente_a, h_doctor):
    cita = agendar(client, h_paciente_a, datos, MANANA).json()
    client.patch(f"/api/citas/{cita['id']}/estado", headers=h_doctor, json={"estado": "cancelada"})
    assert agendar(client, h_paciente_a, datos, MANANA).status_code == 200
