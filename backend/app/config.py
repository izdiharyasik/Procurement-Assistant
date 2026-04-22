from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Procurement AI Suite"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    max_chunk_chars: int = 3200
    storage_path: str = "backend/storage"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
