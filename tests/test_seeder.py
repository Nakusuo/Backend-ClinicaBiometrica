from datetime import date

from app.db.database import SessionLocal
from app.db.seeder import seed_db
from app.models.cita import Cita


def test_citas_demo_desde_hoy(client):
    # Issue #9: las citas de prueba deben verse en "Citas de Hoy", no quedar en el pasado
    db = SessionLocal()
    try:
        seed_db(db)
        fechas = sorted(c.fecha for c in db.query(Cita).all())
    finally:
        db.close()
    assert fechas[0] == date.today().isoformat()
    assert all(f >= date.today().isoformat() for f in fechas)
