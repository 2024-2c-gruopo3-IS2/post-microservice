from dotenv import load_dotenv
from fastapi import HTTPException, Header
import requests
import os
from .config import logger

load_dotenv()


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
        logger.info(f"User email: {user_email}")
        return {"email": user_email, "token": token}
    else:
        raise HTTPException(status_code=401, detail="Invalid token")