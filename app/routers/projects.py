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

    if current_user.role == UserRole.admin:
        pass  # admin can see all projects
    else:
        query = query.where(Project.user_id == current_user.id)

    projects = session.exec(query.offset(skip).limit(limit)).all()
    return projects


@router.get("/{project_id}", response_model=ProjectPublic)
def get_project(project_id: int, session: SessionDep, current_user: CurrentUser):
    project = session.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


""" CREATE """


@router.post("/", response_model=ProjectPublic, status_code=201)
def create_project(
    payload: ProjectCreate, session: SessionDep, current_user: CurrentUser
):
    project = Project.model_validate(payload, update={"user_id": current_user.id})
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
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    project_data = payload.model_dump(exclude_unset=True)
    project.sqlmodel_update(project_data)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


""" DELETE """


@router.delete("/{project_id}")
def delete_project(project_id: int, session: SessionDep, current_user: CurrentUser):
    project = session.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="project not found")
    session.delete(project)
    session.commit()
    return {"message": "Project deleted"}
