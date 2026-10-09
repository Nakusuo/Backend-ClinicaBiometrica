import os
import secrets
import warnings

from dotenv import load_dotenv

load_dotenv()

# Claves de ejemplo que aparecen en la documentación y nunca deben usarse de verdad
CLAVES_INSEGURAS = {
    "",
    "change-me",
    "cambia-esto-por-una-clave-larga-y-secreta",
    "otra_clave_larga_y_secreta",
}


def _bool(nombre: str, por_defecto: str) -> bool:
    return os.getenv(nombre, por_defecto).strip().lower() in ("1", "true", "yes", "si", "sí")


class Settings:
    environment: str = os.getenv("ENVIRONMENT", "development").strip().lower()
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./telemedicina.db")
    secret_key: str = os.getenv("SECRET_KEY", "")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    asterisk_webhook_token: str | None = os.getenv("ASTERISK_WEBHOOK_TOKEN") or None
    freepbx_db_host: str | None = os.getenv("FREEPBX_DB_HOST")
    freepbx_db_port: int = int(os.getenv("FREEPBX_DB_PORT", "3306"))
    freepbx_db_user: str | None = os.getenv("FREEPBX_DB_USER")
    freepbx_db_password: str | None = os.getenv("FREEPBX_DB_PASSWORD")
    freepbx_db_name: str = os.getenv("FREEPBX_DB_NAME", "asteriskcdrdb")
    # Datos de prueba (médico y paciente demo). Nunca activarlo en producción.
    seed_demo_data: bool = _bool("SEED_DEMO_DATA", "false")
    # Los médicos que se registran solos quedan inactivos hasta que otro médico los active
    doctor_requires_approval: bool = _bool("DOCTOR_REQUIRES_APPROVAL", "true")
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",")
        if origin.strip()
    ]

    def __init__(self):
        if self.secret_key in CLAVES_INSEGURAS or len(self.secret_key) < 32:
            if self.environment == "production":
                raise RuntimeError(
                    "SECRET_KEY no está definida o es insegura. Genera una con: "
                    "python -c \"import secrets; print(secrets.token_urlsafe(48))\""
                )
            warnings.warn(
                "SECRET_KEY insegura: se usa una clave aleatoria temporal. "
                "Las sesiones se perderán al reiniciar el servidor.",
                stacklevel=2,
            )
            self.secret_key = secrets.token_urlsafe(48)

        if self.environment == "production" and self.seed_demo_data:
            raise RuntimeError("SEED_DEMO_DATA no puede estar activo en producción.")

    @property
    def freepbx_database_url(self) -> str | None:
        if not all([self.freepbx_db_host, self.freepbx_db_user, self.freepbx_db_password]):
            return None
        return (
            f"mysql+pymysql://{self.freepbx_db_user}:{self.freepbx_db_password}"
            f"@{self.freepbx_db_host}:{self.freepbx_db_port}/{self.freepbx_db_name}"
        )


settings = Settings()
