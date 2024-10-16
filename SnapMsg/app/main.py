from fastapi import FastAPI, HTTPException, Request
from .middleware import ErrorHandlingMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .config import logger
from .controllers import snap_router

app = FastAPI()
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for HTTPException to ensure all errors are returned in RFC 7807 format.
    """
    raise exc


app.include_router(snap_router, prefix="/snaps", tags=["snaps"])

logger.info("FastAPI application is starting...")






