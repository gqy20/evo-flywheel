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
    """测试获取采集状态（返回真实的 CollectionLog 数据）"""
    response = client.get("/api/v1/collection/status")
    assert response.status_code == 200
    data = response.json()

    # 验证返回真实数据结构
    assert "status" in data
    assert data["status"] in ["idle", "running", "success", "failed"]
    assert "last_collection" in data

    # last_collection 应该是 dict 或 None
    if data["last_collection"] is not None:
        assert isinstance(data["last_collection"], dict)
        assert "status" in data["last_collection"]
        assert "total_papers" in data["last_collection"]
        assert "new_papers" in data["last_collection"]
        assert "sources" in data["last_collection"]
        assert "created_at" in data["last_collection"]


def test_collection_log_model_exists():
    """测试 CollectionLog 模型存在"""
    from evo_flywheel.db.models import CollectionLog

    # 验证模型有必需的字段
    assert hasattr(CollectionLog, "__tablename__")
    assert hasattr(CollectionLog, "id")
    assert hasattr(CollectionLog, "status")
    assert hasattr(CollectionLog, "total_papers")
    assert hasattr(CollectionLog, "new_papers")
    assert hasattr(CollectionLog, "sources")
    assert hasattr(CollectionLog, "error_message")
    assert hasattr(CollectionLog, "created_at")


def test_crud_create_collection_log_exists():
    """测试 crud.create_collection_log 函数存在"""
    from evo_flywheel.db import crud

    # 验证函数存在
    assert hasattr(crud, "create_collection_log")
    assert callable(crud.create_collection_log)
