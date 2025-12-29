"""数据库模型单元测试"""


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


def test_daily_report_multiple_same_day_allowed(db_session):
    """测试同一天允许多份报告（飞轮每4小时运行一次）

    场景：飞轮在 00:00, 04:00, 08:00 各运行一次，应生成3份独立报告

    Arrange: 准备数据库会话和相同日期
    Act: 在同一天创建3份报告
    Assert: 应成功创建，每份有独立 ID 和 created_at
    """
    # Arrange
    import time

    from evo_flywheel.db.models import DailyReport

    report_date = "2025-12-29"

    # Act - 创建第一份报告 (00:00)
    report1 = DailyReport(
        report_date=report_date,
        total_papers=36,
        high_value_papers=5,
        report_content='{"summary": "00:00 run"}',
    )
    report1.top_papers_list = [1, 2, 3]  # 使用 setter
    db_session.add(report1)
    db_session.commit()

    time.sleep(0.01)  # 确保 created_at 不同

    # 创建第二份报告 (04:00)
    report2 = DailyReport(
        report_date=report_date,
        total_papers=48,
        high_value_papers=7,
        report_content='{"summary": "04:00 run"}',
    )
    report2.top_papers_list = [1, 2, 3, 4]
    db_session.add(report2)
    db_session.commit()

    time.sleep(0.01)

    # 创建第三份报告 (08:00)
    report3 = DailyReport(
        report_date=report_date,
        total_papers=56,
        high_value_papers=9,
        report_content='{"summary": "08:00 run"}',
    )
    report3.top_papers_list = [1, 2, 3, 4, 5]
    db_session.add(report3)
    db_session.commit()

    # Assert - 验证三份报告都成功创建
    assert report1.id is not None
    assert report2.id is not None
    assert report3.id is not None

    # 验证 ID 不同
    assert report1.id != report2.id
    assert report2.id != report3.id

    # 验证 created_at 不同
    assert report1.created_at != report2.created_at
    assert report2.created_at != report3.created_at

    # 验证查询同一天能返回多份报告
    reports = (
        db_session.query(DailyReport)
        .filter(DailyReport.report_date == report_date)
        .order_by(DailyReport.created_at)
        .all()
    )

    assert len(reports) == 3
    assert reports[0].total_papers == 36
    assert reports[1].total_papers == 48
    assert reports[2].total_papers == 56
