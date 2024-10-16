from dotenv import load_dotenv
from fastapi import HTTPException, Header
import requests
import os
from .config import logger

load_dotenv()

PROFILE_SERVICE_URL = os.getenv("PROFILE_SERVICE_URL")

def get_username_from_token(token: str = Header(None)):
    """
    This function gets the username from the token and keeps the token for further use.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token missing")

    logger.info(f"Getting username from token {token}")
    response = requests.get(
        PROFILE_SERVICE_URL + "/profiles/",
        headers={"Content-Type": "application/json", "token": token}
    )

    if response.status_code == 200:
        username = response.json().get("username")
        logger.info(f"Username: {username}")
        return username
    else:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_followed_users(token: str, username: str):
    """
    Obtain the users followed by the current user, using the token for authentication.
    """
    logger.info(f"Getting followed users")
    response = requests.get(
        PROFILE_SERVICE_URL + f'/profiles/followed-emails?username={username}',
        headers={
            "accept": "application/json",
            "token": token
        }
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error fetching followed users.")
    followed_users = response.json()
    return followed_users

def get_profile_by_username(username: str):
    """
    Get a user profile by username.
    """
    logger.info(f"Getting profile by username {username}")
    response = requests.get(
        PROFILE_SERVICE_URL + f'/profiles/by-username?username={username}',
        headers={"accept": "application/json"}
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Profile not found.")
    profile = response.json()
    return profile