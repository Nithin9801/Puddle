from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL : str
    DOMAIN : str 
    CLIENT_ID : str
    CLIENT_SECRET : str
    JWT_SECRET : str
    JWT_ALGORITHM : str
    REDIS_URL : str

    model_config = SettingsConfigDict(env_file=".env",extra="ignore")

Config = Settings()