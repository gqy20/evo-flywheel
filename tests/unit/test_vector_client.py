"""Chroma 向量数据库客户端单元测试"""

import pytest


def test_chroma_client_init():
    """测试 Chroma 客户端初始化"""
    # Arrange & Act
    from evo_flywheel.vector.client import get_chroma_client

    client = get_chroma_client()

    # Assert
    assert client is not None


def test_get_or_create_collection():
    """测试获取或创建 collection"""
    # Arrange
    from evo_flywheel.vector.client import get_or_create_collection

    collection_name = "test_papers"

    # Act
    collection = get_or_create_collection(collection_name)

    # Assert
    assert collection is not None
    assert collection.name == collection_name


def test_add_paper_embedding(temp_chroma_dir, monkeypatch):
    """测试添加论文向量"""
    # Arrange
    import evo_flywheel.vector.client as client_module
    client_module._chroma_client = None

    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(temp_chroma_dir))

    from evo_flywheel.vector.client import add_paper_embedding

    paper_id = 123
    embedding = [0.1] * 384  # 384维向量
    metadata = {
        "title": "Test Paper",
        "authors": "Author 1",
        "journal": "Test Journal",
    }
    abstract = "Test abstract"

    # Act
    add_paper_embedding(paper_id, embedding, metadata, abstract)

    # Assert - 验证向量已添加
    from evo_flywheel.vector.client import get_chroma_client

    client = get_chroma_client()
    collection = client.get_collection("test_papers")
    count = collection.count()

    assert count >= 1

    # Cleanup
    client_module._chroma_client = None


def test_search_similar_papers(temp_chroma_dir, monkeypatch):
    """测试语义搜索"""
    # Arrange
    import evo_flywheel.vector.client as client_module
    client_module._chroma_client = None

    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(temp_chroma_dir))

    from evo_flywheel.vector.client import (
        get_chroma_client,
        add_paper_embedding,
        search_similar_papers,
    )

    # 添加测试数据
    client = get_chroma_client()
    collection = client.get_or_create_collection("test_papers")

    collection.add(
        ids=["1"],
        embeddings=[[0.1] * 384],
        metadatas=[{"title": "Test Paper 1"}],
        documents=["Abstract 1"],
    )

    collection.add(
        ids=["2"],
        embeddings=[[0.5] * 384],
        metadatas=[{"title": "Test Paper 2"}],
        documents=["Abstract 2"],
    )

    # Act
    results = search_similar_papers("test_papers", [0.1] * 384, n_results=2)

    # Assert
    assert results is not None
    assert "ids" in results
    assert len(results["ids"]) >= 1

    # Cleanup
    client_module._chroma_client = None
