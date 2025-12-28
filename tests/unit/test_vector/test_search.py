"""语义搜索服务单元测试"""

from unittest import mock

import pytest
from evo_flywheel.vector.search import (
    semantic_search,
    semantic_search_by_text,
    semantic_search_similar_paper,
)


class TestSemanticSearchByVector:
    """基于向量的语义搜索测试"""

    def test_search_with_query_vector(self, monkeypatch):
        """测试使用查询向量进行语义搜索"""
        # Arrange
        mock_collection = mock.Mock()
        mock_collection.query.return_value = {
            "ids": [[1, 2, 3]],
            "distances": [[0.1, 0.2, 0.3]],
            "metadatas": [[{"title": "Paper 1"}, {"title": "Paper 2"}, {"title": "Paper 3"}]],
            "documents": [["Abstract 1", "Abstract 2", "Abstract 3"]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        query_vector = [0.1] * 384

        # Act
        results = semantic_search(query_vector, n_results=3)

        # Assert
        mock_collection.query.assert_called_once()
        call_kwargs = mock_collection.query.call_args.kwargs
        assert call_kwargs["query_embeddings"] == [query_vector]
        assert call_kwargs["n_results"] == 3

        assert results["total"] == 3
        assert len(results["results"]) == 3
        assert results["results"][0]["id"] == "1"
        assert results["results"][0]["distance"] == 0.1
        assert results["results"][0]["title"] == "Paper 1"

    def test_search_with_metadata_filter(self, monkeypatch):
        """测试带元数据过滤的语义搜索"""
        # Arrange
        mock_collection = mock.Mock()
        mock_collection.query.return_value = {
            "ids": [[1]],
            "distances": [[0.15]],
            "metadatas": [[{"title": "Paper 1", "taxa": "Drosophila"}]],
            "documents": [["Abstract 1"]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        query_vector = [0.1] * 384

        # Act
        results = semantic_search(query_vector, where={"taxa": "Drosophila"})

        # Assert
        call_kwargs = mock_collection.query.call_args.kwargs
        assert call_kwargs["where"] == {"taxa": "Drosophila"}
        assert results["results"][0]["taxa"] == "Drosophila"

    def test_search_returns_empty_when_no_results(self, monkeypatch):
        """测试无结果时的空返回"""
        # Arrange
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
        results = semantic_search(query_vector)

        # Assert
        assert results["total"] == 0
        assert results["results"] == []

    def test_search_handles_invalid_vector_dimension(self, monkeypatch):
        """测试处理无效的向量维度"""
        # Arrange
        mock_collection = mock.Mock()

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        # Act & Assert - 向量维度太小
        with pytest.raises(ValueError, match="向量维度"):
            semantic_search([0.1, 0.2])  # 只有 2 维

    def test_search_formats_results_correctly(self, monkeypatch):
        """测试结果格式化正确"""
        # Arrange
        mock_collection = mock.Mock()
        mock_collection.query.return_value = {
            "ids": [[100, 200]],
            "distances": [[0.5, 0.8]],
            "metadatas": [
                [
                    {"title": "Test", "authors": "A, B", "journal": "Nature"},
                    {"title": "Test 2", "authors": "C", "journal": "Science"},
                ]
            ],
            "documents": [["Abstract", "Abstract 2"]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        query_vector = [0.1] * 384

        # Act
        results = semantic_search(query_vector)

        # Assert - 验证结果格式
        assert "total" in results
        assert "results" in results
        assert "query_metadata" in results

        result = results["results"][0]
        assert "id" in result
        assert "distance" in result
        assert "title" in result
        assert "abstract" in result
        assert "authors" in result
        assert "journal" in result


class TestSemanticSearchByText:
    """基于文本的语义搜索测试"""

    def test_search_by_text_generates_embedding_first(self, monkeypatch):
        """测试文本搜索先生成向量"""
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
            "distances": [[0.2]],
            "metadatas": [[{"title": "Result"}]],
            "documents": [["Abstract"]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        # Act
        results = semantic_search_by_text("evolutionary genetics")

        # Assert - Embedding API 被调用
        mock_http_client.post.assert_called_once()
        call_kwargs = mock_http_client.post.call_args.kwargs
        assert call_kwargs["json"]["input"] == "evolutionary genetics"

        # Assert - Chroma 查询被调用
        mock_collection.query.assert_called_once()
        assert results["total"] == 1

    def test_search_by_text_handles_empty_query(self, monkeypatch):
        """测试处理空查询"""
        # Act & Assert
        with pytest.raises(ValueError, match="查询文本不能为空"):
            semantic_search_by_text("")

    def test_search_by_text_handles_whitespace_query(self, monkeypatch):
        """测试处理纯空格查询"""
        # Act & Assert
        with pytest.raises(ValueError, match="查询文本不能为空"):
            semantic_search_by_text("   ")

    def test_search_by_text_passes_n_results(self, monkeypatch):
        """测试传递结果数量参数"""
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
        semantic_search_by_text("test", n_results=5)

        # Assert
        call_kwargs = mock_collection.query.call_args.kwargs
        assert call_kwargs["n_results"] == 5


class TestSearchSimilarPaper:
    """查找相似论文测试"""

    def test_search_similar_by_paper_id(self, monkeypatch):
        """测试根据论文 ID 查找相似论文"""
        # Arrange - 模拟从 Chroma 获取论文向量
        mock_collection = mock.Mock()
        mock_collection.get.return_value = {
            "ids": ["123"],
            "embeddings": [[0.1] * 384],
            "metadatas": [[{"title": "Original Paper"}]],
            "documents": [["Original Abstract"]],
        }
        # 模拟相似搜索结果
        mock_collection.query.return_value = {
            "ids": [[456, 789]],
            "distances": [[0.2, 0.3]],
            "metadatas": [[{"title": "Similar 1"}, {"title": "Similar 2"}]],
            "documents": [["Abstract 1", "Abstract 2"]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        # Act
        results = semantic_search_similar_paper(paper_id=123, n_results=5)

        # Assert - 先获取原论文向量
        mock_collection.get.assert_called_once_with(ids=["123"])

        # Assert - 再搜索相似论文
        mock_collection.query.assert_called_once()
        assert results["results"][0]["id"] == "456"

    def test_search_similar_excludes_original_paper(self, monkeypatch):
        """测试相似搜索排除原论文"""
        # Arrange
        mock_collection = mock.Mock()
        # 获取原论文
        mock_collection.get.return_value = {
            "ids": ["100"],
            "embeddings": [[0.1] * 384],
            "metadatas": [[{"title": "Original"}]],
            "documents": [["Abstract"]],
        }
        # 搜索结果（可能包含原论文）
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
        results = semantic_search_similar_paper(paper_id=100)

        # Assert - 应该排除原论文（距离为 0 的）
        assert results["total"] == 2  # 只返回 B 和 C
        assert all(r["id"] != "100" for r in results["results"])

    def test_search_similar_handles_nonexistent_paper(self, monkeypatch):
        """测试处理不存在的论文"""
        # Arrange
        mock_collection = mock.Mock()
        mock_collection.get.side_effect = Exception("Paper not found")

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        # Act & Assert
        with pytest.raises(Exception, match="Paper not found"):
            semantic_search_similar_paper(paper_id=999)


class TestSearchErrorHandling:
    """搜索错误处理测试"""

    def test_handles_chroma_query_error(self, monkeypatch):
        """测试 Chroma 查询错误处理"""
        # Arrange
        mock_collection = mock.Mock()
        mock_collection.query.side_effect = Exception("Query failed")

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        query_vector = [0.1] * 384

        # Act & Assert
        with pytest.raises(Exception, match="Query failed"):
            semantic_search(query_vector)

    def test_handles_embedding_generation_failure(self, monkeypatch):
        """测试 Embedding 生成失败处理"""
        # Arrange
        mock_http_client = mock.Mock()
        mock_http_client.post.side_effect = Exception("API Error")

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
        with pytest.raises(Exception, match="API Error"):
            semantic_search_by_text("test query")

        # Chroma 不应该被调用
        mock_collection.query.assert_not_called()


class TestSearchQuality:
    """搜索质量验证测试"""

    def test_results_sorted_by_distance(self, monkeypatch):
        """测试结果按距离排序"""
        # Arrange
        mock_collection = mock.Mock()
        mock_collection.query.return_value = {
            "ids": [[3, 1, 2]],
            "distances": [[0.1, 0.05, 0.15]],  # 未排序
            "metadatas": [[{"title": "C"}, {"title": "A"}, {"title": "B"}]],
            "documents": [["C1", "A1", "B1"]],
        }

        monkeypatch.setattr(
            "evo_flywheel.vector.client.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        query_vector = [0.1] * 384

        # Act
        results = semantic_search(query_vector)

        # Assert - 结果应该按距离升序排列
        distances = [r["distance"] for r in results["results"]]
        assert distances == sorted(distances)

    def test_search_includes_query_metadata(self, monkeypatch):
        """测试搜索包含查询元数据"""
        # Arrange
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
        results = semantic_search(query_vector, min_score=80)

        # Assert
        assert "query_metadata" in results
        assert results["query_metadata"]["min_score"] == 80
