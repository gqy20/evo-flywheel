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


def test_generate_daily_report_complete(client, paper_factory):
    """测试完整生成每日报告（包含数据库查询和排序）"""
    from datetime import date

    target_date = date.today()

    # 创建测试数据（不同评分）
    paper_factory(
        title="High Score Paper",
        abstract="Important abstract",
        importance_score=95,
        key_findings="Finding 1, Finding 2",
        evolutionary_mechanism="Natural selection",
    )
    paper_factory(title="Medium Score Paper", abstract="Medium abstract", importance_score=75)
    paper_factory(title="Low Score Paper", abstract="Low abstract", importance_score=50)

    # 使用 API 调用生成报告（会使用 test_db）
    response = client.post("/api/v1/reports/generate")
    if response.status_code != 200:
        print("Error:", response.json())
    assert response.status_code == 200
    report = response.json()

    # 验证报告结构
    assert "date" in report
    assert "papers" in report
    assert report["date"] == target_date.isoformat()

    # 验证论文按评分降序排列
    papers = report["papers"]
    assert len(papers) >= 3
    scores = [p["importance_score"] for p in papers if p["importance_score"] is not None]
    assert scores == sorted(scores, reverse=True)

    # 验证高评分论文包含完整分析字段
    high_score_paper = next((p for p in papers if p["importance_score"] == 95), None)
    assert high_score_paper is not None
    assert high_score_paper["title"] == "High Score Paper"
    assert high_score_paper["abstract"] == "Important abstract"
    # key_findings 在测试中是字符串，而不是列表
    assert "Finding 1" in high_score_paper.get("key_findings", "")
    assert high_score_paper.get("evolutionary_mechanism") == "Natural selection"
