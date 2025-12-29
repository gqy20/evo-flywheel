"""报告端点测试"""

from unittest.mock import patch


def test_get_today_report(client, paper_factory):
    """测试获取今日报告"""
    paper_factory(title="Today Paper", importance_score=90)

    response = client.get("/api/v1/reports/today")
    assert response.status_code == 200
    data = response.json()
    assert "date" in data
    assert "papers" in data


def test_get_report_by_date(client, paper_factory):
    """测试获取指定日期报告"""
    response = client.get("/api/v1/reports/2025-12-29")
    assert response.status_code == 200
    data = response.json()
    assert "date" in data


@patch("evo_flywheel.reporters.generator.generate_daily_report")
def test_generate_report(mock_generate, client):
    """测试手动生成报告"""
    mock_generate.return_value = {"date": "2025-12-29", "papers": []}

    response = client.post("/api/v1/reports/generate")
    assert response.status_code == 200
    data = response.json()
    assert "date" in data
