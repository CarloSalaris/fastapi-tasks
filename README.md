# FastAPI Tasks API

A simple CRUD REST API for task management, built with FastAPI and SQLModel.

## Tech Stack

- Python 3.14
- FastAPI
- SQLModel (SQLAlchemy + Pydantic)
- SQLite

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/fastapi-tasks.git
cd fastapi-tasks
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt
```

## Run

```bash
fastapi dev
```

API docs: http://localhost:8000/docs

## Endpoints

| Method | Endpoint        | Description       |
|--------|-----------------|-------------------|
| GET    | /tasks          | List all tasks    |
| GET    | /tasks/{id}     | Get a single task |
| POST   | /tasks          | Create a task     |
| PATCH  | /tasks/{id}     | Update a task     |
| DELETE | /tasks/{id}     | Delete a task     |