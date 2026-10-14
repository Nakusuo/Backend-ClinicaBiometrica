"""Lleva la base de datos a la última migración.

Uso: python -m app.db.migrar   (o lo hace la API sola al arrancar si AUTO_MIGRATE=true)

Las bases creadas antes de usar Alembic (con Base.metadata.create_all) ya tienen las tablas
pero no la tabla alembic_version. A esas se les marca la migración inicial como aplicada
(stamp) en lugar de intentar crear las tablas otra vez.
"""
import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.db.database import engine

# Migración inicial: equivale al esquema que generaba create_all
REVISION_BASE = "0001_esquema_inicial"

RAIZ = Path(__file__).resolve().parents[2]
logger = logging.getLogger(__name__)


def configuracion() -> Config:
    cfg = Config(str(RAIZ / "alembic.ini"))
    cfg.set_main_option("script_location", str(RAIZ / "migrations"))
    # No reconfigurar el logging de la app cuando se llama desde la API
    cfg.attributes["configure_logger"] = False
    return cfg


def migrar() -> None:
    cfg = configuracion()
    tablas = set(inspect(engine).get_table_names())
    if "alembic_version" not in tablas and "doctores" in tablas:
        logger.warning("Base creada sin Alembic: se marca %s como aplicada", REVISION_BASE)
        command.stamp(cfg, REVISION_BASE)
    command.upgrade(cfg, "head")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    migrar()
