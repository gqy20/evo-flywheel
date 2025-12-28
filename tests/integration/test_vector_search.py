"""向量搜索集成测试

测试向量搜索的端到端功能
"""

from unittest import mock

import pytest


class TestVectorSearchIntegration:
    """向量搜索集成测试"""

    def test_semantic_search_end_to_end_with_text_query(self, monkeypatch):
        """测试端到端语义搜索（文本查询）"""
        # Arrange - Mock Embedding API
        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": [{"embedding": [0.1] * 384}]}
        mock_response.raise_for_status = mock.Mock()

        mock_http_client = mock.Mock()
        mock_http_client.post.return_value = mock_response

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client",
            lambda: mock_http_client,
        )

        # Arrange - Mock Chroma collection
        mock_collection = mock.Mock()
        mock_collection.query.return_value = {
            "ids": [[1, 2, 3]],
            "distances": [[0.1, 0.2, 0.3]],
            "metadatas": [
                [
                    {"title": "Paper 1", "taxa": "Drosophila", "importance_score": 85},
                    {"title": "Paper 2", "taxa": "Drosophila", "importance_score": 90},
                    {"title": "Paper 3", "taxa": "Homo sapiens", "importance_score": 75},
                ]
            ],
            "documents": [["Abstract 1", "Abstract 2", "Abstract 3"]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        # Act
        from evo_flywheel.vector.search import semantic_search_by_text

        results = semantic_search_by_text("evolutionary genetics", n_results=3)

        # Assert - 验证结果格式正确
        assert results["total"] == 3
        assert len(results["results"]) == 3
        assert results["query_metadata"]["query_text"] == "evolutionary genetics"

        # Assert - 验证结果按距离排序
        distances = [r["distance"] for r in results["results"]]
        assert distances == sorted(distances)

    def test_semantic_search_with_metadata_filters(self, monkeypatch):
        """测试带元数据过滤的语义搜索"""
        # Arrange
        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": [{"embedding": [0.1] * 384}]}
        mock_response.raise_for_status = mock.Mock()

        mock_http_client = mock.Mock()
        mock_http_client.post.return_value = mock_response

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client",
            lambda: mock_http_client,
        )

        mock_collection = mock.Mock()
        mock_collection.query.return_value = {
            "ids": [[1]],
            "distances": [[0.15]],
            "metadatas": [[{"title": "High Score Paper", "importance_score": 95}]],
            "documents": [["Abstract"]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        # Act
        from evo_flywheel.vector.search import semantic_search_by_text

        results = semantic_search_by_text("test", min_score=80)

        # Assert - 验证 Chroma 被调用时包含 min_score 过滤
        mock_collection.query.assert_called_once()
        call_kwargs = mock_collection.query.call_args.kwargs
        assert call_kwargs["where"] == {"importance_score": {"$gte": 80}}

    def test_similar_paper_search_excludes_original(self, monkeypatch):
        """测试相似论文搜索排除原论文"""
        # Arrange
        mock_collection = mock.Mock()
        # 获取原论文
        mock_collection.get.return_value = {
            "ids": ["100"],
            "embeddings": [[0.1] * 384],
            "metadatas": [[{"title": "Original"}]],
            "documents": [["Abstract"]],
        }
        # 搜索结果（包含原论文）
        mock_collection.query.return_value = {
            "ids": [[100, 200, 300]],  # 第一个是原论文
            "distances": [[0.0, 0.2, 0.3]],
            "metadatas": [[{"title": "A"}, {"title": "B"}, {"title": "C"}]],
            "documents": [["A1", "B1", "C1"]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        # Act
        from evo_flywheel.vector.search import semantic_search_similar_paper

        results = semantic_search_similar_paper(paper_id=100)

        # Assert - 应该排除原论文（距离为 0 的）
        assert results["total"] == 2  # 只返回 B 和 C
        assert all(r["id"] != "100" for r in results["results"])
        assert all(r["distance"] > 0.001 for r in results["results"])

    def test_hybrid_search_sqlite_plus_chroma(self, monkeypatch):
        """测试混合搜索：SQLite 过滤 + Chroma 排序"""
        # Arrange - Mock SQLite
        mock_filtered_papers = [mock.Mock(id=i) for i in [1, 2, 3, 4, 5]]
        mock_get_papers = mock.Mock(return_value=mock_filtered_papers)

        monkeypatch.setattr("evo_flywheel.vector.hybrid.crud.get_papers", mock_get_papers)

        # Arrange - Mock Chroma
        mock_collection = mock.Mock()
        mock_collection.query.return_value = {
            "ids": [[1, 3, 5]],  # 必须是过滤后的 ID
            "distances": [[0.1, 0.2, 0.3]],
            "metadatas": [[{"title": "A"}, {"title": "C"}, {"title": "E"}]],
            "documents": [["A1", "C1", "E1"]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        query_vector = [0.1] * 384

        # Act
        from evo_flywheel.vector.hybrid import hybrid_search_by_text

        results = hybrid_search_by_text(query_vector, taxa="Drosophila")

        # Assert - 验证 SQLite 被调用过滤
        mock_get_papers.assert_called_once()
        call_kwargs = mock_get_papers.call_args.kwargs
        assert call_kwargs["taxa"] == "Drosophila"

        # Assert - 验证 Chroma 只在过滤后的 IDs 中搜索
        mock_collection.query.assert_called_once()
        query_call_kwargs = mock_collection.query.call_args.kwargs
        assert query_call_kwargs["where"] == {"paper_id": {"$in": ["1", "2", "3", "4", "5"]}}

        # Assert - 验证返回结果正确
        assert results["total"] == 3
        assert results["query_metadata"]["sqlite_filtered"] == 5

    def test_hybrid_search_empty_sqlite_results(self, monkeypatch):
        """测试混合搜索 SQLite 无结果时不调用 Chroma"""
        # Arrange
        mock_get_papers = mock.Mock(return_value=[])
        monkeypatch.setattr("evo_flywheel.vector.hybrid.crud.get_papers", mock_get_papers)

        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        query_vector = [0.1] * 384

        # Act
        from evo_flywheel.vector.hybrid import hybrid_search_by_text

        results = hybrid_search_by_text(query_vector, taxa="Nonexistent")

        # Assert - Chroma 不应该被调用
        mock_collection.query.assert_not_called()
        assert results["total"] == 0
        assert results["results"] == []


class TestVectorSearchAccuracy:
    """向量搜索准确性验证"""

    def test_search_results_include_all_metadata(self, monkeypatch):
        """测试搜索结果包含所有必要的元数据"""
        # Arrange
        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": [{"embedding": [0.1] * 384}]}
        mock_response.raise_for_status = mock.Mock()

        mock_http_client = mock.Mock()
        mock_http_client.post.return_value = mock_response

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client",
            lambda: mock_http_client,
        )

        # 正确的 Chroma 返回格式：metadatas 是一个嵌套列表
        mock_collection = mock.Mock()
        mock_collection.query.return_value = {
            "ids": [[1]],
            "distances": [[0.1]],
            "metadatas": [
                [
                    {
                        "title": "Test Paper",
                        "authors": "Author One",
                        "journal": "Nature",
                        "publication_date": "2024-01-01",
                        "doi": "10.1234/test",
                        "taxa": "Drosophila",
                        "evolutionary_scale": "Population",
                        "research_method": "Phylogenetic",
                        "importance_score": 85,
                    }
                ]
            ],
            "documents": [["Abstract text"]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        # Act
        from evo_flywheel.vector.search import semantic_search_by_text

        results = semantic_search_by_text("test")

        # Assert - 验证所有字段都存在（包括可能为 None 的字段）
        result = results["results"][0]
        assert result["id"] == "1"
        assert result["distance"] == 0.1
        assert result["title"] == "Test Paper"
        assert result["abstract"] == "Abstract text"
        assert result["authors"] == "Author One"
        assert result["journal"] == "Nature"
        assert result["publication_date"] == "2024-01-01"
        assert result["doi"] == "10.1234/test"
        assert result["taxa"] == "Drosophila"
        assert result["evolutionary_scale"] == "Population"
        assert result["research_method"] == "Phylogenetic"
        assert result["importance_score"] == 85

    def test_search_handles_chroma_empty_results(self, monkeypatch):
        """测试 Chroma 返回空结果"""
        # Arrange
        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": [{"embedding": [0.1] * 384}]}
        mock_response.raise_for_status = mock.Mock()

        mock_http_client = mock.Mock()
        mock_http_client.post.return_value = mock_response

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client",
            lambda: mock_http_client,
        )

        mock_collection = mock.Mock()
        mock_collection.query.return_value = {
            "ids": [[]],
            "distances": [[]],
            "metadatas": [[]],
            "documents": [[]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        # Act
        from evo_flywheel.vector.search import semantic_search_by_text

        results = semantic_search_by_text("nonexistent query")

        # Assert
        assert results["total"] == 0
        assert results["results"] == []

    def test_hybrid_search_multiple_filters_combined(self, monkeypatch):
        """测试混合搜索多个过滤条件组合"""
        # Arrange
        mock_filtered_papers = [mock.Mock(id=i) for i in [10, 20, 30]]
        mock_get_papers = mock.Mock(return_value=mock_filtered_papers)

        monkeypatch.setattr("evo_flywheel.vector.hybrid.crud.get_papers", mock_get_papers)

        mock_collection = mock.Mock()
        mock_collection.query.return_value = {
            "ids": [[10, 20]],
            "distances": [[0.15, 0.25]],
            "metadatas": [[{"title": "P1"}, {"title": "P2"}]],
            "documents": [["Abs1", "Abs2"]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        query_vector = [0.1] * 384

        # Act
        from evo_flywheel.vector.hybrid import hybrid_search_by_text

        results = hybrid_search_by_text(
            query_vector, taxa="Homo sapiens", min_score=80, journal="Nature"
        )

        # Assert - 验证所有过滤条件都被传递
        call_kwargs = mock_get_papers.call_args.kwargs
        assert call_kwargs["taxa"] == "Homo sapiens"
        assert call_kwargs["min_importance_score"] == 80
        assert call_kwargs["journal"] == "Nature"
