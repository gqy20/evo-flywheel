"""Embedding 服务单元测试"""

from unittest import mock

import pytest
from evo_flywheel.vector.embeddings import (
    generate_embedding,
    generate_embeddings_batch,
    get_embedding_client,
)


class TestGetEmbeddingClient:
    """Embedding 客户端获取测试"""

    def test_get_client_returns_singleton(self, monkeypatch):
        """测试获取客户端返回单例"""
        # Arrange
        import evo_flywheel.vector.embeddings as embeddings_module

        embeddings_module._client = None

        monkeypatch.setenv("EMBEDDING_API_URL", "http://test.api")
        monkeypatch.setenv("EMBEDDING_API_KEY", "test-key")

        # Act
        client1 = get_embedding_client()
        client2 = get_embedding_client()

        # Assert
        assert client1 is client2

    def test_get_client_requires_api_key(self, monkeypatch):
        """测试缺少 API Key 时抛出异常"""
        # Arrange
        import evo_flywheel.vector.embeddings as embeddings_module

        embeddings_module._client = None
        monkeypatch.delenv("EMBEDDING_API_KEY", raising=False)

        # Act & Assert
        with pytest.raises(ValueError, match="API Key"):
            get_embedding_client()


class TestGenerateEmbedding:
    """单个文本向量化测试"""

    def test_generate_embedding_returns_vector(self, monkeypatch):
        """测试生成单个文本的向量表示"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.encode.return_value = [0.1, 0.2, 0.3, 0.4]

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client", lambda: mock_client
        )

        # Act
        vector = generate_embedding("测试文本")

        # Assert
        assert isinstance(vector, list)
        assert len(vector) == 4
        assert vector == [0.1, 0.2, 0.3, 0.4]
        mock_client.encode.assert_called_once()

    def test_generate_embedding_handles_empty_text(self, monkeypatch):
        """测试处理空文本"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.encode.return_value = []

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client", lambda: mock_client
        )

        # Act & Assert
        with pytest.raises(ValueError, match="文本不能为空"):
            generate_embedding("")

    def test_generate_embedding_handles_api_error(self, monkeypatch):
        """测试处理 API 错误"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.encode.side_effect = Exception("API Error")

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client", lambda: mock_client
        )

        # Act & Assert
        with pytest.raises(Exception, match="API Error"):
            generate_embedding("测试文本")

    def test_generate_embedding_returns_correct_dimensions(self, monkeypatch):
        """测试返回正确维度的向量"""
        # Arrange - 384维向量 (all-MiniLM-L6-v2)
        mock_client = mock.Mock()
        mock_client.encode.return_value = [0.0] * 384

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client", lambda: mock_client
        )

        # Act
        vector = generate_embedding("test")

        # Assert
        assert len(vector) == 384
        assert all(isinstance(x, float) for x in vector)


class TestGenerateEmbeddingsBatch:
    """批量向量化测试"""

    def test_batch_returns_multiple_vectors(self, monkeypatch):
        """测试批量生成多个向量"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.encode.side_effect = [
            [0.1, 0.2],
            [0.3, 0.4],
            [0.5, 0.6],
        ]

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client", lambda: mock_client
        )

        texts = ["文本1", "文本2", "文本3"]

        # Act
        vectors = generate_embeddings_batch(texts)

        # Assert
        assert len(vectors) == 3
        assert vectors[0] == [0.1, 0.2]
        assert vectors[1] == [0.3, 0.4]
        assert vectors[2] == [0.5, 0.6]
        assert mock_client.encode.call_count == 3

    def test_batch_handles_empty_list(self, monkeypatch):
        """测试处理空列表"""
        # Arrange
        mock_client = mock.Mock()

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client", lambda: mock_client
        )

        # Act
        vectors = generate_embeddings_batch([])

        # Assert
        assert vectors == []
        mock_client.encode.assert_not_called()

    def test_batch_handles_partial_failure(self, monkeypatch):
        """测试批量处理部分失败"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.encode.side_effect = [
            [0.1, 0.2],  # 成功
            Exception("API Error"),  # 失败
            [0.5, 0.6],  # 成功
        ]

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client", lambda: mock_client
        )

        texts = ["文本1", "文本2", "文本3"]

        # Act
        vectors = generate_embeddings_batch(texts, continue_on_error=True)

        # Assert
        assert len(vectors) == 3
        assert vectors[0] == [0.1, 0.2]
        assert vectors[1] is None  # 失败的返回 None
        assert vectors[2] == [0.5, 0.6]

    def test_batch_limits_concurrent_requests(self, monkeypatch):
        """测试批量处理限制并发数"""
        # Arrange
        call_count = {"count": 0}

        def mock_encode(text):
            call_count["count"] += 1
            return [0.1] * 384

        mock_client = mock.Mock()
        mock_client.encode.side_effect = mock_encode

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client", lambda: mock_client
        )

        texts = ["文本"] * 10

        # Act
        vectors = generate_embeddings_batch(texts, max_concurrent=2)

        # Assert
        assert len(vectors) == 10
        assert call_count["count"] == 10
        assert all(v is not None for v in vectors)


class TestEmbeddingQuality:
    """Embedding 质量验证测试"""

    def test_embedding_values_normalized(self, monkeypatch):
        """测试向量值是否归一化"""
        # Arrange
        mock_client = mock.Mock()
        # 模拟归一化的向量
        mock_client.encode.return_value = [0.5, -0.5, 0.707, -0.707]

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client", lambda: mock_client
        )

        # Act
        vector = generate_embedding("test")

        # Assert - 验证向量长度接近 1 (归一化)
        import math

        norm = math.sqrt(sum(x * x for x in vector))
        assert 0.9 < norm <= 1.1  # 允许小的浮点误差

    def test_embedding_consistent_for_same_text(self, monkeypatch):
        """测试相同文本生成一致的向量"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.encode.return_value = [0.1] * 384

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client", lambda: mock_client
        )

        # Act
        text = "相同文本"
        vector1 = generate_embedding(text)
        vector2 = generate_embedding(text)

        # Assert
        assert vector1 == vector2

    def test_embedding_different_for_different_texts(self, monkeypatch):
        """测试不同文本生成不同的向量"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.encode.side_effect = [
            [0.1] * 384,
            [0.2] * 384,
        ]

        monkeypatch.setattr(
            "evo_flywheel.vector.embeddings.get_embedding_client", lambda: mock_client
        )

        # Act
        vector1 = generate_embedding("文本1")
        vector2 = generate_embedding("文本2")

        # Assert
        assert vector1 != vector2
