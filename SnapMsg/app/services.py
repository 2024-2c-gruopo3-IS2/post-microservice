import logging
import re
from typing import List
from fastapi import HTTPException

from .constants import MAX_MESSAGE_LENGTH
from .schemas import SnapUpdate
from .repositories import SnapRepository
from pymongo.database import Database
from .config import logger



def extract_hashtags(message: str) -> List[str]:
    """
    Extract hashtags from the message, including the '#' symbol.
    """
    return re.findall(r"(#\w+)", message)


class SnapService:
    def __init__(self, snap_repository: SnapRepository, auth_service_url: str):
        self.snap_repository = snap_repository
        self.auth_service_url = auth_service_url
    
    def create_snap(self, db: Database, user_email: str, message: str, is_private: bool):

        hashtags = extract_hashtags(message)
        return self.snap_repository.create_snap(user_email, message, is_private, hashtags)

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

    
    def update_snap(self, db: Database, user_email: str, snap_id: str, snap_update: SnapUpdate):
        """
        Update a snap.
        """
        if len(snap_update.message) > MAX_MESSAGE_LENGTH:
            raise HTTPException(status_code=400, detail="Message exceeds the allowed length.")
         
        snap = self.snap_repository.get_snap_by_id(snap_id)
    
        if snap["email"] != user_email:
            raise HTTPException(status_code=403, detail="Not authorized to update this snap.")

        
        if snap_update.message:
            snap_update.hashtags = extract_hashtags(snap_update.message)

        return self.snap_repository.update_snap(snap_id, snap_update)
    
    def search_snaps_by_hashtag(self, db: Database, hashtag: str):
        """
        Search for snaps containing a specific hashtag.
        """
        snaps = self.snap_repository.search_snaps_by_hashtag(hashtag)
        if not snaps:
            raise HTTPException(status_code=404, detail="No snaps found with that hashtag.")
        return snaps
    
    def get_all_snaps(self, db: Database):
        """
        Fetch all snaps from the database.
        """
        snaps = self.snap_repository.get_all_snaps()
        if not snaps:
            raise HTTPException(status_code=404, detail="No snaps found.")
        return snaps

    def get_snaps_from_followed_users(self, db: Database, followed_users: List[str]):
        """
        obtains the snaps from the users followed by the user chronologically.
        """
        snaps = self.snap_repository.get_snaps_from_users(followed_users)
        return snaps
    
    def like_snap(self, snap_id: str, user_email: str):
        """
        Like a snap.
        """
        snap = self.snap_repository.get_snap_by_id(snap_id)
        if not snap:
            raise HTTPException(status_code=404, detail="Snap not found.")
        
        post_likes = self.snap_repository.get_snap_likes(snap_id)
        
        print("POST LIKES\n\n\n")
        print(post_likes)

        print("USER EMAIL\n\n\n")
        print(user_email)
        if user_email in post_likes:
            raise HTTPException(status_code=400, detail="You have already liked this snap.")
        
        return self.snap_repository.like_snap(snap_id, user_email)
    
    def unlike_snap(self, snap_id: str, user_email: str):
        """
        Unlike a snap.
        """
        snap = self.snap_repository.get_snap_by_id(snap_id)
        if not snap:
            raise HTTPException(status_code=404, detail="Snap not found.")
        
        post_likes = self.snap_repository.get_snap_likes(snap_id)

        if user_email not in post_likes:
            raise HTTPException(status_code=400, detail="You have not liked this snap.")
        
        return self.snap_repository.unlike_snap(snap_id, user_email)
    
    def favourite_snap(self, snap_id: str, user_email: str):
        """
        Favourite a snap.
        """
        snap = self.snap_repository.get_snap_by_id(snap_id)
        if not snap:
            raise HTTPException(status_code=404, detail="Snap not found.")
        
        post_favourites = self.snap_repository.get_snap_favourites(user_email)
        
        if snap_id in post_favourites:
            raise HTTPException(status_code=400, detail="You have already favourited this snap.")
        
        return self.snap_repository.favourite_snap(snap_id, user_email)
    
    def unfavourite_snap(self, snap_id: str, user_email: str):
        """
        Unfavourite a snap.
        """
        snap = self.snap_repository.get_snap_by_id(snap_id)
        if not snap:
            raise HTTPException(status_code=404, detail="Snap not found.")
        
        post_favourites = self.snap_repository.get_snap_favourites(user_email)

        if snap_id not in post_favourites:
            raise HTTPException(status_code=400, detail="You have not favourited this snap.")
        
        return self.snap_repository.unfavourite_snap(snap_id, user_email)
    
    def get_favourite_snaps(self, user_email: str):
        """
        Get the snaps favourited by user.
        """
        snaps_ids = self.snap_repository.get_all_snap_favourites(user_email)
        snaps = []
        for snaps_id in snaps_ids:
            snap = self.snap_repository.get_snap_by_id(snaps_id)
            if snap:
                snaps.append(snap)
        return snaps
