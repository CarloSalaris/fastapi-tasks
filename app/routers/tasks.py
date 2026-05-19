from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import get_current_user
from app.database import get_session
from app.filters import TaskFilters
from app.models import (
    Project,
    Task,
    TaskCreate,
    TaskPublic,
    TaskUpdate,
    User,
    UserRole,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


""" READ """


@router.get("/", response_model=list[TaskPublic])
def list_tasks(
    session: SessionDep,
    current_user: CurrentUser,
    filters: TaskFilters = Depends(),
):
    query = select(Task)

    if current_user.role != UserRole.admin:  # admin can see all tasks
        query = query.where(Task.user_id == current_user.id)

    task = session.exec(filters.apply(query)).all()
    return task


@router.get("/{task_id}", response_model=TaskPublic)
def get_task(task_id: int, session: SessionDep, current_user: CurrentUser):
    task = session.get(Task, task_id)
    if not task or (
        task.user_id != current_user.id and current_user.role != UserRole.admin
    ):
        raise HTTPException(status_code=404, detail="Task not found")
    return task


""" CREATE """


@router.post("/", response_model=TaskPublic, status_code=201)
def create_task(payload: TaskCreate, session: SessionDep, current_user: CurrentUser):
    if payload.user_id is not None and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=403, detail="Only admins can assign tasks to other users"
        )
    assigned_user_id = (
        payload.user_id if payload.user_id is not None else current_user.id
    )
    task = Task.model_validate(payload, update={"user_id": assigned_user_id})
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


""" UPDATE """


@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(
    task_id: int, payload: TaskUpdate, session: SessionDep, current_user: CurrentUser
):
    task = session.get(Task, task_id)
    if not task or (
        task.user_id != current_user.id and current_user.role != UserRole.admin
    ):
        raise HTTPException(status_code=404, detail="Task not found")

    if payload.user_id is not None and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=403, detail="Only admins can reassign tasks to other users"
        )

    # If reassigning a task, remove it from its current project
    # (a task can't belong to a project owned by a different user)
    if payload.user_id is not None and task.project_id is not None:
        project = session.get(Project, task.project_id)
        if project and project.user_id != payload.user_id:
            task.project_id = None

    task_data = payload.model_dump(exclude_unset=True)
    task.sqlmodel_update(task_data)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


""" DELETE """


@router.delete("/{task_id}")
def delete_task(task_id: int, session: SessionDep, current_user: CurrentUser):
    task = session.get(Task, task_id)
    if not task or (
        task.user_id != current_user.id and current_user.role != UserRole.admin
    ):
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"message": "Task deleted"}
