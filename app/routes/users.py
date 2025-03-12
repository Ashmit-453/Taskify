from fastapi import APIRouter, Depends,Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user, require_role
from ..models import User,Task
from ..schemas import TaskResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_user, get_current_active_admin

router = APIRouter()

@router.get("/tasks")
def get_tasks(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return {"message": f"Tasks for user {current_user.username}"}

@router.delete("/admin/delete-user")
def delete_user(db: Session = Depends(get_db), admin=Depends(get_current_active_admin)):
    return {"message": "User deleted by admin"}

# 🛠 Normal User Route
@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email, "role": current_user.role}

# 🔐 Admin-only route
@router.get("/admin/dashboard", dependencies=[Depends(require_role("admin"))])
def admin_dashboard():
    return {"message": "Welcome Admin!"}

@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    skip: int = Query(0, alias="offset", ge=0),  # Offset-based pagination
    limit: int = Query(10, alias="limit", le=100),  # Limit-based pagination
):
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return tasks