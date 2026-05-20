from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, or_, select

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


# Check is user can access the task (assignee, project owner or admin)
def can_access_task(task: Task, user: User, session: Session):
    if user.role == UserRole.admin:
        return True
    if task.user_id == user.id:
        return True
    if task.project_id is not None:
        project = session.get(Project, task.project_id)
        if project and project.user_id == user.id:
            return True
    return False


""" READ """


@router.get("/", response_model=list[TaskPublic])
def list_tasks(
    session: SessionDep,
    current_user: CurrentUser,
    filters: TaskFilters = Depends(),
):
    query = select(Task)

    if current_user.role != UserRole.admin:  # admin can see all tasks
        # Tasks assigned to me OR tasks in projects I own
        my_projects_ids = select(Project.id).where(Project.user_id == current_user.id)
        query = query.where(
            or_(
                Task.user_id == current_user.id,
                Task.project_id.in_(my_projects_ids),
            )
        )

    task = session.exec(filters.apply(query)).all()
    return task


@router.get("/{task_id}", response_model=TaskPublic)
def get_task(task_id: int, session: SessionDep, current_user: CurrentUser):
    task = session.get(Task, task_id)
    if not task or not can_access_task(task, current_user, session):
        raise HTTPException(status_code=404, detail="Task not found")
    return task


""" CREATE """


@router.post("/", response_model=TaskPublic, status_code=201)
def create_task(payload: TaskCreate, session: SessionDep, current_user: CurrentUser):
    # If creating inside a project, check project ownership
    if payload.project_id is not None:
        project = session.get(Project, payload.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        is_owner = project.user_id == current_user.id
        is_admin = current_user.role == UserRole.admin

        if not (is_owner or is_admin):
            raise HTTPException(
                status_code=403, detail="Only project owners or admins can add tasks"
            )

    if payload.user_id is not None and current_user.role != UserRole.admin:
        # Non-admin project owners can assign tasks to others in their project
        if payload.project_id is not None:
            project = session.get(Project, payload.project_id)
            if not project or project.user_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Only admins can assign tasks to other users",
                )
        else:
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
    if not task or not can_access_task(task, current_user, session):
        raise HTTPException(status_code=404, detail="Task not found")

    # Only project owners or admin can reassign tasks
    if payload.user_id is not None:
        is_admin = current_user.role == UserRole.admin
        is_project_owner = False
        if task.project_id is not None:
            project = session.get(Project, task.project_id)
            is_project_owner = project and project.user_id == current_user.id

        if not (is_project_owner or is_admin):
            raise HTTPException(
                status_code=403,
                detail="Only project owners or admins can reassign tasks",
            )

    # Commented because now a user can have tasks inside some other user's project
    """ # If reassigning a task, remove it from its current project
    # (a task can't belong to a project owned by a different user)
    if payload.user_id is not None and task.project_id is not None:
        project = session.get(Project, task.project_id)
        if project and project.user_id != payload.user_id:
            task.project_id = None """

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

    if not task or not can_access_task(task, current_user, session):
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"message": "Task deleted"}
