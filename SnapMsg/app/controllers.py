import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .authentication import get_user_from_token
from .db import get_db, db
from .constants import MAX_MESSAGE_LENGTH
from .schemas import ErrorResponse, SnapCreate, SnapResponse, SnapListResponse, SnapData, SnapUpdate
from .services import SnapService
from .repositories import SnapRepository

snap_router = APIRouter()
snap_service = SnapService(SnapRepository(db), os.getenv("AUTH_SERVICE_URL"))

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
def create_snap(snap: SnapCreate, user_email: callable = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """
    Create a new TwitSnap post for authenticated users.
    """
    if len(snap.message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(status_code=400, detail="Message exceeds 280 characters.")
    
    snap_id = snap_service.create_snap(db, user_email, snap.message, snap.is_private)
    return {"data":{ "id": snap_id, "message": snap.message, "is_private": snap.is_private}}


@snap_router.put("/{snap_id}", response_model=SnapResponse)
def update_snap(snap_id: str, snap_update: SnapUpdate, user_email: callable = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """
    Update a TwitSnap post, only if the user is the owner.
    """

    snap_service.update_snap(db, user_email, snap_id, snap_update)

    return {"data": {"id": snap_id, "message": snap_update.message, "is_private": snap_update.is_private}}


@snap_router.delete("/{snap_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snap(snap_id: str, user_email: callable = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """
    Delete a TwitSnap post, only if the user is the owner.
    """
    
    snap_service.delete_snap(db, snap_id, user_email)
    return {"detail": "Snap deleted successfully"}


@snap_router.get("/")
def get_snaps(user_email: callable = Depends(get_user_from_token), db: Session = Depends(get_db)):
    """
    Get all public or private TwitSnaps based on the user's following status.
    """

    snaps = snap_service.get_snaps(db, user_email)

    return {"data": snaps}

@snap_router.get(
    "/all-snaps",
    summary="Fetch all TwitSnaps",
    response_model=SnapListResponse,
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