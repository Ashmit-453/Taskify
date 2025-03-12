import time
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate Limiting Configuration
RATE_LIMIT = 5  # Max requests per user
TIME_WINDOW = 60  # Time window in seconds

# Store user request counts
request_counts = defaultdict(lambda: {"count": 0, "timestamp": time.time()})

# 🌟 Logging Middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response

# 🚀 Rate Limiting Middleware
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host  # Get user IP
        current_time = time.time()
        user_data = request_counts[client_ip]

        # Reset count if time window passed
        if current_time - user_data["timestamp"] > TIME_WINDOW:
            user_data["count"] = 0
            user_data["timestamp"] = current_time

        # Check rate limit
        if user_data["count"] >= RATE_LIMIT:
            return Response(
                content="🚫 Rate limit exceeded. Try again later.",
                status_code=429,
            )

        user_data["count"] += 1  # Increase request count
        return await call_next(request)

# 🌍 CORS Middleware
def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=True,
        allow_methods=["*"],  
        allow_headers=["*"],  
    )
