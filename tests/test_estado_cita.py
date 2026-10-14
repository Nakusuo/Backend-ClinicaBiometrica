def test_medico_cambia_el_estado_y_el_paciente_solo_cancela(client, datos, h_doctor, h_paciente_a):
    # RF-11
    url = f"/api/citas/{datos['cita']}/estado"
    assert client.patch(url, headers=h_paciente_a, json={"estado": "finalizada"}).status_code == 403
    assert client.patch(url, headers=h_doctor, json={"estado": "en_curso"}).json()["estado"] == "en_curso"
    assert client.patch(url, headers=h_doctor, json={"estado": "cualquiera"}).status_code == 422
    assert client.patch(url, headers=h_paciente_a, json={"estado": "cancelada"}).json()["estado"] == "cancelada"
