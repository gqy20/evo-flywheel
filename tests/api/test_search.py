"""语义搜索端点测试"""

from unittest.mock import Mock, patch


def test_semantic_search_empty_query(client):
    """测试空查询字符串返回错误"""
    response = client.get("/api/v1/search/semantic")
    assert response.status_code == 422  # Validation error


@patch("evo_flywheel.api.v1.search.generate_embedding")
@patch("evo_flywheel.api.v1.search.get_chroma_client")
def test_semantic_search_success(
    mock_chroma_client, mock_generate_embedding, client, paper_factory
):
    """测试语义搜索成功"""
    # Mock embedding 服务
    mock_generate_embedding.return_value = [0.1] * 4096

    # Mock Chroma 客户端
    mock_collection = Mock()
    mock_collection.query.return_value = {
        "ids": [["1", "2"]],
        "documents": [["Abstract 1", "Abstract 2"]],
        "metadatas": [[{"title": "Paper 1"}, {"title": "Paper 2"}]],
        "distances": [[0.1, 0.2]],
    }

    mock_client = Mock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_chroma_client.return_value = mock_client

    # 创建测试数据
    paper_factory(id=1, title="Paper 1", abstract="Abstract 1")
    paper_factory(id=2, title="Paper 2", abstract="Abstract 2")

    response = client.get("/api/v1/search/semantic?q=butterfly evolution")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2


@patch("evo_flywheel.api.v1.search.generate_embedding")
def test_semantic_search_embedding_error(mock_generate_embedding, client):
    """测试 embedding 生成失败"""
    mock_generate_embedding.side_effect = Exception("API error")

    response = client.get("/api/v1/search/semantic?q=test")
    assert response.status_code == 500
    assert "detail" in response.json()


def test_similar_papers(client, paper_factory):
    """测试相似论文推荐"""
    paper = paper_factory(id=1, title="Test Paper", abstract="Test abstract")

    with patch("evo_flywheel.api.v1.search.get_chroma_client") as mock_client:
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [[str(paper.id)]],
            "documents": [[paper.abstract]],
            "metadatas": [[{"title": paper.title}]],
            "distances": [[0.1]],
        }

        mock_cli = Mock()
        mock_cli.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_cli

        response = client.post(f"/api/v1/search/similar?paper_id={paper.id}")
        assert response.status_code == 200
        data = response.json()
        assert "similar_papers" in data


def test_similar_papers_not_found(client):
    """测试相似论文推荐 - 论文不存在"""
    response = client.post("/api/v1/search/similar?paper_id=99999")
    assert response.status_code == 404
