"""统计端点测试"""


def test_get_overview_stats(client, paper_factory):
    """测试获取系统概览统计"""
    paper_factory(title="Paper 1")
    paper_factory(title="Paper 2")

    response = client.get("/api/v1/stats/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_papers" in data
    assert "analyzed_papers" in data
    assert data["total_papers"] >= 2


def test_health_check(client):
    """测试健康检查"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
