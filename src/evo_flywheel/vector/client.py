"""Chroma 向量数据库客户端

使用持久化客户端存储向量数据
"""

from pathlib import Path
from typing import Any

import chromadb

from evo_flywheel.config import get_settings

# 全局 Chroma 客户端实例
_chroma_client: chromadb.ClientAPI | None = None

# 默认 collection 名称
DEFAULT_COLLECTION = "evolutionary_papers"


def get_chroma_client() -> chromadb.ClientAPI:
    """获取 Chroma 客户端单例

    使用持久化客户端存储向量数据

    Returns:
        chromadb.ClientAPI: Chroma 客户端实例
    """
    global _chroma_client

    if _chroma_client is None:
        settings = get_settings()
        persist_dir = Path(settings.chroma_persist_dir)

        # 确保目录存在
        persist_dir.mkdir(parents=True, exist_ok=True)

        # 创建持久化 Chroma 客户端 (新 API)
        _chroma_client = chromadb.PersistentClient(path=str(persist_dir))

    return _chroma_client


def get_or_create_collection(
    name: str = DEFAULT_COLLECTION,
    metadata: dict[str, Any] | None = None,
) -> chromadb.Collection:
    """获取或创建 collection

    Args:
        name: collection 名称
        metadata: collection 元数据

    Returns:
        chromadb.Collection: collection 实例
    """
    client = get_chroma_client()

    if metadata is None:
        metadata = {"description": "进化生物学论文向量库"}

    return client.get_or_create_collection(name=name, metadata=metadata)


def add_paper_embedding(
    paper_id: int,
    embedding: list[float],
    metadata: dict[str, Any],
    document: str,
    collection_name: str = DEFAULT_COLLECTION,
) -> None:
    """添加论文向量到 Chroma

    Args:
        paper_id: 论文 ID (用作 Chroma 中的 ID)
        embedding: 向量嵌入 (384维或1536维)
        metadata: 元数据 (title, authors, journal, taxa, score等)
        document: 论文摘要
        collection_name: collection 名称
    """
    collection = get_or_create_collection(collection_name)

    collection.add(
        ids=[str(paper_id)],
        embeddings=[embedding],
        metadatas=[metadata],
        documents=[document],
    )


def search_similar_papers(
    query_embedding: list[float],
    n_results: int = 10,
    collection_name: str = DEFAULT_COLLECTION,
    where: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """搜索相似论文

    Args:
        query_embedding: 查询向量
        n_results: 返回结果数量
        collection_name: collection 名称
        where: 元数据过滤条件 (如 {"taxa": "Drosophila"})

    Returns:
        dict: 搜索结果，包含 ids, embeddings, metadatas, documents, distances
    """
    collection = get_or_create_collection(collection_name)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where,
    )

    return results


def delete_paper_embedding(
    paper_id: int,
    collection_name: str = DEFAULT_COLLECTION,
) -> None:
    """删除论文向量

    Args:
        paper_id: 论文 ID
        collection_name: collection 名称
    """
    collection = get_or_create_collection(collection_name)
    collection.delete(ids=[str(paper_id)])


def get_paper_count(collection_name: str = DEFAULT_COLLECTION) -> int:
    """获取 collection 中的论文数量

    Args:
        collection_name: collection 名称

    Returns:
        int: 论文数量
    """
    collection = get_or_create_collection(collection_name)
    return collection.count()
