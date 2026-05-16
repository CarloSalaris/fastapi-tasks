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
    user_id: int = Field(foreign_key="user.id")


""" TASKS """


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


""" USERS """


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str


class UserCreate(SQLModel):
    username: str
    email: str
    password: str


class UserPublic(UserBase):
    id: int
