from dotenv import load_dotenv
from fastapi import HTTPException, Header
import requests
import logging
import os

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")

def get_user_from_token(token: str = Header(None)) -> str:
        """
        This function gets the user from the token.
        """
        logger.info(f"Getting user email from token {token}")
        response = requests.get(
            AUTH_SERVICE_URL + "/auth/get-email-from-token",
            headers={"Content-Type": "application/json"},
            json={"token": token}
        )
        if response.status_code == 200:
            logger.info(f"User email: {response.json().get('email')}")
            return response.json().get("email")
        raise HTTPException(status_code=401, detail="Invalid token")