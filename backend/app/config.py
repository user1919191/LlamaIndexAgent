from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    database_url: str = "mysql+pymysql://LlamaIndexAgent:pW8nrp22ARNWF6MA@49.235.161.81:3306/llamaindexagent?charset=utf8mb4"


    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 7
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
