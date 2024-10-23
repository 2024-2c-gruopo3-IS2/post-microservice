from http.client import HTTPException
from fastapi.testclient import TestClient
import sys
import os
import pytest
import urllib.parse
from app.authentication import get_user_from_token
from app.db import db
from httpx import WSGITransport


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app

@pytest.fixture(autouse=True)
def clear_database():
    db.twitsnaps.drop()
    yield
    db.twitsnaps.drop()

def mock_get_user_from_token(_token: str = None):
    return {"email": "mocked_email@example.com", "token": "", "username": "johndoe"}

def mock_get_user_from_token_user_2(_token: str = None):
    return {"email": "mocked_email_2@example.com", "token": "", "username": "janedoe"}

def mock_get_user_from_token_user_3(_token: str = None):
    return {"email": "mocked_email_3@example.com", "token": "", "username": "pepito"}

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
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 0
   


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

def test_like_snap():
    response = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization": "Bearer mock"})

    response_like = client.post(f"/snaps/like?snap_id={response.json()['data']['id']}", headers={"Authorization": "Bearer mocktoken"})

    assert response_like.status_code == 200
    assert response_like.json() == {"detail": "Snap liked successfully"}

def test_like_snap_already_liked():
    response = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization": "Bearer mock"})

    client.post(f"/snaps/like?snap_id={response.json()['data']['id']}", headers={"Authorization": "Bearer mocktoken"})

    response_like2 = client.post(f"/snaps/like?snap_id={response.json()['data']['id']}", headers={"Authorization": "Bearer mocktoken"})


    assert response_like2.status_code == 400
    assert response_like2.json()["detail"] == "You have already liked this snap."

def test_unlike_snap():
    response = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization": "Bearer mock"})

    client.post(f"/snaps/like?snap_id={response.json()['data']['id']}", headers={"Authorization": "Bearer mock"})

    response_unlike = client.post(f"/snaps/unlike?snap_id={response.json()['data']['id']}", headers={"Autorization":"Bearer mocktoken"})

    assert response_unlike.status_code == 200
    assert response_unlike.json() == {"detail":"Snap unliked successfully"}

def test_unlike_snap_not_liked():
    response = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization": "Bearer mock"})

    response_unlike = client.post(f"/snaps/unlike?snap_id={response.json()['data']['id']}", headers={"Authorization": "Bearer mock"})

    assert response_unlike.status_code == 400
    assert response_unlike.json()['detail'] == "You have not liked this snap."

def test_favourite_snap():
    response = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization": "Bearer mock"})

    response_favourite = client.post(f"/snaps/favourite?snap_id={response.json()['data']['id']}", headers={"Authorization": "Bearer mock"})

    assert response_favourite.status_code == 200
    assert response_favourite.json() == {"detail":"Snap favourited successfully"}

def test_favourite_snap_already_favourited():
    response = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization": "Bearer mock"})
    client.post(f"/snaps/favourite?snap_id={response.json()['data']['id']}", headers={"Authorization": "Bearer mock"})
    response_favourite2 = client.post(f"/snaps/favourite?snap_id={response.json()['data']['id']}", headers={"Authorization": "Bearer mock"})

    assert response_favourite2.status_code == 400
    assert response_favourite2.json()['detail'] == "You have already favourited this snap."

def test_unfavourite_snap():
    response = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization": "Bearer mock"})
    client.post(f"/snaps/favourite?snap_id={response.json()['data']['id']}", headers={"Authorization": "Bearer mock"})
    response_unfavourite = client.post(f"/snaps/unfavourite?snap_id={response.json()['data']['id']}", headers={"Authorization": "Bearer mock"})
    assert response_unfavourite.status_code == 200
    assert response_unfavourite.json() == {"detail":"Snap unfavourited successfully"}

