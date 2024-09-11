from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from .constants import MAX_MESSAGE_LENGTH
from .config import get_db, logger
from .schemas import ErrorResponse, SnapCreate, SnapResponse, SnapListResponse, SnapData, SnapUpdate
from .services import SnapService
from .repositories import SnapRepository

snap_router = APIRouter()
snap_service = SnapService(SnapRepository())

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
def create_snap(snap: SnapCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create a new TwitSnap post for authenticated users.
    """
    if len(snap.message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(status_code=400, detail="Message exceeds 280 characters.")
    
    snap_id = snap_service.create_snap(db, user["id"], snap.message, snap.privacy)
    return {"id": snap_id, "message": snap.message}


@snap_router.put("/{snap_id}", response_model=SnapResponse)
def update_snap(snap_id: str, snap_update: SnapUpdate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Update a TwitSnap post, only if the user is the owner.
    """
    snap = snap_service.get_snap_by_id(db, snap_id)
    if snap['user_id'] != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to edit this snap.")

    snap_service.update_snap(db, snap_id, snap_update.message, snap_update.tags)
    return {"id": snap_id, "message": snap_update.message}


@snap_router.delete("/{snap_id}")
def delete_snap(snap_id: str, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Delete a TwitSnap post, only if the user is the owner.
    """
    snap = snap_service.get_snap_by_id(db, snap_id)
    if snap['user_id'] != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to delete this snap.")
    
    snap_service.delete_snap(db, snap_id)
    return {"detail": "Snap deleted successfully"}


@snap_router.get("/")
def get_snaps(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get all public or private TwitSnaps based on the user's following status.
    """
    if user:
        snaps = snap_service.get_user_snaps(db, user["id"])
    else:
        snaps = snap_service.get_public_snaps(db)

    return {"data": snaps}
