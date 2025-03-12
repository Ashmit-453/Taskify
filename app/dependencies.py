from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db
from .auth import get_current_user
from .models import User

# 🚀 Database Dependency (Directly importing from `database.py`)
def get_db():
    db = next(get_db())  # Get DB session
    try:
        yield db
    finally:
        db.close()

# 🔑 Role-Based Access Control (RBAC) - Only Admins
def get_current_active_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="🚫 Not enough permissions"
        )
    return current_user
