from fastapi import HTTPException
from .repositories import SnapRepository
from pymongo.database import Database

class SnapService:
    def __init__(self, snap_repository: SnapRepository):
        self.snap_repository = snap_repository

    def create_snap(self, db: Database, user_id: str, message: str, privacy: str):
        if len(message) > 280:
            raise ValueError("Message exceeds the maximum allowed length.")
        return self.snap_repository.create_snap(user_id, message, privacy)

    def get_snaps(self, db: Database):
        return self.snap_repository.get_snaps()

    def get_snap_by_id(self, db: Database, snap_id: str):
        snap = self.snap_repository.get_snap_by_id(snap_id)
        if not snap:
            raise HTTPException(status_code=404, detail="Snap not found.")
        return snap

    def delete_snap(self, db: Database, snap_id: str):
        return self.snap_repository.delete_snap(snap_id)

    def update_snap(self, db: Database, snap_id: str, message: str, tags: list):
        if len(message) > 280:
            raise HTTPException(status_code=400, detail="Message exceeds the allowed length.")
        return self.snap_repository.update_snap(snap_id, message, tags)

    def get_user_snaps(self, db: Database, user_id: str):
        return self.snap_repository.get_user_snaps(user_id)

    def get_public_snaps(self, db: Database):
        return self.snap_repository.get_public_snaps()

