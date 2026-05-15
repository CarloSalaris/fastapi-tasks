from datetime import datetime

from sqlmodel import Field, SQLModel


class TaskBase(SQLModel):
    title: str
    description: str | None = None
    completed: bool = False


class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TaskPublic(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime | None
