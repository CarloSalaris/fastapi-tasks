from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.auth import get_current_user
from app.database import get_session
from app.models import Task, TaskCreate, TaskPublic, TaskUpdate, User

router = APIRouter(prefix="/tasks", tags=["tasks"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


""" READ """


@router.get("/", response_model=list[TaskPublic])
def list_tasks(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = Query(default=20, le=100),
):
    tasks = session.exec(
        select(Task).where(Task.user_id == current_user.id).offset(skip).limit(limit)
    ).all()
    return tasks


@router.get("/{task_id}", response_model=TaskPublic)
def get_task(task_id: int, session: SessionDep, current_user: CurrentUser):
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


""" CREATE """


@router.post("/", response_model=TaskPublic, status_code=201)
def create_task(payload: TaskCreate, session: SessionDep, current_user: CurrentUser):
    task = Task.model_validate(payload, update={"user_id": current_user.id})
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
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
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
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"message": "Task deleted"}
