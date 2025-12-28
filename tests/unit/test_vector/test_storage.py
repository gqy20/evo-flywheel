"""向量存储服务单元测试"""

from unittest import mock

import pytest
from evo_flywheel.vector.storage import (
    rebuild_paper_embeddings,
    store_paper_embedding,
    store_papers_batch,
)


class TestStorePaperEmbedding:
    """单个论文向量存储测试"""

    def test_store_single_paper_generates_embedding_and_stores(self, monkeypatch):
        """测试存储单个论文生成向量并存入 Chroma"""
        # Arrange - 模拟 Embedding API 响应
        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}
        mock_response.raise_for_status = mock.Mock()

        mock_http_client = mock.Mock()
        mock_http_client.post.return_value = mock_response

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client",
            lambda: mock_http_client,
        )

        # 模拟 Chroma collection
        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        paper = {
            "id": 123,
            "title": "Test Paper",
            "abstract": "This is a test abstract",
            "authors": "Author One",
            "journal": "Test Journal",
            "publication_date": "2024-01-01",
            "doi": "10.1234/test",
            "taxa": "Drosophila",
            "evolutionary_scale": "Population",
            "importance_score": 85,
        }

        # Act
        store_paper_embedding(paper)

        # Assert - 验证 Embedding API 被调用
        mock_http_client.post.assert_called_once()
        call_kwargs = mock_http_client.post.call_args.kwargs
        assert call_kwargs["json"]["input"] == "This is a test abstract"

        # Assert - 验证 Chroma 存储被调用
        mock_collection.add.assert_called_once()
        add_call = mock_collection.add.call_args.kwargs
        assert add_call["ids"] == ["123"]
        assert add_call["embeddings"] == [[0.1, 0.2, 0.3]]
        assert add_call["documents"] == ["This is a test abstract"]

    def test_store_paper_handles_missing_abstract(self, monkeypatch):
        """测试缺少摘要时的处理"""
        # Arrange
        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        paper = {
            "id": 456,
            "title": "No Abstract Paper",
            # 缺少 abstract
            "authors": "Author Two",
            "journal": "Test Journal",
        }

        # Act & Assert - 应该使用 title 作为 fallback
        store_paper_embedding(paper)

        mock_collection.add.assert_called_once()
        add_call = mock_collection.add.call_args.kwargs
        assert add_call["documents"] == ["No Abstract Paper"]

    def test_store_paper_handles_empty_paper(self, monkeypatch):
        """测试空论文数据的处理"""
        # Arrange
        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        paper = {"id": 789}  # 只有 ID，没有 title 或 abstract

        # Act & Assert - 应该抛出异常或优雅处理
        with pytest.raises(ValueError, match="title|abstract"):
            store_paper_embedding(paper)

        mock_collection.add.assert_not_called()

    def test_store_paper_includes_analysis_metadata(self, monkeypatch):
        """测试存储包含分析元数据"""
        # Arrange
        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": [{"embedding": [0.5]}]}
        mock_response.raise_for_status = mock.Mock()

        mock_http_client = mock.Mock()
        mock_http_client.post.return_value = mock_response

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client",
            lambda: mock_http_client,
        )

        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        paper = {
            "id": 999,
            "title": "Analyzed Paper",
            "abstract": "Abstract with analysis",
            "taxa": "Homo sapiens",
            "evolutionary_scale": "Molecular",
            "research_method": "Phylogenetic",
            "evolutionary_mechanism": "Natural Selection",
            "importance_score": 90,
            "key_findings": ["Finding 1", "Finding 2"],
            "innovation_summary": "Novel approach",
        }

        # Act
        store_paper_embedding(paper)

        # Assert - 验证元数据被正确存储
        add_call = mock_collection.add.call_args.kwargs
        metadata = add_call["metadatas"][0]
        assert metadata["taxa"] == "Homo sapiens"
        assert metadata["evolutionary_scale"] == "Molecular"
        assert metadata["research_method"] == "Phylogenetic"
        assert metadata["evolutionary_mechanism"] == "Natural Selection"
        assert metadata["importance_score"] == 90


