"""Las migraciones deben producir exactamente el esquema de los modelos."""
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect

import app.db.migrar as migrar_mod
from app.db.database import Base


def _usar_base_temporal(monkeypatch, tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/mig.db")
    monkeypatch.setattr(migrar_mod, "engine", engine)
    # migrations/env.py usa el engine de app.db.database
    monkeypatch.setattr("app.db.database.engine", engine)
    return engine


def test_base_nueva_queda_igual_a_los_modelos(monkeypatch, tmp_path):
    engine = _usar_base_temporal(monkeypatch, tmp_path)
    migrar_mod.migrar()

    with engine.connect() as conn:
        diferencias = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert diferencias == []


def test_base_antigua_sin_alembic_se_marca_y_no_se_recrea(monkeypatch, tmp_path):
    engine = _usar_base_temporal(monkeypatch, tmp_path)
    # Así quedaban las bases creadas por la versión anterior (create_all al arrancar)
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.exec_driver_sql("INSERT INTO doctores (correo, activo) VALUES ('viejo@clinica.pe', 1)")

    migrar_mod.migrar()

    assert "alembic_version" in inspect(engine).get_table_names()
    with engine.connect() as conn:
        assert conn.exec_driver_sql("SELECT correo FROM doctores").scalar() == "viejo@clinica.pe"


def test_downgrade_completo_funciona(monkeypatch, tmp_path):
    engine = _usar_base_temporal(monkeypatch, tmp_path)
    migrar_mod.migrar()
    command.downgrade(migrar_mod.configuracion(), "base")
    assert set(inspect(engine).get_table_names()) <= {"alembic_version"}
