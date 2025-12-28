"""语义搜索服务

整合 Embedding 服务和 Chroma 搜索，提供高层语义搜索接口
"""

from typing import Any

from evo_flywheel.logging import get_logger
from evo_flywheel.vector import client as chroma_client
from evo_flywheel.vector.embeddings import generate_embedding

logger = get_logger(__name__)

# 最小向量维度（384 维，all-MiniLM-L6-v2）
MIN_EMBEDDING_DIM = 384


def _validate_query_vector(vector: list[float]) -> None:
    """验证查询向量

    Args:
        vector: 查询向量

    Raises:
        ValueError: 向量维度不足
    """
    if len(vector) < MIN_EMBEDDING_DIM:
        raise ValueError(f"向量维度不足，至少需要 {MIN_EMBEDDING_DIM} 维")


def _format_search_results(
    chroma_results: dict[str, Any],
    query_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """格式化 Chroma 搜索结果

    Args:
        chroma_results: Chroma 原始返回结果
        query_metadata: 查询元数据

    Returns:
        dict: 格式化后的结果
    """
    # Chroma 返回格式: {"ids": [[id1, id2]], "distances": [[d1, d2]], ...}
    ids = chroma_results.get("ids", [[]])[0]
    distances = chroma_results.get("distances", [[]])[0]
    metadatas = chroma_results.get("metadatas", [[]])[0]
    documents = chroma_results.get("documents", [[]])[0]

    results = []
    for i, paper_id in enumerate(ids):
        metadata = metadatas[i] if i < len(metadatas) else {}
        results.append(
            {
                "id": str(paper_id),
                "distance": float(distances[i]) if i < len(distances) else 0.0,
                "title": metadata.get("title", ""),
                "abstract": documents[i] if i < len(documents) else "",
                "authors": metadata.get("authors", ""),
                "journal": metadata.get("journal", ""),
                "publication_date": metadata.get("publication_date", ""),
                "doi": metadata.get("doi", ""),
                "taxa": metadata.get("taxa"),
                "evolutionary_scale": metadata.get("evolutionary_scale"),
                "research_method": metadata.get("research_method"),
                "importance_score": metadata.get("importance_score"),
            }
        )

    # 按距离排序（升序）
    results.sort(key=lambda x: x["distance"])

    return {
        "total": len(results),
        "results": results,
        "query_metadata": query_metadata or {},
    }


def semantic_search(
    query_vector: list[float],
    n_results: int = 10,
    collection_name: str = chroma_client.DEFAULT_COLLECTION,
    where: dict[str, Any] | None = None,
    min_score: int | None = None,
) -> dict[str, Any]:
    """语义搜索

    Args:
        query_vector: 查询向量
        n_results: 返回结果数量
        collection_name: Chroma collection 名称
        where: 元数据过滤条件
        min_score: 最低重要性评分

    Returns:
        dict: 搜索结果，包含 total, results, query_metadata

    Raises:
        ValueError: 向量维度不足
        Exception: Chroma 查询失败
    """
    _validate_query_vector(query_vector)

    # 添加 min_score 到过滤条件
    filter_where = where.copy() if where else {}
    if min_score is not None:
        filter_where["importance_score"] = {"$gte": min_score}

    logger.debug(f"语义搜索: n_results={n_results}, where={filter_where}")

    collection = chroma_client.get_or_create_collection(name=collection_name)
    chroma_results = collection.query(
        query_embeddings=[query_vector],  # type: ignore[arg-type]
        n_results=n_results,
        where=filter_where if filter_where else None,
    )

    query_metadata = {
        "n_results": n_results,
        "where": filter_where,
        "min_score": min_score,
    }

    results = _format_search_results(chroma_results, query_metadata)  # type: ignore[arg-type]
    logger.info(f"语义搜索完成: 返回 {results['total']} 条结果")

    return results


def semantic_search_by_text(
    query_text: str,
    n_results: int = 10,
    collection_name: str = chroma_client.DEFAULT_COLLECTION,
    where: dict[str, Any] | None = None,
    min_score: int | None = None,
) -> dict[str, Any]:
    """基于文本的语义搜索

    先将查询文本转换为向量，然后进行语义搜索

    Args:
        query_text: 查询文本
        n_results: 返回结果数量
        collection_name: Chroma collection 名称
        where: 元数据过滤条件
        min_score: 最低重要性评分

    Returns:
        dict: 搜索结果

    Raises:
        ValueError: 查询文本为空
        Exception: Embedding 生成或 Chroma 查询失败
    """
    if not query_text or not query_text.strip():
        raise ValueError("查询文本不能为空")

    query_text = query_text.strip()

    logger.debug(f"文本语义搜索: {query_text[:50]}...")

    # 生成查询向量
    query_vector = generate_embedding(query_text)

    # 执行语义搜索
    results = semantic_search(
        query_vector,
        n_results=n_results,
        collection_name=collection_name,
        where=where,
        min_score=min_score,
    )

    # 添加查询文本到元数据
    results["query_metadata"]["query_text"] = query_text

    return results


def semantic_search_similar_paper(
    paper_id: int,
    n_results: int = 5,
    collection_name: str = chroma_client.DEFAULT_COLLECTION,
) -> dict[str, Any]:
    """查找相似论文

    根据给定论文 ID，找到最相似的论文

    Args:
        paper_id: 论文 ID
        n_results: 返回结果数量
        collection_name: Chroma collection 名称

    Returns:
        dict: 相似论文列表，不包含原论文

    Raises:
        Exception: Chroma 查询失败
    """
    logger.debug(f"查找相似论文: paper_id={paper_id}")

    collection = chroma_client.get_or_create_collection(name=collection_name)

    # 获取原论文的向量
    paper_data = collection.get(ids=[str(paper_id)])
    if not paper_data or not paper_data.get("ids"):
        raise ValueError(f"论文 {paper_id} 不存在")

    # 获取向量（Chroma 返回格式可能不同）
    embeddings = paper_data.get("embeddings", [[]])
    if not embeddings or not embeddings[0]:
        raise ValueError(f"论文 {paper_id} 没有向量数据")

    paper_vector = embeddings[0][0]

    # 搜索相似论文
    n_results_plus_one = n_results + 1  # 多取一个，因为可能包含原论文
    chroma_results = collection.query(
        query_embeddings=[paper_vector],  # type: ignore[arg-type]
        n_results=n_results_plus_one,
    )

    # 格式化结果并排除原论文
    formatted = _format_search_results(chroma_results, {"paper_id": paper_id})  # type: ignore[arg-type]

    # 过滤掉原论文（距离为 0 的就是原论文）
    similar_results = [
        r for r in formatted["results"] if r["id"] != str(paper_id) and r["distance"] > 0.001
    ]

    # 限制结果数量
    similar_results = similar_results[:n_results]

    logger.info(f"找到 {len(similar_results)} 篇相似论文")

    return {
        "total": len(similar_results),
        "results": similar_results,
        "query_metadata": {"paper_id": paper_id, "n_results": n_results},
    }
