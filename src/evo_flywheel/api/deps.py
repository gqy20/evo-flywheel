"""API 依赖注入模块"""

from sqlalchemy.orm import Session


def get_db() -> Session:
    """获取数据库会话

    在生产环境中返回真实的数据库会话。
    在测试环境中会被 override 为测试数据库会话。

    Returns:
        Session: 数据库会话
    """
    from sqlalchemy import create_engine

    from evo_flywheel.config import get_settings

    settings = get_settings()
    engine = create_engine(settings.effective_database_url)

    with Session(engine) as session:
        yield session
