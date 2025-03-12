from fastapi import FastAPI
from app.database import engine, Base
from app.routes import users, tasks
from .middleware import LoggingMiddleware, RateLimitMiddleware, add_cors_middleware
from app.websocket import websocket_endpoint
from app.auth import router as auth_router
# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()
@app.get("/")
def read_root():
    return {"message": "Welcome to Taskify!"}
app.include_router(auth_router)
# Middleware
add_cors_middleware(app)
app.add_middleware(LoggingMiddleware)

# ✅ Apply Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

# WebSocket route
app.add_api_websocket_route("/ws", websocket_endpoint)
