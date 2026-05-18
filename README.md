# FastAPI Tasks API

A simple CRUD REST API for task management, organized into projects, built with FastAPI and SQLModel.

## Tech Stack

- Python 3.14
- FastAPI
- SQLModel (SQLAlchemy + Pydantic)
- SQLite
- Alembic (database migrations)
- pydantic-settings (environment configuration)
- pytest (test suite)

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/fastapi-tasks.git
cd fastapi-tasks
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt
```

Copy the example env file and fill in the required values:

```bash
cp .env.example .env
```

| Variable                      | Default               | Description                   |
| ----------------------------- | --------------------- | ----------------------------- |
| `SECRET_KEY`                  | _(required)_          | JWT signing secret            |
| `DATABASE_URL`                | `sqlite:///./test.db` | SQLAlchemy database URL       |
| `ALGORITHM`                   | `HS256`               | JWT algorithm                 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                  | JWT token lifetime in minutes |

## Database migrations

```bash
alembic upgrade head
```

## Run

```bash
fastapi dev
```

API docs: http://localhost:8000/docs

## Tests

```bash
pytest
```

## Endpoints

### Auth

| Method | Endpoint       | Auth   | Description             |
| ------ | -------------- | ------ | ----------------------- |
| POST   | /auth/register | Public | Register a new user     |
| POST   | /auth/token    | Public | Login and get JWT token |

### Projects

| Method | Endpoint       | Auth | Description                      |
| ------ | -------------- | ---- | -------------------------------- |
| GET    | /projects      | User | List own projects (all if admin) |
| GET    | /projects/{id} | User | Get a single project             |
| POST   | /projects      | User | Create a project                 |
| PATCH  | /projects/{id} | User | Update a project                 |
| DELETE | /projects/{id} | User | Delete a project                 |

### Tasks

| Method | Endpoint    | Auth | Description                   |
| ------ | ----------- | ---- | ----------------------------- |
| GET    | /tasks      | User | List own tasks (all if admin) |
| GET    | /tasks/{id} | User | Get a single task             |
| POST   | /tasks      | User | Create a task                 |
| PATCH  | /tasks/{id} | User | Update a task                 |
| DELETE | /tasks/{id} | User | Delete a task                 |

### Users

| Method | Endpoint    | Auth  | Description             |
| ------ | ----------- | ----- | ----------------------- |
| GET    | /users      | Admin | List all users          |
| GET    | /users/me   | User  | Get own profile         |
| PATCH  | /users/me   | User  | Update own profile      |
| GET    | /users/{id} | Admin | Get a user by ID        |
| POST   | /users      | Admin | Create a user with role |
| PATCH  | /users/{id} | Admin | Update a user           |
| DELETE | /users/{id} | Admin | Delete a user           |
