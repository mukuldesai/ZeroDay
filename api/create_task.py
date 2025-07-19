from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import uuid

from database.models import Task as TaskModel
from database.setup import get_db

router = APIRouter(prefix="/api", tags=["tasks"])

class CreateTaskRequest(BaseModel):
    title: str
    description: str
    priority: str
    dueDate: str
    status: str = "todo"
    assignee: str = "You"

@router.post("/create_task")
def create_task(request: CreateTaskRequest, db: Session = Depends(get_db)):
    new_task = TaskModel(
        id=f"task_{uuid.uuid4().hex[:8]}",
        title=request.title,
        description=request.description,
        priority=request.priority,
        dueDate=request.dueDate,
        status=request.status,
        assignee=request.assignee,
        createdAt=datetime.utcnow()
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
