from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MyET AI"
    api_prefix: str = "/api"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    environment: str = "development"
    data_path: str = "shared/sample_data/articles.json"
    profile_store_path: str = "shared/sample_data/user_profile.json"
    portfolio_path: str = "shared/sample_data/portfolio.csv"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
