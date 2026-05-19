from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.auth import get_current_user
from app.database import get_session
from app.models import (
    Project,
    ProjectCreate,
    ProjectPublic,
    ProjectUpdate,
    Task,
    User,
    UserRole,
)

router = APIRouter(prefix="/projects", tags=["projects"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


""" READ """


@router.get("/", response_model=list[ProjectPublic])
def list_projects(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = Query(default=20, le=100),
):
    query = select(Project)

    if current_user.role != UserRole.admin:  # admin can see all projects
        query = query.where(Project.user_id == current_user.id)

    projects = session.exec(query.offset(skip).limit(limit)).all()
    return projects


@router.get("/{project_id}", response_model=ProjectPublic)
def get_project(project_id: int, session: SessionDep, current_user: CurrentUser):
    project = session.get(Project, project_id)
    if not project or (
        project.user_id != current_user.id and current_user.role != UserRole.admin
    ):
        raise HTTPException(status_code=404, detail="Project not found")
    return project


""" CREATE """


@router.post("/", response_model=ProjectPublic, status_code=201)
def create_project(
    payload: ProjectCreate, session: SessionDep, current_user: CurrentUser
):
    if payload.user_id is not None and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=403, detail="Only admins can assign projects to other users"
        )
    assigned_user_id = (
        payload.user_id if payload.user_id is not None else current_user.id
    )

    project = Project.model_validate(payload, update={"user_id": assigned_user_id})
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


""" UPDATE """


@router.patch("/{project_id}", response_model=ProjectPublic)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    session: SessionDep,
    current_user: CurrentUser,
):
    project = session.get(Project, project_id)
    if not project or (
        project.user_id != current_user.id and current_user.role != UserRole.admin
    ):
        raise HTTPException(status_code=404, detail="Project not found")

    if payload.user_id is not None and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=403, detail="Only admins can reassign projects to other users"
        )
    project_data = payload.model_dump(exclude_unset=True)
    project.sqlmodel_update(project_data)

    # Cascade: reassign all tasks in this project to the new owner
    if payload.user_id is not None:
        tasks = session.exec(select(Task).where(Task.project_id == project_id)).all()
        for task in tasks:
            task.user_id = payload.user_id
            session.add(task)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


""" DELETE """


@router.delete("/{project_id}")
def delete_project(project_id: int, session: SessionDep, current_user: CurrentUser):
    project = session.get(Project, project_id)
    if not project or (
        project.user_id != current_user.id and current_user.role != UserRole.admin
    ):
        raise HTTPException(status_code=404, detail="project not found")
    session.delete(project)
    session.commit()
    return {"message": "Project deleted"}
