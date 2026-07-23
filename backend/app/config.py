from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongo_uri: str = ""
    mongo_db_name: str = "reel_reality_check"
    storage_dir: str = "./storage"
    whisper_model_size: str = "base"
    gemini_api_key: str = ""


settings = Settings()
