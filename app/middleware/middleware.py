from fastapi import Request, status
from fastapi.responses import JSONResponse

from starlette.exceptions import HTTPException

from app.utils.exceptions import APPException
from app.config.settings import settings

import time
import logging

from app.config.logging import setup_logging


setup_logging(
    logging.DEBUG if settings.debug else logging.INFO
)

logger = logging.getLogger(__name__)

class LoggingMiddleware:
    """Middleware for logging requests and responses"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            start_time = time.time()
            
            # Log request
            logger.info(f"Request: {request.method} {request.url}")
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    process_time = time.time() - start_time
                    logger.info(f"Response: {message['status']} - {process_time:.4f}s")
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
