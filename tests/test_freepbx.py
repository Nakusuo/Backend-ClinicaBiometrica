import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.routers import freepbx


@pytest.fixture()
def cdr_falso(monkeypatch):
    """Base SQLite en memoria con la tabla cdr de FreePBX (RF-19)."""
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})  # una sola base en memoria
    with engine.begin() as con:
        con.execute(text("CREATE TABLE cdr (calldate TEXT, clid TEXT, src TEXT, dst TEXT, "
                         "disposition TEXT, duration INT, billsec INT)"))
        for i in range(1, 6):
            con.execute(text("INSERT INTO cdr VALUES (:d, 'Paciente', '100', '200', 'ANSWERED', :s, :s)"),
                        {"d": f"2026-10-0{i} 10:00:00", "s": i * 10})
    sesion = sessionmaker(bind=engine)
    monkeypatch.setattr(freepbx, "get_freepbx_db", lambda: sesion())
    return engine


def test_sin_freepbx_configurado_responde_503(client, datos, h_doctor, monkeypatch):
    monkeypatch.setattr(freepbx, "get_freepbx_db", lambda: None)
    assert client.get("/api/freepbx/cdr", headers=h_doctor).status_code == 503


def test_solo_medicos_ven_el_cdr(client, datos, h_paciente_a, cdr_falso):
    assert client.get("/api/freepbx/cdr", headers=h_paciente_a).status_code == 403


def test_cdr_mas_recientes_primero_y_con_limite(client, datos, h_doctor, cdr_falso):
    r = client.get("/api/freepbx/cdr?limit=3", headers=h_doctor)
    assert r.status_code == 200
    fechas = [fila["calldate"] for fila in r.json()]
    assert fechas == ["2026-10-05 10:00:00", "2026-10-04 10:00:00", "2026-10-03 10:00:00"]


def test_error_de_freepbx_responde_502(client, datos, h_doctor, monkeypatch):
    sesion = sessionmaker(bind=create_engine("sqlite://"))  # sin tabla cdr
    monkeypatch.setattr(freepbx, "get_freepbx_db", lambda: sesion())
    assert client.get("/api/freepbx/cdr", headers=h_doctor).status_code == 502
