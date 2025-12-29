"""AI 分析调度模块

提供批量论文分析和向量化的调度功能
"""

import sys
from typing import Any

from sqlalchemy import text

from evo_flywheel.analyzers.batch import analyze_papers_batch
from evo_flywheel.db import crud
from evo_flywheel.db.context import get_db_session
from evo_flywheel.db.models import Paper
from evo_flywheel.logging import get_logger
from evo_flywheel.vector.client import get_chroma_client
from evo_flywheel.vector.embeddings import generate_embeddings_batch

logger = get_logger(__name__)


def _get_unanalyzed_papers(
    max_papers: int | None = None,
    min_score: int = 0,
) -> list[dict[str, Any]]:
    """从数据库获取未分析的论文

    判断标准: importance_score IS NULL

    Args:
        max_papers: 最大返回数量
        min_score: 最低重要性评分（预留参数）

    Returns:
        list[dict]: 论文数据列表
    """
    with get_db_session() as session:
        query = text("""
            SELECT id, title, abstract, doi, url, authors
            FROM papers
            WHERE importance_score IS NULL
            AND abstract IS NOT NULL AND abstract != ''
            ORDER BY publication_date DESC
            LIMIT :limit
        """)

        result = session.execute(query, {"limit": max_papers or 100})

        papers = []
        for row in result:
            papers.append(
                {
                    "id": row[0],
                    "title": row[1],
                    "abstract": row[2],
                    "doi": row[3],
                    "url": row[4],
                    "authors": row[5].split(";") if row[5] else [],
                }
            )

    logger.info(f"找到 {len(papers)} 篇未分析的论文")
    return papers


def _update_analysis_to_db(papers: list[dict[str, Any]]) -> int:
    """将 AI 分析结果更新到数据库

    Args:
        papers: 包含分析结果的论文列表

    Returns:
        int: 更新的论文数量
    """
    updated_count = 0

    with get_db_session() as session:
        for paper_data in papers:
            # 通过 DOI 或 URL 查找已有论文
            paper = None
            if paper_data.get("doi"):
                paper = crud.get_paper_by_doi(session, paper_data["doi"])
            elif paper_data.get("url"):
                paper = session.query(Paper).filter(Paper.url == paper_data["url"]).first()

            if not paper:
                continue

            # 更新 AI 分析字段
            crud.update_paper(
                session,
                paper.id,
                taxa=paper_data.get("taxa"),
                evolutionary_scale=paper_data.get("evolutionary_scale"),
                research_method=paper_data.get("research_method"),
                evolutionary_mechanism=paper_data.get("evolutionary_mechanism"),
                importance_score=paper_data.get("importance_score"),
                key_findings=paper_data.get("key_findings"),
                innovation_summary=paper_data.get("innovation_summary"),
            )
            updated_count += 1

        logger.info(f"更新了 {updated_count} 篇论文的 AI 分析结果")

    return updated_count


def analyze_unanalyzed_papers(
    max_papers: int | None = None,
    min_score: int = 0,
    max_concurrent: int = 3,
) -> dict[str, Any]:
    """分析未分析的论文

    Args:
        max_papers: 最大分析数量
        min_score: 最低重要性评分（预留）
        max_concurrent: 最大并发数

    Returns:
        dict: 统计信息 {analyzed, skipped, errors}
    """
    logger.info("开始批量分析论文")

    # 1. 获取未分析的论文
    papers = _get_unanalyzed_papers(max_papers=max_papers, min_score=min_score)

    if not papers:
        logger.info("没有需要分析的论文")
        return {"analyzed": 0, "skipped": 0, "errors": 0}

    # 2. 批量分析
    analyzed = analyze_papers_batch(
        papers,
        max_concurrent=max_concurrent,
        continue_on_error=True,
    )

    # 3. 保存到数据库
    updated = _update_analysis_to_db(analyzed)

    # 统计结果
    error_count = sum(1 for p in analyzed if "_error" in p)
    cached_count = sum(1 for p in analyzed if p.get("_cached", False))

    logger.info(
        f"批量分析完成: total={len(papers)}, updated={updated}, "
        f"cached={cached_count}, errors={error_count}"
    )

    return {
        "analyzed": updated,
        "skipped": cached_count,
        "errors": error_count,
    }


def _get_unembedded_papers(max_papers: int | None = None) -> list[dict[str, Any]]:
    """从数据库获取未向量化的论文

    判断标准: embedded = False

    Args:
        max_papers: 最大返回数量

    Returns:
        list[dict]: 论文数据列表
    """
    with get_db_session() as session:
        query = text("""
            SELECT id, title, abstract, doi
            FROM papers
            WHERE embedded = 0
            AND abstract IS NOT NULL AND abstract != ''
            ORDER BY publication_date DESC
            LIMIT :limit
        """)

        result = session.execute(query, {"limit": max_papers or 100})

        papers = []
        for row in result:
            papers.append(
                {
                    "id": row[0],
                    "title": row[1],
                    "abstract": row[2],
                    "doi": row[3],
                }
            )

    logger.info(f"找到 {len(papers)} 篇未向量化的论文")
    return papers


