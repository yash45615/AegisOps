
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AegisOps"
    environment: str = "development"
    database_url: str = "sqlite:///./aegisops.db"
    aegisops_api_key: str = "local-development-only-change-me"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
