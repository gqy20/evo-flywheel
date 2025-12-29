"""API 测试配置和 Fixtures"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from evo_flywheel.db.models import Base


@pytest.fixture
def db_session(temp_db_path):
    """创建数据库会话 fixture

    Args:
        temp_db_path: 临时数据库路径
    """
    engine = create_engine(f"sqlite:///{temp_db_path}")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
