"""论文分析调度 API 端点"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from evo_flywheel.analyzers.batch import analyze_papers_batch
from evo_flywheel.api.deps import get_db
from evo_flywheel.db.models import Paper
from evo_flywheel.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/trigger")
def trigger_analysis(
    limit: int = Query(50, ge=1, le=1000, description="分析论文数量限制"),
    min_score: int | None = Query(None, description="最低重要性评分过滤"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """触发论文分析

    对未分析的论文进行批量分析，使用 LLM 提取关键信息
    """
    try:
        # 获取未分析的论文（importance_score 为空）
        query = db.query(Paper).filter(Paper.importance_score.is_(None))

        # 应用最低评分过滤
        if min_score is not None:
            query = query.filter(Paper.importance_score >= min_score)

        papers = query.order_by(Paper.created_at.desc()).limit(limit).all()

        if not papers:
            return {"analyzed": 0, "total": 0, "message": "没有需要分析的论文"}

        # 转换为字典格式供批量分析使用
        papers_dicts = []
        for p in papers:
            papers_dicts.append(
                {
                    "id": p.id,
                    "title": p.title,
                    "abstract": p.abstract,
                    "authors": p.authors,
                    "doi": p.doi,
                    "publication_date": p.publication_date,  # 已经是字符串
                }
            )

        logger.info(f"开始分析 {len(papers_dicts)} 篇论文")

        # 调用批量分析模块
        analyzed_papers = analyze_papers_batch(
            papers_dicts,
            max_concurrent=3,  # 并发控制，避免 API 限流
            continue_on_error=True,
        )

        # 更新数据库
        analyzed_count = 0
        for paper_dict, paper_obj in zip(analyzed_papers, papers, strict=True):
            # 检查分析是否成功
            if "_error" in paper_dict:
                logger.warning(f"论文 {paper_obj.id} 分析失败: {paper_dict['_error']}")
                continue

            # 更新数据库记录
            paper_obj.taxa = paper_dict.get("taxa")  # type: ignore
            paper_obj.evolutionary_scale = paper_dict.get("evolutionary_scale")  # type: ignore
            paper_obj.research_method = paper_dict.get("research_method")  # type: ignore
            paper_obj.key_findings = paper_dict.get("key_findings")  # type: ignore
            paper_obj.evolutionary_mechanism = paper_dict.get("evolutionary_mechanism")  # type: ignore
            paper_obj.importance_score = paper_dict.get("importance_score")  # type: ignore
            paper_obj.innovation_summary = paper_dict.get("innovation_summary")  # type: ignore

            analyzed_count += 1

        db.commit()

        logger.info(f"分析完成: {analyzed_count}/{len(papers)} 篇论文")

        return {
            "analyzed": analyzed_count,
            "total": len(papers),
            "message": f"已分析 {analyzed_count} 篇论文",
        }

    except Exception as e:
        db.rollback()
        logger.error(f"分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {e!s}")


@router.get("/status")
def get_analysis_status(db: Session = Depends(get_db)) -> dict[str, Any]:
    """获取分析状态

    返回论文分析统计信息
    """
    # 统计未分析的论文
    unanalyzed = db.query(Paper).filter(Paper.importance_score.is_(None)).count()
    total = db.query(Paper).count()
    analyzed = total - unanalyzed

    return {
        "total": total,
        "analyzed": analyzed,
        "unanalyzed": unanalyzed,
        "progress": round(analyzed / total * 100, 2) if total > 0 else 0,
    }
