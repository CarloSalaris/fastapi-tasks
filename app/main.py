from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import auth, tasks, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Tasks API",
    description="CRUD REST API for task management",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)
