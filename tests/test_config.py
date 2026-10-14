import pytest

from app.core.config import Settings

CLAVE_FUERTE = "x" * 48


def settings_con(**valores):
    # Settings lee el entorno al importar; una subclase permite probar otras combinaciones
    return type("SettingsPrueba", (Settings,), valores)()


def test_produccion_rechaza_clave_debil():
    # RNF-09
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        settings_con(environment="production", secret_key="change-me", seed_demo_data=False)


def test_produccion_rechaza_datos_de_prueba():
    # RNF-09
    with pytest.raises(RuntimeError, match="SEED_DEMO_DATA"):
        settings_con(environment="production", secret_key=CLAVE_FUERTE, seed_demo_data=True)


def test_produccion_arranca_con_configuracion_segura():
    assert settings_con(environment="production", secret_key=CLAVE_FUERTE, seed_demo_data=False)
