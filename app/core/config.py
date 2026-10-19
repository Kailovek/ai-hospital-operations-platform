from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "ai-hospital-operations-platform"
    app_env: Literal["demo", "full"] = "demo"
    app_host: str = "127.0.0.1"
    app_port: int = Field(default=8101, ge=1, le=65535)
    database_url: str = "sqlite:///./data/hospital_demo.db"
    llm_provider: Literal["mock", "deepseek", "ollama", "vllm"] = "mock"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    ollama_base_url: str = "http://127.0.0.1:11434"
    vllm_base_url: str = "http://127.0.0.1:8000/v1"
    redis_url: str = ""
    milvus_uri: str = ""
    data_dir: Path = Path("data")

    @model_validator(mode="after")
    def validate_runtime_mode(self) -> "Settings":
        if self.app_env == "demo" and self.llm_provider != "mock":
            raise ValueError("Demo mode requires LLM_PROVIDER=mock")
        if self.llm_provider == "deepseek" and not self.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY is required for the DeepSeek provider")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
