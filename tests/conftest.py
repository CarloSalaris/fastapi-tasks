import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.auth import hash_password
from app.database import get_session
from app.main import app
from app.models import User, UserRole


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient, session: Session):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
        role=UserRole.user,
    )
    session.add(user)
    session.commit()

    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="admin_headers")
def admin_headers_fixture(client: TestClient, session: Session):
    admin = User(
        username="adminuser",
        email="admin@example.com",
        hashed_password=hash_password("adminpass123"),
        role=UserRole.admin,
    )
    session.add(admin)
    session.commit()

    response = client.post(
        "/auth/token",
        data={"username": "adminuser", "password": "adminpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="second_user_headers")
def second_user_headers_fixture(client: TestClient, session: Session):
    user = User(
        username="seconduser",
        email="second@example.com",
        hashed_password=hash_password("secondpass123"),
        role=UserRole.user,
    )
    session.add(user)
    session.commit()

    response = client.post(
        "/auth/token",
        data={"username": "seconduser", "password": "secondpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
