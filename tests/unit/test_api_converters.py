"""API 响应转换器单元测试

测试 daily_report_to_response 函数的各种场景
"""

import json
from datetime import datetime

import pytest
from evo_flywheel.api.converters import daily_report_to_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from evo_flywheel.db.crud import create_daily_report, create_paper
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


class TestDailyReportToResponse:
    """测试 DailyReport 转 DeepReportDetailResponse"""

    def test_convert_valid_report(self, db_session):
        """测试转换有效报告"""
        # Arrange
        paper = create_paper(
            db_session,
            title="Test Paper",
            importance_score=85,
        )
        report = create_daily_report(
            db_session,
            report_date="2024-12-28",
            total_papers=1,
            high_value_papers=1,
            top_paper_ids=[paper.id],
            report_content='{"research_summary": "测试摘要"}',
        )

        # Act
        response = daily_report_to_response(report)

        # Assert
        assert response.id == report.id
        assert response.report_date == "2024-12-28"
        assert response.total_papers == 1
        assert response.high_value_papers == 1
        assert response.top_paper_ids == [paper.id]
        assert response.content == {"research_summary": "测试摘要"}

    def test_convert_with_json_content(self, db_session):
        """测试带 JSON 内容的报告转换"""
        # Arrange
        content_dict = {
            "research_summary": "今日研究概要",
            "hot_topics": ["进化机制", "遗传变异"],
            "trend_analysis": {"direction": "上升"},
            "recommended_papers": [],
            "top_paper_ids": [1, 2, 3],
        }
        report = create_daily_report(
            db_session,
            report_date="2024-12-28",
            total_papers=10,
            high_value_papers=3,
            top_paper_ids=[1, 2, 3],
            report_content=json.dumps(content_dict, ensure_ascii=False),
        )

        # Act
        response = daily_report_to_response(report)

        # Assert
        assert response.content == content_dict

    def test_convert_with_invalid_json_content(self, db_session):
        """测试带无效 JSON 内容的报告转换（降级处理）"""
        # Arrange
        report = create_daily_report(
            db_session,
            report_date="2024-12-28",
            total_papers=5,
            high_value_papers=2,
            top_paper_ids=[1, 2],
            report_content="invalid json { content",
        )

        # Act
        response = daily_report_to_response(report)

        # Assert
        assert response.content == {"raw": "invalid json { content"}

    def test_convert_with_none_content(self, db_session):
        """测试内容为 None 的报告转换"""
        # Arrange
        report = create_daily_report(
            db_session,
            report_date="2024-12-28",
            total_papers=0,
            high_value_papers=0,
            top_paper_ids=[],
            report_content=None,
        )

        # Act
        response = daily_report_to_response(report)

        # Assert
        assert response.content == {}

    def test_convert_with_empty_content(self, db_session):
        """测试内容为空字符串的报告转换"""
        # Arrange
        report = create_daily_report(
            db_session,
            report_date="2024-12-28",
            total_papers=0,
            high_value_papers=0,
            top_paper_ids=[],
            report_content="",
        )

        # Act
        response = daily_report_to_response(report)

        # Assert
        assert response.content == {}

    def test_convert_with_pre_parsed_content(self, db_session):
        """测试传入已解析的内容（避免重复解析）"""
        # Arrange
        paper = create_paper(
            db_session,
            title="Test Paper",
            importance_score=85,
        )
        report = create_daily_report(
            db_session,
            report_date="2024-12-28",
            total_papers=1,
            high_value_papers=1,
            top_paper_ids=[paper.id],
            report_content='{"research_summary": "测试摘要"}',
        )
        pre_parsed_content = {"custom": "content", "research_summary": "覆盖内容"}

        # Act
        response = daily_report_to_response(report, content=pre_parsed_content)

        # Assert
        assert response.content == pre_parsed_content

    def test_convert_created_at_format(self, db_session):
        """测试 created_at 字段格式化为 ISO 字符串"""
        # Arrange
        report = create_daily_report(
            db_session,
            report_date="2024-12-28",
            total_papers=1,
            high_value_papers=1,
        )
        # 确保 created_at 有值
        assert report.created_at is not None

        # Act
        response = daily_report_to_response(report)

        # Assert
        assert isinstance(response.created_at, str)
        # 验证是有效的 ISO 格式
        datetime.fromisoformat(response.created_at)
