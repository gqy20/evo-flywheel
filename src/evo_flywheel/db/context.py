"""数据库上下文管理器

提供统一的数据库会话创建和管理
"""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from evo_flywheel.config import get_settings
from evo_flywheel.logging import get_logger

logger = get_logger(__name__)

# 全局引擎和会话工厂缓存
_engine = None
_session_factory = None


def _get_engine():
    """获取数据库引擎（单例模式）"""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(settings.effective_database_url)
        logger.info(f"Created database engine: {settings.effective_database_url}")
    return _engine


def _get_session_factory():
    """获取会话工厂（单例模式）"""
    global _session_factory
    if _session_factory is None:
        engine = _get_engine()
        _session_factory = sessionmaker(bind=engine)
    return _session_factory


@contextmanager
def get_db_session():
    """统一的数据库会话上下文管理器

    自动处理会话创建、提交、回滚和关闭

    Yields:
        Session: SQLAlchemy 会话对象

    Example:
        >>> with get_db_session() as session:
        ...     papers = session.query(Paper).all()
    """
    session_factory = _get_session_factory()
    session = session_factory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        logger.error("Database session error, rolled back")
        raise
    finally:
        session.close()
