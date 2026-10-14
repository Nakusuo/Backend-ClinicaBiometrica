def cuerpo(datos, **cambios):
    return {"paciente_id": datos["paciente_a"], "doctor_id": datos["doctor"], "fecha": "2099-01-10",
            "hora": "10:00 AM", "motivo": "Control", **cambios}


def test_paciente_reprograma_pero_no_cambia_el_estado(client, datos, h_paciente_a):
    url = f"/api/citas/{datos['cita']}"
    r = client.put(url, headers=h_paciente_a, json=cuerpo(datos))
    assert r.status_code == 200
    assert r.json()["fecha"] == "2099-01-10"
    assert r.json()["estado"] == "programada"
    assert client.put(url, headers=h_paciente_a, json=cuerpo(datos, estado="finalizada")).status_code == 403


def test_medico_si_cambia_el_estado_por_put(client, datos, h_doctor):
    r = client.put(f"/api/citas/{datos['cita']}", headers=h_doctor, json=cuerpo(datos, estado="en_curso"))
    assert r.json()["estado"] == "en_curso"
