from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    APP_ENV: str = "prod"
    ECHO: bool = False

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_BROKER_DB: int = 0
    REDIS_RESULT_DB: int = 1

    @property
    def async_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def sync_db_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def redis_url(self, db: int) -> str:
        return (
            f"redis://:{self.REDIS_PASSWORD}"
            f"@{self.REDIS_HOST}:{self.REDIS_PORT}/{db}"
        )

    @property
    def celery_broker_url(self) -> str:
        return self.redis_url(self.REDIS_BROKER_DB)

    @property
    def celery_result_backend_url(self) -> str:
        return self.redis_url(self.REDIS_RESULT_DB)

    # Pydantic автоматически читает только этот .env файл. Значения из .env.dev
    # загружаются командами Makefile как реальные переменные окружения.
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )


settings = Settings()  # type: ignore[call-arg]
