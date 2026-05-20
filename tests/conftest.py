import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import room_manager, task_storage


@pytest.fixture(autouse=True)
def reset_state():
    task_storage.reset()
    room_manager.reset()
    yield
    task_storage.reset()
    room_manager.reset()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
