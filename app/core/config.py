"""配置"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = "sk-xxx"
    openai_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/ai_study"
    chunk_size: int = 500
    chunk_overlap: int = 80
    top_k: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
