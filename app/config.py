from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://studygo:supersecret@localhost:5432/studygo"
    JWT_SECRET: str = "dev-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24*7
    CORS_ORIGIN: str = "*"
    BASE_URL: str = "http://localhost:8000"
    UPLOAD_DIR: str = "./uploads"

    class Config:
        env_file = ".env"

settings = Settings()
