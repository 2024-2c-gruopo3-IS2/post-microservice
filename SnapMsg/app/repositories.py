import datetime
from typing import List
from bson import ObjectId
from .config import logger


class SnapRepository:
    def __init__(self, db):
        self.snaps_collection = db["twitsnaps"]
        self.likes_collection = db["likes"]
        self.favourites_collection = db["favourites"]
        self.snap_shares_collection = db["snap_shares"]

    def create_snap(self, email, message, is_private, hashtags, username):
        """
        Create a new snap.
        """
        new_snap = {
            "email": email,
            "username": username,
            "message": message,
            "created_at": datetime.datetime.now(),
            "is_private": is_private,
            "hashtags": hashtags,
            "likes": 0,
            "is_blocked": False
        }
        result = self.snaps_collection.insert_one(new_snap)
        new_snap["_id"] = str(result.inserted_id)
        logger.info(f"Snap created with id {new_snap['_id']}")
        return new_snap

    def get_snaps(self, email):
        """
        Fetch all snaps for a user.
        """
        snaps = list(self.snaps_collection.find({"email": email, "is_blocked": False}).sort("created_at", -1))
        for snap in snaps:
            snap["_id"] = str(snap["_id"])
        logger.info(f"Snaps retrieved for user {email}")
        return snaps
    
    def get_snap_by_id(self, snap_id):
        """
        Fetch a snap by its ID.
        """
        snap = self.snaps_collection.find_one({"_id": ObjectId(snap_id)})
        if snap and not snap["is_blocked"]:
            snap['id'] = str(snap.pop('_id'))
            logger.info(f"Snap with id {snap_id} retrieved")
        elif snap and snap["is_blocked"]:
            logger.info(f"Snap with id {snap_id} is blocked")
            snap = "Snap is blocked"
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
        snaps = list(self.snaps_collection.find({"hashtags": hashtag, "is_blocked": False}).sort("created_at", -1))
        for snap in snaps:
            snap["_id"] = str(snap["_id"])
        logger.info(f"Retrieved snaps with hashtag {hashtag}")
        return snaps
    
    def get_snaps_from_users(self, followed_users: List[str]):
        """
        obtains the snaps from the users followed by the user.
        """
        logger.info(f"Fetching snaps for followed users: {followed_users}")
        snaps = list(self.snaps_collection.find({"email": {"$in": followed_users}, "is_blocked": False}).sort("created_at", -1))
        print(snaps)
        for snap in snaps:
            snap["_id"] = str(snap["_id"])
        logger.info(f"Retrieved snaps from followed users")
        return snaps
    
    def like_snap(self, snap_id, user_email):
        """
        Like a snap.
        """
        snap = self.snaps_collection.find_one({"_id": ObjectId(snap_id)})
        if not snap or snap["is_blocked"]:
            return False
        
        result = self.likes_collection.insert_one({"snap_id": snap_id, "email": user_email})

        self.snaps_collection.update_one({"_id": ObjectId(snap_id)}, {"$inc": {"likes": 1}})

        return result.inserted_id
    
    def get_snap_likes(self, snap_id):
        """
        Get the emails of likes for snap.
        """
        likes = [x["email"] for x in list(self.likes_collection.find({"snap_id": snap_id}, {"email": 1, "_id": 0}))]
        return likes
    
    def unlike_snap(self, snap_id, user_email):
        """
        Unlike a snap.
        """
        snap = self.snaps_collection.find_one({"_id": ObjectId(snap_id)})
        if not snap or snap["is_blocked"]:
            return False
        
        result = self.likes_collection.delete_one({"snap_id": snap_id, "email": user_email})

        self.snaps_collection.update_one({"_id": ObjectId(snap_id)}, {"$inc": {"likes": -1}})

        return result.deleted_count
    
    def favourite_snap(self, snap_id, user_email):
        """
        Favourite a snap.
        """
        snap = self.snaps_collection.find_one({"_id": ObjectId(snap_id)})
        if not snap or snap["is_blocked"]:
            return False
        
        result = self.favourites_collection.insert_one({"snap_id": snap_id, "email": user_email})
        return result.inserted_id
    
    def get_snap_favourites(self, user_email):
        """
        Get the IDs of snaps favourited by user.
        """
        favourites = [x["snap_id"] for x in list(self.favourites_collection.find({"email": user_email}, {"snap_id": 1, "_id": 0}))]
        return favourites
    
    def unfavourite_snap(self, snap_id, user_email):
        """
        Unfavourite a snap.
        """
        snap = self.snaps_collection.find_one({"_id": ObjectId(snap_id)})
        if not snap or snap["is_blocked"]:
            return False
        
        result = self.favourites_collection.delete_one({"snap_id": snap_id, "email": user_email})
        return result.deleted_count
    
    def get_all_snap_favourites(self, user_email):
        """
        Get all the favourites for all snaps.
        """
        favourites = list(self.favourites_collection.find({"email": user_email}))
        for favourite in favourites:
            favourite["_id"] = str(favourite["_id"])
        return [x["snap_id"] for x in favourites]
    
    def get_all_snap_likes(self, user_email):
        """
        Get all the likes for all snaps.
        """
        likes = list(self.likes_collection.find({"email": user_email}))
        for like in likes:
            like["_id"] = str(like["_id"])
        return [x["snap_id"] for x in likes]
    
    def get_relevant_snaps(self, interests: List[str]):
        """
        Get snaps relevant to the user's interests.
        """
        interests = ["#" + x.lower() for x in interests]
        snaps = list(self.snaps_collection.find({"hashtags": {"$in": interests}, "is_blocked": False}).sort("created_at", -1))
        for snap in snaps:
            snap["_id"] = str(snap["_id"])
        return snaps
    
    def block_snap(self, snap_id, user_email):
        """
        Block a snap.
        """
        snap = self.snaps_collection.find_one({"_id": ObjectId(snap_id)})
        if not snap or snap["is_blocked"]:
            return False
        
        result = self.snaps_collection.update_one({"_id": ObjectId(snap_id)}, {"$set": {"is_blocked": True}})
        return result.modified_count
    
    def unblock_snap(self, snap_id, user_email):
        """
        Unblock a snap.
        """
        snap = self.snaps_collection.find_one({"_id": ObjectId(snap_id)})
        if not snap or not snap["is_blocked"]:
            return False
        
        result = self.snaps_collection.update_one({"_id": ObjectId(snap_id)}, {"$set": {"is_blocked": False}})
        return result.modified_count
    
    def get_snaps_unblocked(self, user_email):
        """
        Get all unblocked snaps.
        """
        snaps = list(self.snaps_collection.find({"is_blocked": False}).sort("created_at", -1))
        for snap in snaps:
            snap["_id"] = str(snap["_id"])
        return snaps
    
    def get_last_24_hours_snaps(self):
        """
        Get all snaps from the last 24 hours.
        """
        snaps = list(self.snaps_collection.find({"created_at": {"$gte": datetime.datetime.now() - datetime.timedelta(days=1)}}).sort("created_at", -1))
        for snap in snaps:
            snap["_id"] = str(snap["_id"])
        return snaps
    
    def snap_share(self, snap_id, user_email, username):
        """
        Share a snap.
        """
        snap = self.snaps_collection.find_one({"_id": ObjectId(snap_id)})
        if not snap or snap["is_blocked"]:
            return False
        
        result = self.snap_shares_collection.insert_one({"snap_id": snap_id, "email": user_email, "username": username, "created_at": datetime.datetime.now()})
        return result.inserted_id
    
    def get_snap_shares_by_email(self, user_email):
        """
        Get all snap shares.
        """
        shares = list(self.snap_shares_collection.find({"email": user_email}))
        for share in shares:
            share["_id"] = str(share["_id"])
        return shares


