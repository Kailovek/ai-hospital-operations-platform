from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    settings = Settings(
        app_env="demo",
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        llm_provider="mock",
    )
    with TestClient(create_app(settings)) as test_client:
        yield test_client
