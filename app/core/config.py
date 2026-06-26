import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./telemedicina.db")
    secret_key: str = os.getenv("SECRET_KEY", "change-me")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    asterisk_webhook_token: str | None = os.getenv("ASTERISK_WEBHOOK_TOKEN")
    freepbx_db_host: str | None = os.getenv("FREEPBX_DB_HOST")
    freepbx_db_port: int = int(os.getenv("FREEPBX_DB_PORT", "3306"))
    freepbx_db_user: str | None = os.getenv("FREEPBX_DB_USER")
    freepbx_db_password: str | None = os.getenv("FREEPBX_DB_PASSWORD")
    freepbx_db_name: str = os.getenv("FREEPBX_DB_NAME", "asteriskcdrdb")
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "*").split(",")
        if origin.strip()
    ]

    @property
    def freepbx_database_url(self) -> str | None:
        if not all([self.freepbx_db_host, self.freepbx_db_user, self.freepbx_db_password]):
            return None
        return (
            f"mysql+pymysql://{self.freepbx_db_user}:{self.freepbx_db_password}"
            f"@{self.freepbx_db_host}:{self.freepbx_db_port}/{self.freepbx_db_name}"
        )


settings = Settings()
