from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/eve_healthcare"
    SECRET_KEY: str = "change-this-secret-key-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    PROJECT_NAME: str = "EVE Healthcare API"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
