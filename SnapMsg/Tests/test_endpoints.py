from http.client import HTTPException
from fastapi.testclient import TestClient
import sys
import os
import pytest
import urllib.parse

from app.authentication import get_user_from_token
from app.db import db
from httpx import WSGITransport
import ddtrace


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app


@pytest.fixture(autouse=True)
def clear_database():
    ddtrace.config.mongodb["service"] = None
    db.twitsnaps.drop()
    yield
    db.twitsnaps.drop()

def mock_get_user_from_token(_token: str = None):
    return {"email": "mocked_email@example.com", "token": ""}

def mock_get_user_from_token_user_2(_token: str = None):
    return {"email": "mocked_email_2@example.com", "token": ""}

def mock_get_user_from_token_user_3(_token: str = None):
    return {"email": "mocked_email_3@example.com", "token": ""}

def mock_get_user_from_token_invalid(_token: str = None):
    raise HTTPException(status_code=401, detail="Invalid token")


app.dependency_overrides[get_user_from_token] = mock_get_user_from_token


transport = WSGITransport(app=app)
client = TestClient(app)

def test_create_snap():
    data = {"message": "Hello World!", "is_private": False}

    response = client.post("/snaps/", json=data, headers={"Authorization": "Bearer mocktoken"})
    assert response.status_code == 201
    assert response.json()["data"]["message"] == "Hello World!"

def test_get_snaps():
    client.post("/snaps/", json={"message": "Test snap", "is_private": False})
    client.post("/snaps/", json={"message": "Another test snap", "is_private": False})

    response = client.get("/snaps/")
    assert response.status_code == 200
    data = response.json()
    print("Data: ", data)
    assert len(data["data"]) == 2
    assert data["data"][0]["message"] == "Another test snap"
    assert data["data"][1]["message"] == "Test snap"

def test_create_snap_message_too_long():
    long_message = "x" * 281
    response = client.post("/snaps", json={"message": long_message, "is_private": False}, headers={"Authorization": "Bearer mocktoken"})
    assert response.status_code == 400
    data = response.json()
    assert data["type"] == "about:blank"
    assert data["title"] == "Bad Request Error"
    assert data["detail"] == "Message exceeds 280 characters."
    
def test_delete_snap():
    response = client.post("/snaps", json={"message": "Hello World!", "is_private": False}, headers={"Authorization": "Bearer mocktoken"})
    snap_id = response.json()["data"]["id"]

    response = client.delete(f"/snaps/{snap_id}", headers={"Authorization": "Bearer mocktoken"})
    assert response.status_code == 204


def test_delete_snap_not_found():
    invalid_uuid = "66f9a1c9dcf674a1a9c6e2f0"
    response = client.delete(f"/snaps/{invalid_uuid}", headers={"Authorization": "Bearer mocktoken"})
    assert response.status_code == 404
    data = response.json()
    assert data["type"] == "about:blank"
    assert data["title"] == "Snap Not Found"
    assert data["detail"] == f"Snap with ID {invalid_uuid} not found."
    

def test_get_all_snaps():
  
    client.post("/snaps/", json={"message": "Snap 1", "is_private": False}, headers={"Authorization": "Bearer mocktoken"})
    client.post("/snaps/", json={"message": "Snap 2", "is_private": False}, headers={"Authorization": "Bearer mocktoken"})
    client.post("/snaps/", json={"message": "Snap 3", "is_private": False}, headers={"Authorization": "Bearer mocktoken"})

    
    response = client.get("/snaps/all-snaps", headers={"Authorization": "Bearer mocktoken"})
    
    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]) == 3
    assert data["data"][0]["message"] == "Snap 3"
    assert data["data"][1]["message"] == "Snap 2"
    assert data["data"][2]["message"] == "Snap 1"


def test_get_all_snaps_no_snaps():
    
    response = client.get("/snaps/all-snaps", headers={"Authorization ": "Bearer mocktoken"})
    assert response.status_code == 404
    data = response.json()
    assert data["type"] == "about:blank"
    assert data["title"] == "Snap Not Found"


def test_create_snap_with_hashtags():
    data = {"message": "Hello World! #test #snap", "is_private": False}

    response = client.post("/snaps/", json=data, headers={"Authorization": "Bearer mocktoken"})
    assert response.status_code == 201
    response_data = response.json()["data"]
    assert response_data["message"] == "Hello World! #test #snap"
    assert response_data["hashtags"] == ["#test", "#snap"]


def test_update_snap_with_hashtags():
   
    response = client.post("/snaps/", json={"message": "Initial Message", "is_private": False}, headers={"Authorization": "Bearer mocktoken"})
    snap_id = response.json()["data"]["id"]

    updated_data = {"message": "Updated Message #updated", "is_private": False}
    response = client.put(f"/snaps/{snap_id}", json=updated_data, headers={"Authorization": "Bearer mocktoken"})
    
    assert response.status_code == 200
    response_data = response.json()["data"]
    assert response_data["message"] == "Updated Message #updated"
    assert response_data["hashtags"] == ["#updated"]


def test_search_snaps_by_hashtag():
    
    client.post("/snaps/", json={"message": "Snap with #fun", "is_private": False}, headers={"Authorization": "Bearer mocktoken"})
    client.post("/snaps/", json={"message": "Another snap with #fun", "is_private": False}, headers={"Authorization": "Bearer mocktoken"})
    client.post("/snaps/", json={"message": "Snap with #serious", "is_private": False}, headers={"Authorization": "Bearer mocktoken"})

    hashtag = "#fun"
    encoded_hashtag = urllib.parse.quote(hashtag)

    response = client.get(f"/snaps/by-hashtag?hashtag={encoded_hashtag}", headers={"Authorization": "Bearer mocktoken"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    assert data[0]["message"] == "Another snap with #fun"
    assert data[1]["message"] == "Snap with #fun"


def test_search_snaps_by_non_existing_hashtag():

    hashtag = "#nonexistent"
    encoded_hashtag = urllib.parse.quote(hashtag)
    
    response = client.get(f"/snaps/by-hashtag?hashtag={encoded_hashtag}", headers={"Authorization": "Bearer mocktoken"})
    assert response.status_code == 404
    data = response.json()
    assert data["type"] == "about:blank"
    assert data["title"] == "Snap Not Found"

def test_get_snap_by_id():
    response1 = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization": "Bearer mocktoken"})

    response = client.get(f"/snaps/{response1.json()['data']['id']}", headers={"Authorization": "Bearer mocktoken"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["message"] == "Snap"


