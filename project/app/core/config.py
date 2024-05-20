from pydantic_settings import BaseSettings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
    class Config:
        env_file = ".env"

settings = Settings()

app = FastAPI()

# Разрешить запросы с указанных доменов
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    # Добавьте здесь другие домены, с которых вы отправляете запросы
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Лучше указать конкретные источники, чем * в продакшене
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)