"""向量存储服务

整合 Embedding 服务和 Chroma 客户端，提供向量存储高层接口
"""

from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from evo_flywheel.db import crud
from evo_flywheel.logging import get_logger
from evo_flywheel.vector import client as chroma_client
from evo_flywheel.vector.embeddings import generate_embedding, generate_embeddings_batch

logger = get_logger(__name__)


def _extract_text_for_embedding(paper: dict[str, Any]) -> str:
    """提取用于向量化的文本

    Args:
        paper: 论文数据字典

    Returns:
        str: 用于向量化的文本（摘要优先，标题作为 fallback）

    Raises:
        ValueError: 既没有摘要也没有标题
    """
    # 优先使用摘要
    abstract = paper.get("abstract") or ""
    if abstract and abstract.strip():
        return abstract.strip()

    # Fallback 到标题
    title = paper.get("title") or ""
    if title and title.strip():
        return title.strip()

    raise ValueError("论文必须包含 abstract 或 title 字段")


def _build_metadata(paper: dict[str, Any]) -> dict[str, Any]:
    """构建 Chroma 元数据

    Args:
        paper: 论文数据字典

    Returns:
        dict: 元数据字典
    """
    metadata = {
        "title": paper.get("title", ""),
        "authors": paper.get("authors", ""),
        "journal": paper.get("journal", ""),
        "publication_date": paper.get("publication_date", ""),
        "doi": paper.get("doi", ""),
    }

    # 添加分析字段（如果存在）
    optional_fields = [
        "taxa",
        "evolutionary_scale",
        "research_method",
        "evolutionary_mechanism",
        "importance_score",
    ]
    for field in optional_fields:
        value = paper.get(field)
        if value is not None:
            metadata[field] = value

    return metadata


def store_paper_embedding(
    paper: dict[str, Any],
    collection_name: str = chroma_client.DEFAULT_COLLECTION,
) -> None:
    """存储单个论文向量

    Args:
        paper: 论文数据字典，必须包含 id 和 abstract/title
        collection_name: Chroma collection 名称

    Raises:
        ValueError: 论文缺少必要字段
        Exception: Embedding API 或 Chroma 存储失败
    """
    paper_id = paper.get("id")
    if not paper_id:
        raise ValueError("论文必须包含 id 字段")

    # 提取向量化文本
    text = _extract_text_for_embedding(paper)

    logger.debug(f"为论文 {paper_id} 生成向量: {text[:50]}...")

    # 生成向量
    embedding = generate_embedding(text)

    # 构建元数据
    metadata = _build_metadata(paper)

    # 存储到 Chroma
    collection = chroma_client.get_or_create_collection(name=collection_name)
    collection.add(
        ids=[str(paper_id)],
        embeddings=[embedding],  # type: ignore[arg-type]
        metadatas=[metadata],  # type: ignore[arg-type]
        documents=[text],
    )

    logger.info(f"论文 {paper_id} 向量已存储")


