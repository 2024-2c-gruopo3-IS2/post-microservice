from dotenv import load_dotenv
from fastapi import HTTPException, Header
import requests
import os

from .users import PROFILE_SERVICE_URL
from .config import logger

load_dotenv()

def get_profile_by_email(email: str):
    """
    Get a user profile by email.
    """
    logger.info(f"Getting profile by email {email}")
    response = requests.get(
        PROFILE_SERVICE_URL + f'/profiles/by-email?email={email}',
        headers={"accept": "application/json"}
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Profile not found.")
    profile = response.json()
    return profile


AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")

def get_user_from_token(token: str = Header(None)):
    """
    This function gets the user from the token and keeps the token for further use.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Token missing")

    logger.info(f"Getting user email from token {token}")
    response = requests.get(
        AUTH_SERVICE_URL + "/auth/get-email-from-token",
        headers={"Content-Type": "application/json"},
        json={"token": token}
    )

    if response.status_code == 200:
        user_email = response.json().get("email")

        username = get_profile_by_email(user_email)["username"]

        logger.info(f"User email: {user_email}")
        return {"email": user_email, "token": token, "username": username}
    else:
        raise HTTPException(status_code=401, detail="Invalid token")