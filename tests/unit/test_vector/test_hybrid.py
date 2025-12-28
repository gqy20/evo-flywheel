"""混合搜索单元测试

混合搜索 = SQLite 元数据过滤 + Chroma 语义排序
"""

from unittest import mock

import pytest
from evo_flywheel.vector.hybrid import hybrid_search_by_text


class TestHybridSearchByVector:
    """基于向量的混合搜索测试"""

    def test_hybrid_search_filters_by_sqlite_first(self, monkeypatch):
        """测试混合搜索先用 SQLite 过滤"""
        # Arrange - 模拟 SQLite 返回过滤后的 paper_ids
        mock_filtered_ids = [1, 2, 3, 4, 5]

        monkeypatch.setattr(
            "evo_flywheel.vector.hybrid.crud.get_papers",
            lambda **kw: [mock.Mock(id=i) for i in mock_filtered_ids],
        )

        # 模拟 Chroma 语义搜索结果（应该只在这 5 个 paper 中搜索）
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
        hybrid_search_by_text(query_vector, taxa="Drosophila")

        # Assert - 验证 SQLite 被调用过滤
        import evo_flywheel.vector.hybrid as hybrid_module

        hybrid_module.crud.get_papers.assert_called_once()
        call_kwargs = hybrid_module.crud.get_papers.call_args.kwargs
        assert call_kwargs["taxa"] == "Drosophila"

        # Assert - 验证 Chroma 只在过滤后的 IDs 中搜索
        mock_collection.query.assert_called_once()
        query_call_kwargs = mock_collection.query.call_args.kwargs
        assert query_call_kwargs["where"] == {"paper_id": {"$in": ["1", "2", "3", "4", "5"]}}

    def test_hybrid_search_with_multiple_filters(self, monkeypatch):
        """测试混合搜索支持多个过滤条件"""
        # Arrange
        mock_filtered_ids = [10, 20, 30]

        monkeypatch.setattr(
            "evo_flywheel.vector.hybrid.crud.get_papers",
            lambda **kw: [mock.Mock(id=i) for i in mock_filtered_ids],
        )

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
        hybrid_search_by_text(query_vector, taxa="Homo sapiens", min_score=80, journal="Nature")

        # Assert
        import evo_flywheel.vector.hybrid as hybrid_module

        call_kwargs = hybrid_module.crud.get_papers.call_args.kwargs
        assert call_kwargs["taxa"] == "Homo sapiens"
        assert call_kwargs["min_importance_score"] == 80
        assert call_kwargs["journal"] == "Nature"

    def test_hybrid_search_handles_empty_sqlite_results(self, monkeypatch):
        """测试 SQLite 返回空结果"""
        # Arrange
        monkeypatch.setattr("evo_flywheel.vector.hybrid.crud.get_papers", lambda **kw: [])

        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        query_vector = [0.1] * 384

        # Act
        results = hybrid_search_by_text(query_vector, taxa="Nonexistent")

        # Assert - Chroma 不应该被调用
        mock_collection.query.assert_not_called()
        assert results["total"] == 0
        assert results["results"] == []