def _save_embeddings_to_chroma(
    papers: list[dict[str, Any]],
    vectors: list[list[float] | None],
) -> int:
    """保存向量到 Chroma

    Args:
        papers: 论文列表（需包含 doi）
        vectors: 向量列表

    Returns:
        int: 成功保存的数量
    """
    client = get_chroma_client()
    collection = client.get_or_create_collection("evolutionary_papers")

    saved_count = 0

    with get_db_session() as session:
        for paper, vector in zip(papers, vectors, strict=True):
            if not vector:
                continue

            # 通过 DOI 获取数据库中的论文 ID
            if not paper.get("doi"):
                continue

            db_paper = crud.get_paper_by_doi(session, paper["doi"])
            if not db_paper:
                continue

            # 准备 Chroma 文档
            collection.add(
                ids=[str(db_paper.id)],
                documents=[paper.get("abstract", "")],
                embeddings=[vector],
                metadatas=[
                    {
                        "title": paper.get("title", ""),
                        "doi": paper.get("doi", ""),
                        "taxa": paper.get("taxa", ""),
                        "score": paper.get("importance_score", 0),
                    }
                ],
            )

            # 标记为已向量化
            crud.update_paper(session, db_paper.id, embedded=True)
            saved_count += 1

        logger.info(f"保存了 {saved_count} 个向量到 Chroma")

    return saved_count


def embed_unembedded_papers(
    max_papers: int | None = None,
    max_concurrent: int = 5,
) -> dict[str, Any]:
    """为未向量化的论文生成向量

    Args:
        max_papers: 最大处理数量
        max_concurrent: 最大并发数

    Returns:
        dict: 统计信息 {embedded, errors}
    """
    logger.info("开始批量生成向量")

    # 1. 获取未向量化的论文
    papers = _get_unembedded_papers(max_papers=max_papers)

    if not papers:
        logger.info("没有需要向量化的论文")
        return {"embedded": 0, "errors": 0}

    # 2. 批量生成向量
    texts = [p["abstract"] for p in papers]
    vectors = generate_embeddings_batch(
        texts,
        max_concurrent=max_concurrent,
        continue_on_error=True,
    )

    # 3. 保存到 Chroma
    saved = _save_embeddings_to_chroma(papers, vectors)

    error_count = sum(1 for v in vectors if v is None)

    logger.info(f"批量向量化完成: embedded={saved}, errors={error_count}")

    return {
        "embedded": saved,
        "errors": error_count,
    }


def main() -> None:
    """命令行入口

    用法:
        evo-analyze               # 分析未分析的论文
        evo-analyze --max 50      # 最多分析 50 篇
        evo-analyze --embed-only  # 只生成向量
        evo-analyze --help        # 显示帮助信息
    """
    # 解析参数
    args = sys.argv[1:]

    max_papers = None
    embed_only = False

    i = 0
    while i < len(args):
        if args[i] in ("--help", "-h"):
            print("""
evo-analyze - AI 分析和向量化工具

用法:
  evo-analyze [选项]

选项:
  --max N              最多处理的论文数量
  --embed-only         只生成向量，不进行 AI 分析
  --help, -h           显示此帮助信息

示例:
  evo-analyze               # 分析所有未分析的论文
  evo-analyze --max 50      # 最多分析 50 篇
  evo-analyze --embed-only  # 只生成向量
""")
            return
        elif args[i] == "--max" and i + 1 < len(args):
            max_papers = int(args[i + 1])
            i += 2
        elif args[i] == "--embed-only":
            embed_only = True
            i += 1
        else:
            i += 1

    try:
        if embed_only:
            # 仅向量化模式
            logger.info("运行向量化模式")
            result = embed_unembedded_papers(max_papers=max_papers)
            logger.info(f"向量化完成: embedded={result['embedded']}, errors={result['errors']}")
        else:
            # 分析模式
            logger.info("运行分析模式")
            result = analyze_unanalyzed_papers(max_papers=max_papers)
            logger.info(
                f"分析完成: analyzed={result['analyzed']}, "
                f"skipped={result['skipped']}, errors={result['errors']}"
            )

    except Exception as e:
        logger.error(f"执行失败: {e}")
        # 优雅退出，不抛出异常
        return


if __name__ == "__main__":
    main()
