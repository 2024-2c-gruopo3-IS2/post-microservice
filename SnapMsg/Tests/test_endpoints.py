from fastapi.testclient import TestClient
import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app
from app.models import Base
from app.config import engine

os.environ["ENVIRONMENT"] = "testing"

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_snap():
    response = client.post("/snaps", json={"message": "Hello World!"})
    assert response.status_code == 201
    data = response.json()
    assert "data" in data
    assert "id" in data["data"]
    assert data["data"]["message"] == "Hello World!"
    
def test_get_snaps():

    client.post("/snaps", json={"message": "Test snap"})
    client.post("/snaps", json={"message": "Another test snap"})

    response = client.get("/snaps")
    assert response.status_code == 200
    data = response.json()
    assert "data" in response.json()
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 3
    assert data["data"][0]["message"] == "Another test snap"
    assert data["data"][1]["message"] == "Test snap"
    assert data["data"][2]["message"] == "Hello World!"


def test_create_snap_message_too_long():
    long_message = "x" * 281
    response = client.post("/snaps", json={"message": long_message})
    assert response.status_code == 400
    data = response.json()
    assert data["type"] == "about:blank"
    assert data["title"] == "Bad Request Error"
    assert data["detail"] == "Message must be 280 characters or less"
      

def test_get_snap():
    
    response = client.post("/snaps", json={"message": "Hello World!"})
    snap_id = response.json()["data"]["id"]

    response = client.get(f"/snaps/{snap_id}")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["id"] == snap_id
    assert data["data"]["message"] == "Hello World!"

def test_get_snap_not_found():
    invalid_uuid = "12345678-1234-5678-1234-567812345678"
    response = client.get(f"/snaps/{invalid_uuid}")
    assert response.status_code == 404
    data = response.json()
    assert data["type"] == "about:blank"
    assert data["title"] == "Snap Not Found"
    assert data["detail"] == f"The snap with ID {invalid_uuid} was not found."
    
def test_delete_snap():
    response = client.post("/snaps", json={"message": "Hello World!"})
    snap_id = response.json()["data"]["id"]

    response = client.delete(f"/snaps/{snap_id}")
    assert response.status_code == 204

    response = client.get(f"/snaps/{snap_id}")
    assert response.status_code == 404


def test_delete_snap_not_found():
    invalid_uuid = "12345678-1234-5678-1234-567812345678"
    response = client.delete(f"/snaps/{invalid_uuid}")
    assert response.status_code == 404
    data = response.json()
    assert data["type"] == "about:blank"
    assert data["title"] == "Snap Not Found"
    assert data["detail"] == f"The snap with ID {invalid_uuid} was not found."


def test_create_snap_blank_message():
    response = client.post("/snaps", json={"message": ""})
    assert response.status_code == 201
    data = response.json()
    assert "data" in data
    assert "id" in data["data"]
    assert data["data"]["message"] == ""
    

