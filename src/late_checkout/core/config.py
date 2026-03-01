from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Default to sqlite in memory for testing without .env
    DATABASE_URL: str = "sqlite:///:memory:"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
