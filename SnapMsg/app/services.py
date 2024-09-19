import logging
from fastapi import HTTPException
import requests
from schemas import SnapUpdate
from repositories import SnapRepository
from pymongo.database import Database

logger = logging.getLogger(__name__)
class SnapService:
    def __init__(self, snap_repository: SnapRepository, auth_service_url: str):
        self.snap_repository = snap_repository
        self.auth_service_url = auth_service_url
    
    def get_user_email_from_token(self, token: str) -> str:
        logger.info(f"Getting user email from token {token}")
        response = requests.get(
            self.auth_service_url + "/auth/get-email-from-token",
            headers={"Content-Type": "application/json"},
            json={"token": token}
        )
        if response.status_code == 200:
            logger.info(f"User email: {response.json().get('email')}")
            return response.json().get("email")
        raise HTTPException(status_code=401, detail="Invalid token")

    def create_snap(self, db: Database, token: str, message: str, is_private: str):
        
        email = self.get_user_email_from_token(token)

        return self.snap_repository.create_snap(email, message, is_private)

    def get_snaps(self, db: Database, token: str):
        
        email = self.get_user_email_from_token(token)

        return self.snap_repository.get_snaps(email)

    def get_snap_by_id(self, db: Database, snap_id: str):
        snap = self.snap_repository.get_snap_by_id(snap_id)
        if not snap:
            raise HTTPException(status_code=404, detail="Snap not found.")
        return snap

    def delete_snap(self, db: Database, snap_id: str, token: str):

        email = self.get_user_email_from_token(token)

        snap = self.snap_repository.get_snap_by_id(snap_id)

        if snap["email"] != email:
            raise HTTPException(status_code=403, detail="Not authorized to delete this snap.")
        
        return self.snap_repository.delete_snap(snap_id)

    def update_snap(self, db: Database, token: str,  snap_id: str, snap_update: SnapUpdate):
        if len(snap_update.message) > 280:
            raise HTTPException(status_code=400, detail="Message exceeds the allowed length.")
        
        email = self.get_user_email_from_token(token)

        snap = self.snap_repository.get_snap_by_id(snap_id)

        if snap["email"] != email:
            raise HTTPException(status_code=403, detail="Not authorized to update this snap.")
        
        return self.snap_repository.update_snap(snap_id, snap_update)

    def get_user_snaps(self, db: Database, user_id: str):
        return self.snap_repository.get_user_snaps(user_id)

    def get_public_snaps(self, db: Database):
        return self.snap_repository.get_public_snaps()