def test_unfavourite_snap_not_favourited():
    response = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization": "Bearer mock"})
    response_unfavourite = client.post(f"/snaps/unfavourite?snap_id={response.json()['data']['id']}", headers={"Authorization": "Bearer mock"})
    assert response_unfavourite.status_code == 400
    assert response_unfavourite.json()['detail'] == "You have not favourited this snap."

def test_get_favourite_snaps():
    response = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization ": "Bearer mock"})
    client.post(f"/snaps/favourite?snap_id={response.json()['data']['id']}", headers={"Authorization ": "Bearer mock"})
    response_favourite = client.get("/snaps/favourites/", headers={"Authorization ": "Bearer mock"})
    assert response_favourite.status_code == 200
    data = response_favourite.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["message"] == "Snap"

def test_get_liked_snaps():
    response = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization ": "Bearer mock"})
    client.post(f"/snaps/like?snap_id={response.json()['data']['id']}", headers={" Authorization ": "Bearer mock"})
    response_liked = client.get("/snaps/liked/", headers = {"Authorization ": "Bearer mock"})
    assert response_liked.status_code == 200
    data = response_liked.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["message"] == "Snap"


def test_block_snap():
    response = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization ": "Bearer mock"})
    snap_id = response.json()["data"]["id"]
    response_block = client.post(f"/snaps/block?snap_id={snap_id}", headers={" Authorization ": "Bearer mock"})
    assert response_block.status_code == 200
    assert response_block.json() == {"detail":"Snap blocked successfully"}

def test_block_snap_already_blocked():
    response = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization ": "Bearer mock"})
    snap_id = response.json()["data"]["id"]
    client.post(f"/snaps/block?snap_id={snap_id}", headers = {"Authorization ": "Bearer mock"})
    response_block2 = client.post(f"/snaps/block?snap_id={snap_id}", headers = {"Authorization ": "Bearer mock"})
    assert response_block2.status_code == 400
    assert response_block2.json()["detail"] == "Snap already blocked."

def test_get_snaps_blocked():
    client.post("/snaps/", json={"message": "Test snap", "is_private": False})
    response_post = client.post("/snaps/", json={"message": "Another test snap", "is_private": False})
    snap_id = response_post.json()["data"]["id"]
    client.post(f"/snaps/block?snap_id={snap_id}", headers = {"Authorization ": "Bearer mock"})

    response = client.get("/snaps/")
    assert response.status_code == 200
    data = response.json()
    print("Data: ", data)
    assert len(data["data"]) == 1
    assert data["data"][0]["message"] == "Test snap"

def test_unblock_snap():
    response = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization ": "Bearer mock"})
    snap_id = response.json()["data"]["id"]
    client.post(f"/snaps/block?snap_id={snap_id}", headers = {"Authorization ": "Bearer mock"})
    response_unblock = client.post(f"/snaps/unblock?snap_id={snap_id}", headers = {"Authorization ": "Bearer mock"})
    assert response_unblock.status_code == 200
    assert response_unblock.json() == {"detail":"Snap unblocked successfully"}

def test_unblock_snap_not_blocked():
    response = client.post("/snaps/", json={"message": "Snap", "is_private": False}, headers={"Authorization ": "Bearer mock"})
    snap_id = response.json()["data"]["id"]
    response_unblock = client.post(f"/snaps/unblock?snap_id={snap_id}", headers = {"Authorization ": "Bearer mock"})
    assert response_unblock.status_code == 400
    assert response_unblock.json()["detail"] == "Snap already unblocked."

def test_get_snaps_unblocked():
    client.post("/snaps/", json={"message": "Test snap", "is_private": False}, headers={"Authorization ": "Bearer mock"})
    response_post = client.post("/snaps/", json={"message": "Another test snap", "is_private": False}, headers={" Authorization ": "Bearer mock"})
    snap_id = response_post.json()["data"]["id"]
    client.post(f"/snaps/block?snap_id={snap_id}", headers = {"Authorization ": "Bearer mock"})

    response = client.get("/snaps/unblocked/", headers={"Authorization ": "Bearer mock"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["message"] == "Test snap"
   
