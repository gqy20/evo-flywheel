"""数据库 CRUD 操作单元测试"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from evo_flywheel.db.crud import (
    create_daily_report,
    create_feedback,
    create_paper,
    delete_paper,
    get_daily_report_by_date,
    get_paper_by_doi,
    get_paper_by_id,
    get_papers,
    update_paper,
)
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


class TestPaperCRUD:
    """论文 CRUD 操作测试"""

    def test_create_paper(self, db_session):
        """测试创建论文"""
        # Arrange
        paper_data = {
            "title": "Test Paper",
            "authors": ["Author 1", "Author 2"],
            "abstract": "Test abstract",
            "doi": "10.1234/test",
            "url": "https://example.com/paper",
            "publication_date": "2024-12-28",
            "journal": "Test Journal",
            "source": "test_source",
        }

        # Act
        paper = create_paper(db_session, **paper_data)

        # Assert
        assert paper.id is not None
        assert paper.title == "Test Paper"
        assert paper.doi == "10.1234/test"

    def test_get_paper_by_id(self, db_session):
        """测试根据 ID 获取论文"""
        # Arrange
        paper = create_paper(
            db_session,
            title="Test Paper",
            doi="10.1234/test",
        )

        # Act
        found_paper = get_paper_by_id(db_session, paper.id)

        # Assert
        assert found_paper is not None
        assert found_paper.id == paper.id
        assert found_paper.title == "Test Paper"

    def test_get_paper_by_doi(self, db_session):
        """测试根据 DOI 获取论文"""
        # Arrange
        create_paper(
            db_session,
            title="Test Paper",
            doi="10.1234/test",
        )

        # Act
        found_paper = get_paper_by_doi(db_session, "10.1234/test")

        # Assert
        assert found_paper is not None
        assert found_paper.doi == "10.1234/test"

    def test_get_papers_with_filters(self, db_session):
        """测试获取论文列表（带过滤）"""
        # Arrange - 创建多个论文
        create_paper(
            db_session,
            title="Paper 1",
            journal="Nature",
            importance_score=85,
        )
        create_paper(
            db_session,
            title="Paper 2",
            journal="Science",
            importance_score=70,
        )
        db_session.commit()

        # Act - 获取所有论文
        papers = get_papers(db_session)

        # Assert
        assert len(papers) == 2

        # Act - 按期刊过滤
        nature_papers = get_papers(db_session, journal="Nature")

        # Assert
        assert len(nature_papers) == 1
        assert nature_papers[0].journal == "Nature"

    def test_update_paper(self, db_session):
        """测试更新论文"""
        # Arrange
        paper = create_paper(
            db_session,
            title="Original Title",
            importance_score=None,
        )

        # Act
        updated = update_paper(
            db_session,
            paper.id,
            title="Updated Title",
            importance_score=90,
        )

        # Assert
        assert updated.title == "Updated Title"
        assert updated.importance_score == 90

    def test_delete_paper(self, db_session):
        """测试删除论文"""
        # Arrange
        paper = create_paper(
            db_session,
            title="To Delete",
        )

        # Act
        delete_paper(db_session, paper.id)

        # Assert
        deleted = get_paper_by_id(db_session, paper.id)
        assert deleted is None


class TestDailyReportCRUD:
    """每日报告 CRUD 操作测试"""

    def test_create_daily_report(self, db_session):
        """测试创建每日报告"""
        # Arrange
        paper = create_paper(
            db_session,
            title="Test Paper",
            importance_score=85,
        )

        # Act
        report = create_daily_report(
            db_session,
            report_date="2024-12-28",
            total_papers=1,
            high_value_papers=1,
            top_paper_ids=[paper.id],
            report_content="# Test Report",
        )

        # Assert
        assert report.id is not None
        assert report.report_date == "2024-12-28"
        assert report.total_papers == 1

    def test_get_daily_report_by_date(self, db_session):
        """测试根据日期获取报告"""
        # Arrange
        create_daily_report(
            db_session,
            report_date="2024-12-28",
            total_papers=10,
        )

        # Act
        report = get_daily_report_by_date(db_session, "2024-12-28")

        # Assert
        assert report is not None
        assert report.report_date == "2024-12-28"
        assert report.total_papers == 10


class TestFeedbackCRUD:
    """反馈 CRUD 操作测试"""

    def test_create_feedback(self, db_session):
        """测试创建反馈"""
        # Arrange
        paper = create_paper(db_session, title="Test Paper")

        # Act
        feedback = create_feedback(
            db_session,
            paper_id=paper.id,
            rating=5,
            is_helpful=True,
            comment="Great!",
        )

        # Assert
        assert feedback.id is not None
        assert feedback.rating == 5
        assert feedback.paper_id == paper.id
