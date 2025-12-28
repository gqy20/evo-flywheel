"""数据库模型单元测试"""


# 测试先写在这里，这些测试会失败因为模型还没创建


def test_paper_model_create():
    """测试论文模型创建"""
    # Arrange
    from evo_flywheel.db.models import Paper

    # Act
    paper = Paper(
        title="Test Paper",
        authors=["Author 1", "Author 2"],
        abstract="Test abstract",
        doi="10.1234/test",
        url="https://example.com/paper",
        publication_date="2024-12-28",
        journal="Test Journal",
        source="test_source",
    )

    # Assert
    assert paper.title == "Test Paper"
    assert paper.authors == ["Author 1", "Author 2"]
    assert paper.doi == "10.1234/test"
    assert paper.importance_score is None  # 默认值


def test_daily_report_model_create():
    """测试每日报告模型创建"""
    # Arrange
    from evo_flywheel.db.models import DailyReport

    # Act
    report = DailyReport(
        report_date="2024-12-28",
        total_papers=10,
        high_value_papers=3,
        top_paper_ids=[1, 2, 3],
        report_content="# Test Report\n",
    )

    # Assert
    assert report.report_date == "2024-12-28"
    assert report.total_papers == 10
    assert report.high_value_papers == 3


def test_feedback_model_create():
    """测试反馈模型创建"""
    # Arrange
    from evo_flywheel.db.models import Feedback

    # Act
    feedback = Feedback(
        paper_id=1,
        rating=5,
        is_helpful=True,
        comment="Great paper!",
    )

    # Assert
    assert feedback.paper_id == 1
    assert feedback.rating == 5
    assert feedback.is_helpful is True
