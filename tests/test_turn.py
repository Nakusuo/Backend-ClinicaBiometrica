import base64
import hashlib
import hmac

from app.core import turn
from app.core.config import settings


def test_credencial_turn_es_la_de_coturn():
    c = turn.credenciales_turn("paciente-1", "secreto", ttl=600, ahora=1_000_000)
    assert c["username"] == "1000600:paciente-1"
    esperada = base64.b64encode(hmac.new(b"secreto", b"1000600:paciente-1", hashlib.sha1).digest()).decode()
    assert c["credential"] == esperada


def test_sin_turn_solo_stun(client, datos, h_paciente_a, monkeypatch):
    monkeypatch.setattr(settings, "turn_urls", [])
    r = client.get(f"/api/llamadas/{datos['cita']}/ice-servers", headers=h_paciente_a)
    assert r.status_code == 200
    assert r.json()["iceServers"] == [{"urls": settings.stun_urls}]


def test_con_turn_entrega_credencial_temporal_sin_el_secreto(client, datos, h_doctor, monkeypatch):
    monkeypatch.setattr(settings, "turn_urls", ["turn:turn.clinica.pe:3478"])
    monkeypatch.setattr(settings, "turn_secret", "secreto-del-servidor")
    r = client.get(f"/api/llamadas/{datos['cita']}/ice-servers", headers=h_doctor)
    turn_srv = r.json()["iceServers"][-1]
    assert turn_srv["urls"] == ["turn:turn.clinica.pe:3478"]
    assert turn_srv["username"].endswith(f":doctor-{datos['doctor']}")
    assert "secreto-del-servidor" not in r.text


def test_ice_servers_exige_sesion(client, datos):
    assert client.get(f"/api/llamadas/{datos['cita']}/ice-servers").status_code == 401


def test_turn_solo_para_participantes_de_la_cita(client, datos, h_paciente_b):
    assert client.get(f"/api/llamadas/{datos['cita']}/ice-servers", headers=h_paciente_b).status_code == 403


def test_turn_no_para_citas_cerradas(client, datos, h_doctor):
    client.patch(f"/api/citas/{datos['cita']}/estado", headers=h_doctor, json={"estado": "finalizada"})
    assert client.get(f"/api/llamadas/{datos['cita']}/ice-servers", headers=h_doctor).status_code == 403
