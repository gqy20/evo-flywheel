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


@pytest.fixture(autouse=True)
def reset_flywheel_state():
    """每个测试后重置飞轮状态

    防止测试间状态污染
    """
    yield
    # 测试结束后重置状态
    try:
        import importlib

        flywheel_module = importlib.import_module("evo_flywheel.api.v1.flywheel")
        # 重置调度器状态
        flywheel_module._scheduler_status["running"] = False
        flywheel_module._scheduler_status["last_run"] = None
        flywheel_module._scheduler_status["next_run"] = None
        # 重置调度器实例
        flywheel_module._scheduler_instance = None
    except Exception:
        # 如果模块未加载或出错，忽略
        pass
