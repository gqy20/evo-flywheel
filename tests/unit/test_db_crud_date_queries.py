"""日期范围查询功能的单元测试

测试 get_papers_by_date_range 函数的各种场景
"""

from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from evo_flywheel.db.crud import get_papers_by_date_range
from evo_flywheel.db.models import Base


@pytest.fixture
def db_session(temp_db_path):
    """临时数据库会话"""
    engine = create_engine(f"sqlite:///{temp_db_path}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestGetPapersByDateRange:
    """测试日期范围查询论文功能"""

    def test_query_papers_by_single_date(self, db_session):
        """测试查询单日论文（默认行为：end_date = start_date + 1 天）"""
        # Arrange
        from evo_flywheel.db.crud import create_paper

        target_date = date(2024, 12, 28)
        create_paper(
            db_session,
            title="Today Paper",
            importance_score=85,
        )
        # 修改 created_at 为目标日期
        from evo_flywheel.db.models import Paper

        paper = db_session.query(Paper).first()
        paper.created_at = target_date
        db_session.commit()

        # Act
        papers = get_papers_by_date_range(db_session, target_date)

        # Assert
        assert len(papers) == 1
        assert papers[0].title == "Today Paper"

    def test_query_papers_with_date_range(self, db_session):
        """测试指定日期范围查询"""
        # Arrange
        from evo_flywheel.db.crud import create_paper

        # 创建 3 篇不同日期的论文
        for i in range(3):
            paper = create_paper(
                db_session,
                title=f"Paper {i}",
                importance_score=70 + i * 5,
            )
            paper.created_at = date(2024, 12, 26) + timedelta(days=i)
        db_session.commit()

        # Act - 查询 12/27 - 12/29
        start_date = date(2024, 12, 27)
        end_date = date(2024, 12, 29)
        papers = get_papers_by_date_range(db_session, start_date, end_date=end_date)

        # Assert - 应该返回 Paper 1 (12/27) 和 Paper 2 (12/28)
        assert len(papers) == 2
        titles = {p.title for p in papers}
        assert "Paper 1" in titles
        assert "Paper 2" in titles

    def test_query_only_analyzed_papers(self, db_session):
        """测试只返回已分析的论文"""
        # Arrange
        from evo_flywheel.db.crud import create_paper

        target_date = date(2024, 12, 28)
        # 已分析论文
        analyzed_paper = create_paper(
            db_session,
            title="Analyzed Paper",
            importance_score=85,
        )
        analyzed_paper.created_at = target_date
        # 未分析论文
        unanalyzed_paper = create_paper(
            db_session,
            title="Unanalyzed Paper",
            importance_score=None,
        )
        unanalyzed_paper.created_at = target_date
        db_session.commit()

        # Act
        papers = get_papers_by_date_range(db_session, target_date, only_analyzed=True)

        # Assert
        assert len(papers) == 1
        assert papers[0].title == "Analyzed Paper"

    def test_query_with_limit(self, db_session):
        """测试限制返回数量"""
        # Arrange
        from evo_flywheel.db.crud import create_paper

        target_date = date(2024, 12, 28)
        for i in range(5):
            paper = create_paper(
                db_session,
                title=f"Paper {i}",
                importance_score=70 + i * 5,
            )
            paper.created_at = target_date
        db_session.commit()

        # Act
        papers = get_papers_by_date_range(db_session, target_date, limit=3)

        # Assert
        assert len(papers) == 3

    def test_query_order_by_importance_score(self, db_session):
        """测试按重要性评分降序排序"""
        # Arrange
        from evo_flywheel.db.crud import create_paper

        target_date = date(2024, 12, 28)
        scores = [70, 90, 80]
        for score in scores:
            paper = create_paper(
                db_session,
                title=f"Paper {score}",
                importance_score=score,
            )
            paper.created_at = target_date
        db_session.commit()

        # Act
        papers = get_papers_by_date_range(db_session, target_date)

        # Assert - 应该按 90, 80, 70 降序排列
        assert len(papers) == 3
        assert papers[0].importance_score == 90
        assert papers[1].importance_score == 80
        assert papers[2].importance_score == 70

    def test_query_empty_result(self, db_session):
        """测试查询无结果情况"""
        # Arrange
        target_date = date(2024, 12, 28)

        # Act
        papers = get_papers_by_date_range(db_session, target_date)

        # Assert
        assert len(papers) == 0

    def test_query_with_score_filter_combined(self, db_session):
        """测试组合查询：日期范围 + 已分析 + 评分排序"""
        # Arrange
        from evo_flywheel.db.crud import create_paper

        target_date = date(2024, 12, 28)
        # 创建混合数据
        for i in range(4):
            paper = create_paper(
                db_session,
                title=f"Paper {i}",
                importance_score=70 + i * 5 if i < 3 else None,  # Paper 3 无评分
            )
            paper.created_at = target_date
        db_session.commit()

        # Act - 只查询已分析的，限制返回 2 条
        papers = get_papers_by_date_range(
            db_session,
            target_date,
            only_analyzed=True,
            limit=2,
        )

        # Assert - 应该返回评分最高的 2 篇 (80, 75)
        assert len(papers) == 2
        assert papers[0].importance_score == 80
        assert papers[1].importance_score == 75
        assert all(p.importance_score is not None for p in papers)
