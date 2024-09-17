import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import get_db, db
from constants import MAX_MESSAGE_LENGTH
from schemas import ErrorResponse, SnapCreate, SnapResponse, SnapListResponse, SnapData, SnapUpdate
from services import SnapService
from repositories import SnapRepository

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
def create_snap(token: str, snap: SnapCreate, db: Session = Depends(get_db)):
    """
    Create a new TwitSnap post for authenticated users.
    """
    if len(snap.message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(status_code=400, detail="Message exceeds 280 characters.")
    
    snap_id = snap_service.create_snap(db, token, snap.message, snap.privacy)
    return {"data":{ "id": snap_id, "message": snap.message, "privacy": snap.privacy}}


@snap_router.put("/{snap_id}", response_model=SnapResponse)
def update_snap(token: str, snap_id: str, snap_update: SnapUpdate, db: Session = Depends(get_db)):
    """
    Update a TwitSnap post, only if the user is the owner.
    """

    snap_service.update_snap(db, token, snap_id, snap_update)

    return {"data": {"id": snap_id, "message": snap_update.message, "privacy": snap_update.privacy}}


@snap_router.delete("/{snap_id}")
def delete_snap(token: str, snap_id: str, db: Session = Depends(get_db)):
    """
    Delete a TwitSnap post, only if the user is the owner.
    """
    
    snap_service.delete_snap(db, snap_id, token)
    return {"detail": "Snap deleted successfully"}


@snap_router.get("/")
def get_snaps(token: str, db: Session = Depends(get_db)):
    """
    Get all public or private TwitSnaps based on the user's following status.
    """

    snaps = snap_service.get_snaps(db, token)

    return {"data": snaps}
