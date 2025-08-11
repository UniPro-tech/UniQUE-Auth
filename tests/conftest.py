import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import hashlib
from datetime import datetime, timezone
from unique_api.app.main import app
from unique_api.app.model import (
    Users,
    Apps,
    RedirectUris,
)
from unique_api.app.db import get_db, Base


# テスト用のデータベース設定
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def test_db():
    # テスト用のデータベースを作成
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def test_user(test_db):
    # テストユーザーを作成
    user = Users(
        custom_id="test_user",
        password_hash=hashlib.sha256("test_password".encode()).hexdigest(),
        created_at=datetime.now(timezone.utc)
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_app(test_db):
    # テストアプリケーションを作成
    app = Apps(
        name="Test App",
        client_id="test_client_id",
        client_secret=hashlib.sha256("test_client_secret".encode()).hexdigest(),
        aud="test_client_id",
        created_at=datetime.now(timezone.utc)
    )
    redirect_uri = RedirectUris(
        uri="http://localhost:3000/callback"
    )
    app.redirect_uris.append(redirect_uri)
    test_db.add(app)
    test_db.commit()
    test_db.refresh(app)
    return app
