from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from app.database import engine
from app.routers import auth, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Tasks API",
    description="CRUD REST API for task management",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(tasks.router)
app.include_router(auth.router)
