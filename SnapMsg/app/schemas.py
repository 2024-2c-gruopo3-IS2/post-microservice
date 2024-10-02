from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

class SnapCreate(BaseModel):
    """
    Model for creating a Snap.
    
    Attributes:
        message (str): The content of the Snap.
        is_private (bool): Whether the Snap is private or not.
    """
    message: str
    is_private: bool

class SnapData(BaseModel):
    """
    Model for representing Snap data.
    
    Attributes:
        id (UUID): The unique identifier of the Snap.
        message (str): The content of the Snap.
        is_private (bool): Whether the Snap is private or not.
        hashtags (List[str]): The list of hashtags in the Snap.
    """
    id: str
    message: str
    is_private: bool
    hashtags: List[str]

class SnapResponse(BaseModel):
    """
    Model for the response of an individual Snap.
    
    Attributes:
        data (SnapData): The data of the Snap.
    """
    data: SnapData

class SnapListResponse(BaseModel):
    """
    Model for the response of a list of Snaps.
    
    Attributes:
        data (List[SnapData]): The list of Snaps.
    """
    data: List[SnapData]


class ErrorResponse(BaseModel):
    """
    Model for representing an error response.

    Attributes:
        type (str): The type of the error.
        title (str): The title of the error.
        status (int): The HTTP status code of the error.
        detail (str): The detailed description of the error.
        instance (str): The instance where the error occurred.
    """
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str

class SnapUpdate(BaseModel):
    """
    Model for updating a Snap.
    
    Attributes:
        message (Optional[str]): The new content of the Snap.
        is_private (Optional[bool]): Whether the Snap is private or not.
        hashtags (Optional[List[str]]): The new list of hashtags in the Snap.
    """
    message: Optional[str] = None
    is_private: Optional[bool] = None
    hashtags: Optional[List[str]] = None



