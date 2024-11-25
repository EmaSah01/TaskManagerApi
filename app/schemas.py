from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional

class TaskStatusEnum(str, Enum):
    pending = "Pending"
    completed = "Completed"
    in_progress = "In Progress"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: datetime
    reminder_time: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    status: Optional[TaskStatusEnum] = None

class Task(TaskBase):
    id: int
    user_id: int
    status: TaskStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True

class User(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime

    class Config:
        orm_mode = True
