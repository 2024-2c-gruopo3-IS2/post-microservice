from fastapi import FastAPI, HTTPException, Request
from ddtrace import patch_all
from ddtrace.contrib.asgi import TraceMiddleware
from .middleware import ErrorHandlingMiddleware
from .config import logger
from .controllers import snap_router


patch_all()

app = FastAPI()

app.add_middleware(TraceMiddleware, service="post-microservice", distributed_tracing=True)

app.add_middleware(ErrorHandlingMiddleware)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for HTTPException to ensure all errors are returned in RFC 7807 format.
    """
    raise exc


app.include_router(snap_router, prefix="/snaps")

logger.info("FastAPI application is starting...")




