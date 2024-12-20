import os
from fastapi import APIRouter, Depends, HTTPException, status
import requests
from sqlalchemy.orm import Session

from .users import get_followed_users, get_profile_by_username
from .authentication import get_admin_from_token, get_user_from_token
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
    username = user_data["username"]

    if len(snap.message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(status_code=400, detail="Message exceeds 280 characters.")
    
    snap_created = snap_service.create_snap(db, user_email, snap.message, snap.is_private, username)
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

@snap_router.get("/feed/", summary="Get TwitSnaps for feed")
def get_feed_snaps(user_data: dict = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """
    Get TwitSnaps from followed users and relevant content snaps.
    """
    token = user_data["token"]
    username = user_data["username"]
    email = user_data["email"]

    followed_users = get_followed_users(token, username)

    followed_snaps = snap_service.get_snaps_from_followed_users(db, followed_users)

    interest = get_profile_by_username(username)["interests"]

    relevant_snaps = snap_service.get_relevant_snaps(interest)

    retweets = snap_service.get_followed_retweeted_snaps(followed_users)

    snaps = followed_snaps + relevant_snaps + retweets

    snaps = sorted(snaps, key=lambda x: x["created_at"], reverse=True)

    response = requests.get(f"https://profile-microservice.onrender.com/profiles/verified-users")
    verified_users = response.json()

    print("email: ", email)
    shared = snap_service.get_shared_snaps(email)
    liked = snap_service.get_liked_snaps(email)
    favourited = snap_service.get_favourite_snaps(email)

    print("shared", [x["id"] for x in shared])
    print("liked", [x["id"] for x in liked])
    print("favourited", [x["id"] for x in favourited])
    print("verified", verified_users)


    for snap in snaps:
        snap["is_shared"] = snap["_id"] in [x["id"] for x in shared]
        snap["is_liked"] = snap["_id"] in [x["id"] for x in liked]
        snap["is_favourited"] = snap["_id"] in [x["id"] for x in favourited]
        snap["is_verified"] = snap["username"] in verified_users


    snaps = list({dic["_id"]: dic for dic in snaps}.values())

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
    username = user_data["username"]
    snap_service.like_snap(snap_id, user_email, username)
    return {"detail": "Snap liked successfully"}

@snap_router.post("/unlike", summary="Unlike a snap")
def unlike_snap(snap_id: str, user_data: dict = Depends(get_user_from_token)):
    """
    Unlike a Snap post.
    """
    user_email = user_data["email"]
    snap_service.unlike_snap(snap_id, user_email)
    return {"detail": "Snap unliked successfully"}

@snap_router.get("/liked/", summary="Get user's liked snaps")
def get_liked_snaps(user_data: dict = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """
    Get all Snap posts liked by the user.
    """
    user_email = user_data["email"]
    snaps = snap_service.get_liked_snaps(user_email)

    return {"data": snaps}

@snap_router.post("/favourite", summary="Favourite a snap")
def favourite_snap(snap_id: str, user_data: dict = Depends(get_user_from_token)):
    """
    Favourite a Snap post.
    """
    user_email = user_data["email"]
    snap_service.favourite_snap(snap_id, user_email)
    return {"detail": "Snap favourited successfully"}

@snap_router.post("/unfavourite", summary="Unfavourite a snap")
def unfavourite_snap(snap_id: str, user_data: dict = Depends(get_user_from_token)):
    """
    Unfavourite a Snap post.
    """
    user_email = user_data["email"]
    snap_service.unfavourite_snap(snap_id, user_email)
    return {"detail": "Snap unfavourited successfully"}

@snap_router.get("/favourites/", summary="Get user's favourite snaps")
def get_favourite_snaps(user_data: dict = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """
    Get all Snap posts favourited by the user.
    """
    user_email = user_data["email"]
    snaps = snap_service.get_favourite_snaps(user_email)

    return {"data": snaps}


@snap_router.get("/by-username/{username}", summary="Get TwitSnaps by username")
def get_snaps_by_username(
    username: str,  
    db: Session = Depends(get_db)
):
    """
    Get TwitSnaps for a particular user based on their username.
    """
    user_email = get_profile_by_username(username)["email"]
    
    snaps = snap_service.get_snaps(db, user_email)
    for snap in snaps:
        snap["retweet_user"] = ""

    retweeted_snaps = snap_service.get_retweeted_snaps(user_email)

    return {"data": sorted(snaps + retweeted_snaps, key=lambda x: x["created_at"], reverse=True)}

@snap_router.post("/block", summary="Block a twitsnap")
def block_snap(snap_id: str, user_data: dict = Depends(get_admin_from_token)):
    """
    Block a Snap post.
    """
    user_email = user_data["email"]
    snap_service.block_snap(snap_id, user_email)
    return {"detail": "Snap blocked successfully"}

@snap_router.post("/unblock", summary="Unblocke a twitsnap")
def unblock_snap(snap_id: str, user_data: dict = Depends(get_admin_from_token)):
    """
    Unblock a Snap post.
    """
    user_email = user_data["email"]
    snap_service.unblock_snap(snap_id, user_email)
    return {"detail": "Snap unblocked successfully"}

@snap_router.get("/unblocked/", summary="Get unblocked snaps")
def get_unblocked_snaps(user_data: dict = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """
    Get all unblocked Snap posts.
    """
    user_email = user_data["email"]
    snaps = snap_service.get_unblocked_snaps(user_email)

    return {"data": snaps}

@snap_router.get("/trending-topics/", summary="Get trending hashtags")
def get_trending_hashtags():
    """
    Get trending hashtags based on Snap posts.
    """
    hashtags = snap_service.get_trending_hashtags()
    return {"data": hashtags}

@snap_router.post("/snap-share", summary="Retweet a snap")
def snap_share(snap_id: str, user_data: dict = Depends(get_user_from_token)):
    """
    Retweet a Snap post.
    """
    user_email = user_data["email"]
    username = user_data["username"]
    snap_service.snap_share(snap_id, user_email, username)
    return {"detail": "Snap shared successfully"}

@snap_router.get("/shared/", summary="Get shared snaps")
def get_shared_snaps(user_data: dict = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """
    Get all Snap posts shared by the user.
    """
    user_email = user_data["email"]
    snaps = snap_service.get_shared_snaps(user_email)

    return {"data": snaps}


@snap_router.get("/users-interactions/", summary="Get users iteractions with my snaps")
def get_users_interactions(user_data: dict = Depends(get_user_from_token)):
    """
    Get all users who interacted with user's Snap posts.
    """
    user_email = user_data["email"]
    users = snap_service.get_users_liked_and_retweeted_snaps(user_email)

    return {"data": users}