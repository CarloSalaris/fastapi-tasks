from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, or_, select

from app.auth import get_current_user
from app.database import get_session
from app.filters import ProjectFilters
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
    filters: ProjectFilters = Depends(),
):
    query = select(Project)

    if current_user.role != UserRole.admin:
        # Projects I own OR projects where I have tasks assigned
        my_projects_ids = select(Task.project_id).where(
            Task.user_id == current_user.id, Task.project_id.is_not(None)
        )
        query = query.where(
            or_(
                Project.user_id == current_user.id,
                Project.id.in_(my_projects_ids),
            )
        )

    projects = session.exec(filters.apply(query)).all()
    return projects


@router.get("/{project_id}", response_model=ProjectPublic)
def get_project(project_id: int, session: SessionDep, current_user: CurrentUser):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role != UserRole.admin:
        has_tasks = session.exec(
            select(Task.id).where(
                Task.project_id == project_id, Task.user_id == current_user.id
            )
        ).first()

        if current_user.id != project.user_id and not has_tasks:
            raise HTTPException(status_code=404, detail="Project not found")
        # 404 instead of 403 so we don't reveal the existence of the project
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