class TestHybridSearchByText:
    """基于文本的混合搜索测试"""

    def test_hybrid_search_by_text_generates_embedding_first(self, monkeypatch):
        """测试文本混合搜索先生成向量"""
        # Arrange
        mock_filtered_ids = [1, 2]

        monkeypatch.setattr(
            "evo_flywheel.vector.hybrid.crud.get_papers",
            lambda **kw: [mock.Mock(id=i) for i in mock_filtered_ids],
        )

        # Mock Embedding API
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
            "distances": [[0.2]],
            "metadatas": [[{"title": "Result"}]],
            "documents": [["Abstract"]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        # Act
        results = hybrid_search_by_text("evolutionary genetics")

        # Assert - Embedding API 被调用
        mock_http_client.post.assert_called_once()
        call_kwargs = mock_http_client.post.call_args.kwargs
        assert call_kwargs["json"]["input"] == "evolutionary genetics"

        # Assert - Chroma 查询被调用
        mock_collection.query.assert_called_once()
        assert results["total"] == 1


class TestHybridSearchBehavior:
    """混合搜索行为测试"""

    def test_hybrid_search_limits_chroma_results(self, monkeypatch):
        """测试混合搜索限制 Chroma 返回结果数"""
        # Arrange
        mock_filtered_ids = list(range(1, 101))  # 100 篇论文

        monkeypatch.setattr(
            "evo_flywheel.vector.hybrid.crud.get_papers",
            lambda **kw: [mock.Mock(id=i) for i in mock_filtered_ids],
        )

        mock_collection = mock.Mock()
        # Chroma 可能返回更多结果，但应该被限制
        mock_collection.query.return_value = {
            "ids": [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],  # 只取前 10
            "distances": [[0.1] * 10],
            "metadatas": [[{"title": f"P{i}"} for i in range(1, 11)]],
            "documents": [[f"A{i}" for i in range(1, 11)]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        query_vector = [0.1] * 384

        # Act - 只请求 10 个结果
        results = hybrid_search_by_text(query_vector, n_results=10)

        # Assert
        query_call_kwargs = mock_collection.query.call_args.kwargs
        assert query_call_kwargs["n_results"] == 10
        assert results["total"] == 10

    def test_hybrid_search_passes_date_range_filter(self, monkeypatch):
        """测试混合搜索传递日期范围过滤"""
        # Arrange
        monkeypatch.setattr(
            "evo_flywheel.vector.hybrid.crud.get_papers",
            lambda **kw: [mock.Mock(id=1)],
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

        query_vector = [0.1] * 384

        # Act
        hybrid_search_by_text(query_vector, date_from="2024-01-01", date_to="2024-12-31")

        # Assert
        import evo_flywheel.vector.hybrid as hybrid_module

        call_kwargs = hybrid_module.crud.get_papers.call_args.kwargs
        assert call_kwargs["date_from"] == "2024-01-01"
        assert call_kwargs["date_to"] == "2024-12-31"

    def test_hybrid_search_includes_filter_metadata(self, monkeypatch):
        """测试混合搜索结果包含过滤元数据"""
        # Arrange
        monkeypatch.setattr("evo_flywheel.vector.hybrid.crud.get_papers", lambda **kw: [])

        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        query_vector = [0.1] * 384

        # Act
        results = hybrid_search_by_text(
            query_vector,
            taxa="Drosophila",
            min_score=70,
            journal="PLOS Biology",
            date_from="2024-01-01",
        )

        # Assert - 验证查询元数据包含所有过滤条件
        metadata = results["query_metadata"]
        assert metadata["taxa"] == "Drosophila"
        assert metadata["min_score"] == 70
        assert metadata["journal"] == "PLOS Biology"
        assert metadata["date_from"] == "2024-01-01"


class TestHybridSearchErrorHandling:
    """混合搜索错误处理测试"""

    def test_hybrid_search_handles_crud_error(self, monkeypatch):
        """测试 CRUD 错误处理"""
        # Arrange
        monkeypatch.setattr(
            "evo_flywheel.vector.hybrid.crud.get_papers",
            lambda **kw: (_ for _ in ()).throw(Exception("Database error")),
        )

        query_vector = [0.1] * 384

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            hybrid_search_by_text(query_vector)

    def test_hybrid_search_handles_chroma_error(self, monkeypatch):
        """测试 Chroma 查询错误处理"""
        # Arrange - 先让 SQLite 过滤成功
        monkeypatch.setattr(
            "evo_flywheel.vector.hybrid.crud.get_papers",
            lambda **kw: [mock.Mock(id=1)],
        )

        mock_collection = mock.Mock()
        mock_collection.query.side_effect = Exception("Chroma error")

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        query_vector = [0.1] * 384

        # Act & Assert
        with pytest.raises(Exception, match="Chroma error"):
            hybrid_search_by_text(query_vector)

    def test_hybrid_search_handles_embedding_error(self, monkeypatch):
        """测试 Embedding 生成错误处理"""
        # Arrange
        monkeypatch.setattr(
            "evo_flywheel.vector.hybrid.crud.get_papers",
            lambda **kw: [mock.Mock(id=1)],
        )

        mock_http_client = mock.Mock()
        mock_http_client.post.side_effect = Exception("Embedding API error")

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client",
            lambda: mock_http_client,
        )

        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        # Act & Assert
        with pytest.raises(Exception, match="Embedding API error"):
            hybrid_search_by_text("test query")

        # Chroma 不应该被调用
        mock_collection.query.assert_not_called()


class TestHybridSearchOptimization:
    """混合搜索性能优化测试"""

    def test_hybrid_search_limits_sqlite_results(self, monkeypatch):
        """测试 SQLite 限制返回数量"""
        # Arrange
        monkeypatch.setattr(
            "evo_flywheel.vector.hybrid.crud.get_papers",
            lambda **kw: [mock.Mock(id=i) for i in range(100)],
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

        query_vector = [0.1] * 384

        # Act
        hybrid_search_by_text(query_vector)

        # Assert - SQLite 应该有合理的 limit
        import evo_flywheel.vector.hybrid as hybrid_module

        call_kwargs = hybrid_module.crud.get_papers.call_args.kwargs
        assert "limit" in call_kwargs
        assert call_kwargs["limit"] <= 500  # 最多 500 条

    def test_hybrid_search_uses_paper_id_in_chroma(self, monkeypatch):
        """测试 Chroma 使用 paper_id 字段进行过滤"""
        # Arrange
        mock_filtered_ids = [5, 15, 25]

        monkeypatch.setattr(
            "evo_flywheel.vector.hybrid.crud.get_papers",
            lambda **kw: [mock.Mock(id=i) for i in mock_filtered_ids],
        )

        mock_collection = mock.Mock()
        mock_collection.query.return_value = {
            "ids": [[15, 5]],
            "distances": [[0.1, 0.2]],
            "metadatas": [[{"title": "A"}, {"title": "B"}]],
            "documents": [["A1", "B1"]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        query_vector = [0.1] * 384

        # Act
        hybrid_search_by_text(query_vector)

        # Assert - Chroma where 条件应该使用 paper_id 字段
        query_call_kwargs = mock_collection.query.call_args.kwargs
        assert "where" in query_call_kwargs
        assert "paper_id" in query_call_kwargs["where"]
        assert "$in" in query_call_kwargs["where"]["paper_id"]
