from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import logger
from schemas import ErrorResponse


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that handles exceptions occurring during request processing and returns
    a structured JSON response adhering to the RFC 7807 standard.

    This middleware captures `HTTPException` errors and general exceptions, formats them
    into a standardized error response, and logs the exceptions for debugging purposes.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Intercepts the request, processes it, and handles any exceptions that occur during
        the request lifecycle.

        Args:
            request (Request): The incoming HTTP request object.
            call_next (Callable): A function that processes the request and returns a response.

        Returns:
            Response: The HTTP response object, either a successful response or an error response
            formatted according to RFC 7807.
        """
        logger.info(f"Request received")
        try:
            response = await call_next(request)
            return response
        except HTTPException as http_exc:
            logger.warning(f"Caught HTTPException: {http_exc.detail}")
            
            if http_exc.status_code == status.HTTP_400_BAD_REQUEST:
                title = "Bad Request Error"
            elif http_exc.status_code == status.HTTP_404_NOT_FOUND:
                title = "Snap Not Found"
            else:
                title = http_exc.detail or "HTTP Error"
            
            error_response = ErrorResponse(
                type="about:blank",
                title=title,
                status=http_exc.status_code,
                detail=http_exc.detail or "An error occurred.",
                instance=str(request.url),
            )
            return JSONResponse(status_code=http_exc.status_code, content=error_response.dict())
        except Exception as exc:
            error_response = ErrorResponse(
                type="about:blank",
                title="Internal Server Error",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred.",
                instance=str(request.url),
            )
            logger.error(f"Unhandled exception: {exc}")
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response.dict())