def store_papers_batch(
    papers: list[dict[str, Any]],
    collection_name: str = chroma_client.DEFAULT_COLLECTION,
    max_concurrent: int = 5,
    continue_on_error: bool = False,
    skip_existing: bool = False,
) -> dict[str, int]:
    """批量存储论文向量

    Args:
        papers: 论文数据列表
        collection_name: Chroma collection 名称
        max_concurrent: 最大并发数
        continue_on_error: 遇到错误是否继续
        skip_existing: 是否跳过已有向量的论文

    Returns:
        dict: 处理统计 {"total": int, "successful": int, "failed": int, "skipped": int}
    """
    if not papers:
        return {"total": 0, "successful": 0, "failed": 0, "skipped": 0}

    total = len(papers)
    successful = 0
    failed = 0
    skipped = 0

    # 获取 collection
    collection = chroma_client.get_or_create_collection(name=collection_name)

    # 如果启用 skip_existing，过滤已有向量的论文
    papers_to_process = papers
    if skip_existing:
        existing_ids: set[str] = set()
        try:
            # 批量检查已有 ID
            all_ids = [str(p["id"]) for p in papers if p.get("id")]
            if all_ids:
                # Chroma 没有直接的批量检查方法，这里简化为逐个检查
                for paper_id in all_ids:
                    try:
                        collection.get(ids=[paper_id])
                        existing_ids.add(paper_id)
                    except Exception:  # nosec: ID 不存在是预期行为
                        # ID 不存在，这是预期的行为
                        pass
        except Exception as e:
            logger.warning(f"检查已有向量时出错: {e}")

        if existing_ids:
            papers_to_process = [p for p in papers if str(p.get("id")) not in existing_ids]
            skipped = len(existing_ids)
            logger.info(f"跳过 {skipped} 个已有向量的论文")

    if not papers_to_process:
        return {"total": total, "successful": 0, "failed": 0, "skipped": skipped}

    # 提取文本列表
    texts = []
    valid_papers = []
    for paper in papers_to_process:
        try:
            text = _extract_text_for_embedding(paper)
            texts.append(text)
            valid_papers.append(paper)
        except ValueError as e:
            logger.warning(f"论文 {paper.get('id')} 文本提取失败: {e}")
            failed += 1
            if not continue_on_error:
                raise

    # 批量生成向量
    embeddings = generate_embeddings_batch(
        texts,
        max_concurrent=max_concurrent,
        continue_on_error=continue_on_error,
    )

    # 批量存储
    ids_to_add = []
    embeddings_to_add = []
    metadatas_to_add = []
    documents_to_add = []

    for i, (paper, embedding) in enumerate(zip(valid_papers, embeddings, strict=True)):
        if embedding is None:
            logger.error(f"论文 {paper.get('id')} 向量化失败")
            failed += 1
            if not continue_on_error:
                raise
            continue

        ids_to_add.append(str(paper["id"]))
        embeddings_to_add.append(embedding)
        metadatas_to_add.append(_build_metadata(paper))
        documents_to_add.append(texts[i])
        successful += 1

    if ids_to_add:
        collection.add(
            ids=ids_to_add,
            embeddings=embeddings_to_add,  # type: ignore[arg-type]
            metadatas=metadatas_to_add,  # type: ignore[arg-type]
            documents=documents_to_add,
        )

    result = {
        "total": total,
        "successful": successful,
        "failed": failed,
        "skipped": skipped,
    }
    logger.info(f"批量存储完成: {result}")
    return result


def get_papers_without_embeddings() -> list[dict[str, Any]]:
    """获取没有向量的论文

    从数据库获取所有论文，供重建向量使用

    Returns:
        list[dict]: 论文列表
    """
    from evo_flywheel.config import get_settings

    settings = get_settings()

    # 创建数据库连接
    engine = create_engine(
        settings.effective_database_url,
        connect_args={"check_same_thread": False}
        if settings.effective_database_url.startswith("sqlite")
        else {},
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        papers = crud.get_papers(db, limit=10000)

        # 转换为字典格式
        result = []
        for paper in papers:
            result.append(
                {
                    "id": paper.id,
                    "title": paper.title,
                    "abstract": paper.abstract,
                    "authors": paper.authors,
                    "journal": paper.journal,
                    "publication_date": (
                        paper.publication_date.isoformat() if paper.publication_date else None
                    ),
                    "doi": paper.doi,
                    "taxa": paper.taxa,
                    "evolutionary_scale": paper.evolutionary_scale,
                    "research_method": paper.research_method,
                    "evolutionary_mechanism": paper.evolutionary_mechanism,
                    "importance_score": paper.importance_score,
                    "key_findings": paper.key_findings,
                    "innovation_summary": paper.innovation_summary,
                }
            )

        return result

    finally:
        db.close()
        engine.dispose()


def rebuild_paper_embeddings(
    collection_name: str = chroma_client.DEFAULT_COLLECTION,
    clear_existing: bool = False,
    max_concurrent: int = 5,
) -> dict[str, int]:
    """重建所有论文向量

    Args:
        collection_name: Chroma collection 名称
        clear_existing: 是否清除现有向量
        max_concurrent: 最大并发数

    Returns:
        dict: 处理统计 {"total": int, "successful": int, "failed": int}
    """
    logger.info("开始重建向量...")

    # 清除现有向量（如果需要）
    if clear_existing:
        collection = chroma_client.get_or_create_collection(name=collection_name)
        count = collection.count()
        if count > 0:
            logger.warning(f"清除 {count} 个现有向量")
            # Chroma 不支持批量删除全部，需要删除 collection 重建
            client = chroma_client.get_chroma_client()
            client.delete_collection(name=collection_name)
            chroma_client.get_or_create_collection(name=collection_name)

    # 获取所有论文
    papers = get_papers_without_embeddings()
    total = len(papers)

    if total == 0:
        logger.info("没有论文需要向量化")
        return {"total": 0, "successful": 0, "failed": 0}

    logger.info(f"开始为 {total} 篇论文生成向量...")

    # 批量存储
    result = store_papers_batch(
        papers,
        collection_name=collection_name,
        max_concurrent=max_concurrent,
        continue_on_error=True,
    )

    logger.info(f"向量重建完成: {result}")
    return {
        "total": result["total"],
        "successful": result["successful"],
        "failed": result["failed"],
    }
