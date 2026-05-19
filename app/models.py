from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

""" PROJECTS """


class ProjectBase(SQLModel):
    name: str
    description: str | None = None
    color: str | None = None


class Project(ProjectBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    user_id: int = Field(foreign_key="user.id")


class ProjectCreate(ProjectBase):
    user_id: int | None = None


class ProjectUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    user_id: int | None = None


class ProjectPublic(ProjectBase):
    id: int
    name: str
    created_at: datetime
    user_id: int


""" TASKS """


class TaskBase(SQLModel):
    title: str
    description: str | None = None
    completed: bool = False
    due_date: datetime | None = None
    project_id: int | None = Field(
        default=None, foreign_key="project.id"
    )  # for now it's optional. A task can exist without a project


class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None
    user_id: int = Field(foreign_key="user.id")


class TaskCreate(TaskBase):
    user_id: int | None = None


class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    due_date: datetime | None = None
    project_id: int | None = None
    user_id: int | None = None


class TaskPublic(TaskBase):
    id: int
    user_id: int
    project_id: int | None
    created_at: datetime
    updated_at: datetime | None
    due_date: datetime | None


class TaskFilters(BaseModel):
    """
    Query parameters for filtering and sorting tasks.

    How to add a new filter:
    1. Add the field here with type | None = None
    2. Add the field name to `filter_fields` in the apply() method
    3. The field name must match a column name in the Task model

    Sort and pagination are handled separately in apply().
    To add a new sortable field, update the `sort` pattern regex.
    """

    # --- Filters (must match Task column names) ---
    project_id: int | None = None
    user_id: int | None = None  # Filtro pensato per utente admin
    completed: bool | None = None

    # --- Sorting ---
    sort: Literal[
        "created_at",
        "updated_at",
        "due_date",
        "title",
        "completed",
        "project_id",
        "user_id",
    ] = "created_at"
    order: Literal["asc", "desc"] = "desc"

    # --- Pagination ---
    skip: int = 0
    limit: int = 20

    def apply(self, query):
        # Fields that map 1:1 to Task columns.
        # Add new filter field names here — no router changes needed.
        filter_fields = {"completed", "project_id", "user_id"}

        for field_name in filter_fields:
            value = getattr(self, field_name)
            if value is not None:
                query = query.where(getattr(Task, field_name) == value)

        sort_column = getattr(Task, self.sort)
        query = query.order_by(
            sort_column.desc() if self.order == "desc" else sort_column.asc()
        )

        return query.offset(self.skip).limit(self.limit)


""" USERS """


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)


class UserRole(str, Enum):
    admin = "admin"
    user = "user"


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.user)


class UserCreate(SQLModel):
    username: str
    email: str
    password: str


class UserUpdate(SQLModel):
    email: str | None = None
    username: str | None = None
    role: UserRole | None = None


class UserPublic(UserBase):
    id: int
    role: UserRole
