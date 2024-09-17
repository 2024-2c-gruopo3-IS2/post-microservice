import datetime
from bson import ObjectId
from config import logger


class SnapRepository:
    def __init__(self, db):
        self.snaps_collection = db["twitsnaps"]

    def create_snap(self, email, message, privacy):
        new_snap = {
            "email": email,
            "message": message,
            "created_at": datetime.datetime.now(),
            "privacy": privacy,
        }
        result = self.snaps_collection.insert_one(new_snap)
        return str(result.inserted_id)

    def get_snaps(self, email):
        snaps = list(self.snaps_collection.find({"email": email}).sort("created_at", -1))
        for snap in snaps:
            snap["_id"] = str(snap["_id"])
        return snaps
    
    def get_snap_by_id(self, snap_id):
        snap = self.snaps_collection.find_one({"_id": ObjectId(snap_id)})
        return snap

    def delete_snap(self, snap_id):
        result = self.snaps_collection.delete_one({"_id": ObjectId(snap_id)})
        return result.deleted_count

    def update_snap(self, snap_id, update_data):
        update_data = update_data.dict()
        result = self.snaps_collection.update_one({"_id": ObjectId(snap_id)}, {"$set": update_data})
        return result.modified_count

    def get_user_snaps(self, user_id):
        return list(self.snaps_collection.find({"user_id": user_id}))

    def get_public_snaps(self):
        return list(self.snaps_collection.find({"privacy": "public"}))

