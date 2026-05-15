from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models import Task, TaskCreate, TaskPublic, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])

SessionDep = Annotated[Session, Depends(get_session)]

""" READ """


@router.get("/", response_model=list[TaskPublic])
def list_tasks(
    session: SessionDep, skip: int = 0, limit: int = Query(default=20, le=100)
):
    tasks = session.exec(select(Task).offset(skip).limit(limit)).all()
    return tasks


@router.get("/{task_id}", response_model=TaskPublic)
def get_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


""" CREATE """


@router.post("/", response_model=TaskPublic, status_code=201)
def create_task(payload: TaskCreate, session: SessionDep):
    task = Task.model_validate(payload)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


""" UPDATE """


@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(task_id: int, payload: TaskUpdate, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_data = payload.model_dump(exclude_unset=True)
    task.sqlmodel_update(task_data)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


""" DELETE """


@router.delete("/{task_id}")
def delete_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"message": "Task deleted"}
