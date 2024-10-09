import datetime
from typing import List
from bson import ObjectId
from .config import logger


class SnapRepository:
    def __init__(self, db):
        self.snaps_collection = db["twitsnaps"]

    def create_snap(self, email, message, is_private, hashtags):
        """
        Create a new snap.
        """
        new_snap = {
            "email": email,
            "message": message,
            "created_at": datetime.datetime.now(),
            "is_private": is_private,
            "hashtags": hashtags
        }
        result = self.snaps_collection.insert_one(new_snap)
        new_snap["_id"] = str(result.inserted_id)
        logger.info(f"Snap created with id {new_snap['_id']}")
        return new_snap

    def get_snaps(self, email):
        """
        Fetch all snaps for a user.
        """
        snaps = list(self.snaps_collection.find({"email": email}).sort("created_at", -1))
        for snap in snaps:
            snap["_id"] = str(snap["_id"])
        logger.info(f"Snaps retrieved for user {email}")
        return snaps
    
    def get_snap_by_id(self, snap_id):
        """
        Fetch a snap by its ID.
        """
        snap = self.snaps_collection.find_one({"_id": ObjectId(snap_id)})
        if snap:
            snap['id'] = str(snap.pop('_id'))
        logger.info(f"Snap with id {snap_id} retrieved")
        return snap

    def delete_snap(self, snap_id):
        """
        Delete a snap.
        """
        result = self.snaps_collection.delete_one({"_id": ObjectId(snap_id)})
        logger.info(f"Snap with id {snap_id} deleted")
        return result.deleted_count

    def update_snap(self, snap_id, update_data):
        """
        Update a snap.
        """
        update_data = update_data.dict()
        result = self.snaps_collection.update_one({"_id": ObjectId(snap_id)}, {"$set": update_data})
        logger.info(f"Snap with id {snap_id} updated")
        return result.modified_count

    def get_user_snaps(self, user_id):
        logger.info(f"Getting snaps for user {user_id}")
        return list(self.snaps_collection.find({"user_id": user_id}))

    def get_public_snaps(self):
        logger.info(f"Getting public snaps")
        return list(self.snaps_collection.find({"is_private": False}))
    
    def get_all_snaps(self):
        """
        Fetch all public and private snaps from the database.
        """
        snaps = list(self.snaps_collection.find().sort("created_at", -1))
        for snap in snaps:
            snap["_id"] = str(snap["_id"])
        logger.info(f"Retrieved all snaps")
        return snaps
    
    def search_snaps_by_hashtag(self, hashtag):
        """
        Search for snaps that contain a specific hashtag.
        """
        snaps = list(self.snaps_collection.find({"hashtags": hashtag}).sort("created_at", -1))
        for snap in snaps:
            snap["_id"] = str(snap["_id"])
        logger.info(f"Retrieved snaps with hashtag {hashtag}")
        return snaps
    
    def get_snaps_from_users(self, followed_users: List[str]):
        """
        obtains the snaps from the users followed by the user.
        """
        logger.info(f"Fetching snaps for followed users: {followed_users}")
        snaps = list(self.snaps_collection.find({"email": {"$in": followed_users}}).sort("created_at", -1))
        print(snaps)
        for snap in snaps:
            snap["_id"] = str(snap["_id"])
        logger.info(f"Retrieved snaps from followed users")
        return snaps

