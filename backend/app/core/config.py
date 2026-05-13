from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Pramaan-X Intelligent C2 OS"
    database_url: str = "sqlite:///./praamanx_dev.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    telemetry_fresh_seconds: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_prefix="PRAAMANX_")


settings = Settings()
