import logging
from fastapi import HTTPException
from .schemas import SnapUpdate
from .repositories import SnapRepository
from pymongo.database import Database

logger = logging.getLogger(__name__)
class SnapService:
    def __init__(self, snap_repository: SnapRepository, auth_service_url: str):
        self.snap_repository = snap_repository
        self.auth_service_url = auth_service_url

    def create_snap(self, db: Database, user_email: str, message: str, is_private: str):

        return self.snap_repository.create_snap(user_email, message, is_private)

    def get_snaps(self, db: Database, user_email: str):

        return self.snap_repository.get_snaps(user_email)

    def get_snap_by_id(self, db: Database, snap_id: str):
        snap = self.snap_repository.get_snap_by_id(snap_id)
        if not snap:
            raise HTTPException(status_code=404, detail="Snap not found.")
        return snap

    def delete_snap(self, db: Database, snap_id: str, user_email: str):

        snap = self.snap_repository.get_snap_by_id(snap_id)

        if not snap:
            raise HTTPException(status_code=404, detail=f"Snap with ID {snap_id} not found.")

        if snap["email"] != user_email:
            raise HTTPException(status_code=403, detail="Not authorized to delete this snap.")
        
        return self.snap_repository.delete_snap(snap_id)

    def update_snap(self, db: Database, user_email: str,  snap_id: str, snap_update: SnapUpdate):
        if len(snap_update.message) > 280:
            raise HTTPException(status_code=400, detail="Message exceeds the allowed length.")

        snap = self.snap_repository.get_snap_by_id(snap_id)

        if snap["email"] != user_email:
            raise HTTPException(status_code=403, detail="Not authorized to update this snap.")
        
        return self.snap_repository.update_snap(snap_id, snap_update)

