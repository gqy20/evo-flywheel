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


@patch("evo_flywheel.api.v1.collection.load_rss_sources")
@patch("evo_flywheel.api.v1.collection.collect_from_all_sources")
def test_trigger_fetch_with_sources_filter(mock_collect, mock_load_sources, client):
    """测试 sources 参数过滤数据源"""
    # Mock RSS 源
    all_sources = [
        {"name": "biorxiv_api", "url": "...", "source_type": "api"},
        {"name": "arxiv", "url": "...", "source_type": "rss"},
        {"name": "plos", "url": "...", "source_type": "rss"},
    ]
    mock_load_sources.return_value = all_sources

    # Mock 采集结果
    mock_collect.return_value = [
        {
            "title": "Filtered Paper",
            "doi": "10.1101/2025.00001",
            "authors": ["Author"],
            "abstract": "Abstract",
            "url": "https://example.com/1",
            "publication_date": "2025-12-29",
            "journal": "Test Journal",
            "source": "biorxiv_api",
        }
    ]

    # 请求指定 sources 参数 - 只要 biorxiv_api 和 arxiv
    response = client.post("/api/v1/collection/fetch?days=7&sources=biorxiv_api,arxiv")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1

    # 验证 collect_from_all_sources 被调用时传入了过滤后的 rss_sources
    mock_collect.assert_called_once()
    call_args = mock_collect.call_args
    rss_sources_arg = call_args.kwargs.get("rss_sources")

    # 验证 rss_sources 被过滤
    assert rss_sources_arg is not None
    source_names = [s.get("name") for s in rss_sources_arg]

    # 应该只包含 biorxiv_api 和 arxiv，不包含 plos
    assert len(source_names) == 2
    assert "biorxiv_api" in source_names
    assert "arxiv" in source_names
    assert "plos" not in source_names


@patch("evo_flywheel.api.v1.collection.load_rss_sources")
@patch("evo_flywheel.api.v1.collection.collect_from_all_sources")
@patch("evo_flywheel.api.v1.collection.crud.get_paper_by_doi")
@patch("evo_flywheel.api.v1.collection.crud.create_paper")
def test_trigger_fetch_single_source(
    mock_create, mock_get_paper, mock_collect, mock_load_sources, client
):
    """测试单个数据源过滤"""
    mock_load_sources.return_value = [
        {"name": "biorxiv_api", "url": "...", "source_type": "api"},
        {"name": "arxiv", "url": "...", "source_type": "rss"},
    ]

    mock_collect.return_value = [
        {"title": "Paper", "doi": "10.1101/2025.00001", "source": "biorxiv_api"}
    ]
    mock_get_paper.return_value = None

    response = client.post("/api/v1/collection/fetch?days=7&sources=biorxiv_api")
    assert response.status_code == 200

    # 验证只使用了 biorxiv_api
    mock_collect.assert_called_once()
    call_args = mock_collect.call_args
    rss_sources = call_args.kwargs.get("rss_sources", [])
    source_names = [s.get("name") for s in rss_sources]

    # 应该只有 biorxiv_api
    assert "biorxiv_api" in source_names
