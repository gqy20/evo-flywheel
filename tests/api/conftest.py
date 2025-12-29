"""API 测试 Fixtures"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from evo_flywheel.db.models import Base

# 导入 paper_factory fixture
from tests.factories.paper_factory import paper_factory  # noqa: F401

# 使用内存数据库进行测试
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def test_engine():
    """创建测试数据库引擎"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db(test_engine):
    """创建测试数据库会话"""
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client(test_db):
    """创建测试客户端"""
    # 导入在这里进行，确保测试数据库已创建
    from evo_flywheel.api.deps import get_db
    from evo_flywheel.api.main import app

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