class TestStorePapersBatch:
    """批量向量存储测试"""

    def test_batch_stores_multiple_papers(self, monkeypatch):
        """测试批量存储多个论文"""
        # Arrange
        call_count = {"count": 0}

        def mock_post(*args, **kwargs):
            call_count["count"] += 1
            mock_resp = mock.Mock()
            mock_resp.json.return_value = {"data": [{"embedding": [0.1 * call_count["count"]]}]}
            mock_resp.raise_for_status = mock.Mock()
            return mock_resp

        mock_http_client = mock.Mock()
        mock_http_client.post.side_effect = mock_post

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client",
            lambda: mock_http_client,
        )

        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        papers = [
            {"id": 1, "title": "Paper 1", "abstract": "Abstract 1"},
            {"id": 2, "title": "Paper 2", "abstract": "Abstract 2"},
            {"id": 3, "title": "Paper 3", "abstract": "Abstract 3"},
        ]

        # Act
        store_papers_batch(papers)

        # Assert
        assert mock_http_client.post.call_count == 3
        mock_collection.add.assert_called_once()
        add_call = mock_collection.add.call_args.kwargs
        assert len(add_call["ids"]) == 3
        assert add_call["ids"] == ["1", "2", "3"]

    def test_batch_handles_empty_list(self, monkeypatch):
        """测试批量处理空列表"""
        # Arrange
        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        # Act
        store_papers_batch([])

        # Assert
        mock_collection.add.assert_not_called()

    def test_batch_handles_partial_failure(self, monkeypatch):
        """测试批量处理部分失败"""

        # Arrange
        def mock_post(*args, **kwargs):
            json_data = kwargs.get("json", {})
            input_text = json_data.get("input", "")

            if "Paper 2" in input_text:
                raise Exception("API Error for Paper 2")

            mock_resp = mock.Mock()
            mock_resp.json.return_value = {"data": [{"embedding": [0.1]}]}
            mock_resp.raise_for_status = mock.Mock()
            return mock_resp

        mock_http_client = mock.Mock()
        mock_http_client.post.side_effect = mock_post

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client",
            lambda: mock_http_client,
        )

        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        papers = [
            {"id": 1, "title": "Paper 1", "abstract": "Abstract 1"},
            {"id": 2, "title": "Paper 2", "abstract": "Abstract 2"},
            {"id": 3, "title": "Paper 3", "abstract": "Abstract 3"},
        ]

        # Act
        results = store_papers_batch(papers, continue_on_error=True)

        # Assert
        assert results["total"] == 3
        assert results["successful"] == 2
        assert results["failed"] == 1

    def test_batch_skips_already_analyzed(self, monkeypatch):
        """测试批量处理跳过已有向量的论文"""
        # Arrange - 模拟已有向量数据
        mock_collection = mock.Mock()
        mock_collection.get.return_value = ["existing_ids"]  # 已存在

        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        mock_http_client = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client",
            lambda: mock_http_client,
        )

        papers = [{"id": 100, "title": "Existing", "abstract": "Already stored"}]

        # Act
        results = store_papers_batch(papers, skip_existing=True)

        # Assert - 应该跳过已有向量的论文
        assert results["skipped"] == 1
        assert results["successful"] == 0
        mock_http_client.post.assert_not_called()


class TestRebuildPaperEmbeddings:
    """重建向量测试"""

    def test_rebuild_fetches_papers_and_generates_embeddings(self, monkeypatch):
        """测试重建向量从数据库获取论文"""
        # Arrange - 模拟从数据库获取论文
        mock_papers = [
            {"id": 1, "title": "Paper 1", "abstract": "Abstract 1"},
            {"id": 2, "title": "Paper 2", "abstract": "Abstract 2"},
        ]

        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_papers_without_embeddings",
            lambda: mock_papers,
        )

        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": [{"embedding": [0.1]}]}
        mock_response.raise_for_status = mock.Mock()

        mock_http_client = mock.Mock()
        mock_http_client.post.return_value = mock_response

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client",
            lambda: mock_http_client,
        )

        # Act
        result = rebuild_paper_embeddings()

        # Assert
        assert result["total"] == 2
        assert mock_http_client.post.call_count == 2
        mock_collection.add.assert_called_once()

    def test_rebuild_handles_empty_database(self, monkeypatch):
        """测试重建空数据库"""
        # Arrange
        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_papers_without_embeddings",
            lambda: [],
        )

        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        # Act
        result = rebuild_paper_embeddings()

        # Assert
        assert result["total"] == 0
        mock_collection.add.assert_not_called()

    def test_rebuild_clears_existing_embeddings(self, monkeypatch):
        """测试重建前清除现有向量"""
        # Arrange
        mock_papers = [{"id": 1, "title": "P1", "abstract": "A1"}]

        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_papers_without_embeddings",
            lambda: mock_papers,
        )

        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": [{"embedding": [0.1]}]}
        mock_response.raise_for_status = mock.Mock()

        mock_http_client = mock.Mock()
        mock_http_client.post.return_value = mock_response

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client",
            lambda: mock_http_client,
        )

        # Act
        result = rebuild_paper_embeddings(clear_existing=True)

        # Assert - 应该先删除现有数据
        mock_collection.delete.assert_called_once()
        assert result["total"] == 1


class TestStorageErrorHandling:
    """错误处理测试"""

    def test_handles_chroma_connection_error(self, monkeypatch):
        """测试 Chroma 连接错误处理"""
        # Arrange
        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_or_create_collection",
            lambda **kw: (_ for _ in ()).throw(Exception("Connection error")),
        )

        paper = {"id": 1, "title": "Test", "abstract": "Test"}

        # Act & Assert
        with pytest.raises(Exception, match="Connection error"):
            store_paper_embedding(paper)

    def test_handles_embedding_api_failure(self, monkeypatch):
        """测试 Embedding API 失败处理"""
        # Arrange
        mock_http_client = mock.Mock()
        mock_http_client.post.side_effect = Exception("API timeout")

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client",
            lambda: mock_http_client,
        )

        mock_collection = mock.Mock()
        monkeypatch.setattr(
            "evo_flywheel.vector.storage.get_or_create_collection",
            lambda **kw: mock_collection,
        )

        paper = {"id": 1, "title": "Test", "abstract": "Test"}

        # Act & Assert
        with pytest.raises(Exception, match="API timeout"):
            store_paper_embedding(paper)

        mock_collection.add.assert_not_called()
