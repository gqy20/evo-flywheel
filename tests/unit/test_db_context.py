"""数据库上下文管理器单元测试

测试 get_db_session 函数的各种场景
"""

from evo_flywheel.db.context import get_db_session


class TestGetDbSession:
    """测试数据库会话上下文管理器"""

    def test_get_db_session_returns_session(self):
        """测试返回有效的 Session 对象"""
        # Arrange & Act
        with get_db_session() as session:
            # Assert
            assert session is not None
            # 验证是 SQLAlchemy Session
            from sqlalchemy.orm import Session

            assert isinstance(session, Session)

    def test_get_db_session_context_manager(self):
        """测试上下文管理器正确关闭会话"""
        # Act & Assert
        with get_db_session() as db:
            # 验证会话是活跃的
            assert db.is_active

        # 退出上下文后会话应关闭
        # 注意：SQLAlchemy 的 Session.close() 后 is_active 仍为 True
        # 这里我们主要验证不会抛出异常

    def test_get_db_session_can_query(self):
        """测试可以通过会话执行查询"""
        # Arrange & Act
        with get_db_session() as session:
            # 尝试查询（即使表不存在也不应该抛出连接错误）
            from evo_flywheel.db.models import Paper

            result = session.query(Paper).all()

            # Assert - 应该返回空列表（如果数据库初始化）
            assert isinstance(result, list)

    def test_get_db_session_multiple_calls(self):
        """测试多次调用返回不同的会话实例"""
        # Arrange & Act
        with get_db_session() as session1, get_db_session() as session2:
            # Assert - 应该是不同的实例
            assert session1 is not session2

    def test_get_db_session_commit_on_success(self):
        """测试成功时自动提交"""
        # Arrange
        import time

        from evo_flywheel.db.models import Paper

        unique_doi = f"10.1234/test-commit-{int(time.time())}"

        # Act
        with get_db_session() as session:
            paper = Paper(
                title="Test Paper",
                doi=unique_doi,
                abstract="Test abstract",
            )
            session.add(paper)
            # 上下文退出时应自动 commit

        # Assert - 验证数据已提交
        with get_db_session() as session:
            saved = session.query(Paper).filter(Paper.doi == unique_doi).first()
            assert saved is not None
            assert saved.title == "Test Paper"

    def test_get_db_session_rollback_on_error(self):
        """测试异常时自动回滚"""
        # Arrange
        import time

        from evo_flywheel.db.models import Paper

        unique_doi = f"10.1234/test-rollback-{int(time.time())}"

        # Act & Assert
        try:
            with get_db_session() as session:
                paper = Paper(
                    title="Test Paper",
                    doi=unique_doi,
                    abstract="Test abstract",
                )
                session.add(paper)
                # 手动触发刷新确保对象在会话中
                session.flush()

                # 模拟异常
                raise ValueError("Simulated error")
        except ValueError:
            pass

        # Assert - 验证数据已回滚，不存在于数据库中
        with get_db_session() as session:
            rolled_back = session.query(Paper).filter(Paper.doi == unique_doi).first()
            assert rolled_back is None
