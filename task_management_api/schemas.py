from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["johndoe"])
    email: EmailStr = Field(..., examples=["john@example.com"])

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, examples=["Finish API Project"])
    description: Optional[str] = Field(None, max_length=500, examples=["Write end-to-end code"])
    status: TaskStatus = Field(default=TaskStatus.TODO)
    user_id: int = Field(..., description="The ID of the user assigned to this task")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    user_id: int

    class Config:
        from_attributes = True