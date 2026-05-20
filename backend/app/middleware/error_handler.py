import logging
import time
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Add timing header
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log request
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.4f}s"
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error processing {request.method} {request.url.path} - "
                f"Error: {str(e)} - Time: {process_time:.4f}s",
                exc_info=True
            )
            
            # Return structured error response
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Internal Server Error",
                    "message": str(e) if logger.isEnabledFor(logging.DEBUG) else "An unexpected error occurred"
                }
            )

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log request details
        logger.info(
            f"Incoming request: {request.method} {request.url} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        response = await call_next(request)
        
        return response
