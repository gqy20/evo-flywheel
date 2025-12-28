"""混合搜索服务

混合搜索 = SQLite 元数据过滤 + Chroma 语义排序
"""

from typing import Any

from evo_flywheel.db import crud
from evo_flywheel.logging import get_logger
from evo_flywheel.vector import client as chroma_client
from evo_flywheel.vector.embeddings import generate_embedding
from evo_flywheel.vector.search import _format_search_results

logger = get_logger(__name__)

# SQLite 最大返回数量（避免过多数据）
MAX_SQLITE_RESULTS = 500


def hybrid_search(
    query_vector: list[float],
    taxa: str | None = None,
    min_score: int | None = None,
    journal: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    n_results: int = 10,
    collection_name: str = chroma_client.DEFAULT_COLLECTION,
) -> dict[str, Any]:
    """混合搜索（基于向量）

    先用 SQLite 过滤元数据，再用 Chroma 进行语义排序

    Args:
        query_vector: 查询向量
        taxa: 物种过滤
        min_score: 最低重要性评分
        journal: 期刊过滤
        date_from: 起始日期
        date_to: 结束日期
        n_results: 返回结果数量
        collection_name: Chroma collection 名称

    Returns:
        dict: 搜索结果，包含 total, results, query_metadata

    Raises:
        Exception: SQLite 查询或 Chroma 查询失败
    """
    # Step 1: 用 SQLite 过滤元数据
    filter_metadata = {
        "taxa": taxa,
        "min_importance_score": min_score,
        "journal": journal,
        "date_from": date_from,
        "date_to": date_to,
        "limit": MAX_SQLITE_RESULTS,
    }

    # 移除 None 值
    filter_metadata = {k: v for k, v in filter_metadata.items() if v is not None}

    logger.debug(f"混合搜索 SQLite 过滤: {filter_metadata}")

    papers = crud.get_papers(**filter_metadata)  # type: ignore[arg-type]

    if not papers:
        logger.info("SQLite 过滤后无结果")
        return {
            "total": 0,
            "results": [],
            "query_metadata": {
                "taxa": taxa,
                "min_score": min_score,
                "journal": journal,
                "date_from": date_from,
                "date_to": date_to,
                "n_results": n_results,
                "sqlite_filtered": 0,
            },
        }

    paper_ids = [str(p.id) for p in papers]
    logger.info(f"SQLite 过滤后剩余 {len(paper_ids)} 篇论文")

    # Step 2: 用 Chroma 在过滤结果中进行语义搜索
    collection = chroma_client.get_or_create_collection(name=collection_name)

    # Chroma 的 where 语法：{"paper_id": {"$in": ["1", "2", "3"]}}
    chroma_where = {"paper_id": {"$in": paper_ids}}

    chroma_results = collection.query(
        query_embeddings=[query_vector],  # type: ignore[arg-type]
        n_results=n_results,
        where=chroma_where,  # type: ignore[arg-type]
    )

    # Step 3: 格式化结果
    query_metadata = {
        "taxa": taxa,
        "min_score": min_score,
        "journal": journal,
        "date_from": date_from,
        "date_to": date_to,
        "n_results": n_results,
        "sqlite_filtered": len(paper_ids),
    }

    results = _format_search_results(chroma_results, query_metadata)  # type: ignore[arg-type]
    logger.info(f"混合搜索完成: SQLite 过滤 {len(paper_ids)} 篇, 返回 {results['total']} 篇")

    return results


def hybrid_search_by_text(
    query: str | list[float],
    taxa: str | None = None,
    min_score: int | None = None,
    journal: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    n_results: int = 10,
    collection_name: str = chroma_client.DEFAULT_COLLECTION,
) -> dict[str, Any]:
    """混合搜索（基于文本或向量）

    如果输入是文本，先生成查询向量，然后执行混合搜索

    Args:
        query: 查询文本或向量
        taxa: 物种过滤
        min_score: 最低重要性评分
        journal: 期刊过滤
        date_from: 起始日期
        date_to: 结束日期
        n_results: 返回结果数量
        collection_name: Chroma collection 名称

    Returns:
        dict: 搜索结果

    Raises:
        ValueError: 查询文本为空
        Exception: Embedding 生成、SQLite 查询或 Chroma 查询失败
    """
    # 处理向量输入
    if isinstance(query, list):
        query_vector = query
        query_text = None
    else:
        # 处理文本输入
        if not query or not query.strip():
            raise ValueError("查询文本不能为空")
        query_text = query.strip()
        logger.debug(f"文本混合搜索: {query_text[:50]}...")
        # 生成查询向量
        query_vector = generate_embedding(query_text)

    # 执行混合搜索
    results = hybrid_search(
        query_vector,
        taxa=taxa,
        min_score=min_score,
        journal=journal,
        date_from=date_from,
        date_to=date_to,
        n_results=n_results,
        collection_name=collection_name,
    )

    # 添加查询文本到元数据（如果有）
    if query_text:
        results["query_metadata"]["query_text"] = query_text

    return results
