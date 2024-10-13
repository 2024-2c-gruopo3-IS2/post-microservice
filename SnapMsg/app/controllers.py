import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .users import get_followed_users, get_username_from_token
from .authentication import get_user_from_token
from .db import get_db, db
from .constants import MAX_MESSAGE_LENGTH
from .schemas import ErrorResponse, SnapCreate, SnapResponse, SnapUpdate
from .services import SnapService
from .repositories import SnapRepository

snap_router = APIRouter()
snap_service = SnapService(SnapRepository(db),os.getenv("AUTH_SERVICE_URL"))

@snap_router.post(
        "/",
        summary="Create a new TwitSnap",
        response_model=SnapResponse,
        status_code=status.HTTP_201_CREATED,
        responses={
            status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
            status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
        })
def create_snap(snap: SnapCreate, user_data: dict = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """
    Create a new TwitSnap post for authenticated users.
    """
    user_email = user_data["email"]

    if len(snap.message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(status_code=400, detail="Message exceeds 280 characters.")
    
    snap_created = snap_service.create_snap(db, user_email, snap.message, snap.is_private)
    return {"data":{ "id": snap_created["_id"], "message": snap_created["message"], "is_private": snap_created["is_private"], "hashtags": snap_created["hashtags"]}}


@snap_router.put("/{snap_id}", response_model=SnapResponse)
def update_snap(snap_id: str, snap_update: SnapUpdate, user_data: dict = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """
    Update a TwitSnap post, only if the user is the owner.
    """
    user_email = user_data["email"]
    snap_service.update_snap(db, user_email, snap_id, snap_update)

    return {"data": {"id": snap_id, "message": snap_update.message, "is_private": snap_update.is_private, "hashtags": snap_update.hashtags}}


@snap_router.delete("/{snap_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snap(snap_id: str, user_data: dict = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """
    Delete a TwitSnap post, only if the user is the owner.
    """
    user_email = user_data["email"]
    snap_service.delete_snap(db, snap_id, user_email)
    return {"detail": "Snap deleted successfully"}


@snap_router.get("/")
def get_snaps(user_data: dict = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """
    Get all public or private TwitSnaps based on the user's following status.
    """
    user_email = user_data["email"]
    snaps = snap_service.get_snaps(db, user_email)

    return {"data": snaps}

@snap_router.get(
    "/all-snaps",
    summary="Fetch all TwitSnaps",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    }
)
def get_all_snaps(db: Session = Depends(get_db)):
    """
    Fetch all public and private TwitSnaps.
    """
    snaps = snap_service.get_all_snaps(db)
    return {"data": snaps}


@snap_router.get("/snaps-followed/", summary="Get TwitSnaps from followed users")
def get_followed_snaps(user_data: dict = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """
    Get TwitSnaps from users the current user follows, ordered by most recent.
    This function requires both the email and the token.
    """
    token = user_data["token"] 

    username = get_username_from_token(token)


    followed_users = get_followed_users(token, username)

    
    snaps = snap_service.get_snaps_from_followed_users(db, followed_users)
    
    return {"data": snaps}

@snap_router.get("/by-hashtag", summary="Search snaps by hashtag")
def search_snaps(hashtag: str, db: Session = Depends(get_db)):
    """
    Search for TwitSnaps by hashtag.
    """
    snaps = snap_service.search_snaps_by_hashtag(db, hashtag)
    return {"data": snaps}

@snap_router.get("/{snap_id}", response_model=SnapResponse)
def get_snap(snap_id: str, db: Session = Depends(get_db)):
    """
    Get a Snap post by ID.
    """
    snap = snap_service.get_snap_by_id(db, snap_id)
    if snap:
        return {"data": snap}
    raise HTTPException(status_code=404, detail="Snap not found.")

@snap_router.post("/like", summary="Like a snap")
def like_snap(snap_id: str, user_data: dict = Depends(get_user_from_token)):
    """
    Like a Snap post.
    """
    user_email = user_data["email"]
    snap_service.like_snap(snap_id, user_email)
    return {"detail": "Snap liked successfully"}

@snap_router.post("/unlike", summary="Unlike a snap")
def unlike_snap(snap_id: str, user_data: dict = Depends(get_user_from_token)):
    """
    Unlike a Snap post.
    """
    user_email = user_data["email"]
    snap_service.unlike_snap(snap_id, user_email)
    return {"detail": "Snap unliked successfully"}