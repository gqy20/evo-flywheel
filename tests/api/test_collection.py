"""采集端点测试"""

from unittest.mock import patch


@patch("evo_flywheel.api.v1.collection.load_rss_sources")
@patch("evo_flywheel.api.v1.collection.collect_from_all_sources")
@patch("evo_flywheel.api.v1.collection.crud.get_paper_by_doi")
@patch("evo_flywheel.api.v1.collection.crud.create_paper")
def test_trigger_fetch(mock_create, mock_get_paper, mock_collect, mock_load_sources, client):
    """测试触发数据采集"""
    # Mock RSS sources
    mock_load_sources.return_value = []

    # Mock collection result (返回 5 篇论文)
    mock_collect.return_value = [
        {
            "title": f"Paper {i}",
            "doi": f"10.1101/2025.{i:05d}",
            "authors": ["Author A"],
            "abstract": f"Abstract {i}",
            "url": f"https://example.com/paper{i}",
            "publication_date": "2025-12-29",
            "journal": "Test Journal",
            "source": "test",
        }
        for i in range(5)
    ]

    # Mock: 所有论文都是新的 (get_paper_by_doi 返回 None)
    mock_get_paper.return_value = None

    response = client.post("/api/v1/collection/fetch?days=7")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert data["new"] == 5


def test_get_collection_status(client):
    """测试获取采集状态"""
    response = client.get("/api/v1/collection/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
