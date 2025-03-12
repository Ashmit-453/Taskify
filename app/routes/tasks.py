from fastapi import APIRouter, Depends,HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user, require_role
from ..models import User,Task
from app.schemas import TaskCreate, TaskResponse
import time 
from app.schemas import TaskUpdate
from app.websocket import manager

router = APIRouter()

# 📝 Normal users can create tasks
@router.post("/")
def create_task(task_data: dict, current_user: User = Depends(get_current_user)):
    return {"message": f"Task created by {current_user.username}"}

# 🔐 Admin can delete tasks
@router.delete("/{task_id}", dependencies=[Depends(require_role("admin"))])
def delete_task(task_id: int):
    return {"message": f"Task {task_id} deleted by Admin"}

def send_task_notification(email: str, task_name: str):
    """Simulates sending an email when a new task is created."""
    time.sleep(3)  # Simulating delay
    print(f"📩 Email sent to {email}: New task '{task_name}' created!")

@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Creates a new task and sends a background email notification."""
    new_task = Task(**task.dict(), owner_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Send email notification in the background
    background_tasks.add_task(send_task_notification, current_user.email, task.title)

    return new_task

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = task_update.status
    db.commit()
    db.refresh(task)

    # Notify clients about the update
    await manager.broadcast(f"Task {task_id} updated to {task.status}")

    return {"message": "Task updated", "task": task}