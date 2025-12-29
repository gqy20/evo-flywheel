"""论文分析调度 API 端点"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from evo_flywheel.api.deps import get_db
from evo_flywheel.db.models import Paper

router = APIRouter()


@router.post("/trigger")
def trigger_analysis(
    limit: int = Query(50, ge=1, le=100, description="分析论文数量限制"),
    min_score: int | None = Query(None, description="最低重要性评分过滤"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """触发论文分析

    对未分析的论文进行批量分析
    """
    try:
        # 获取未分析的论文（importance_score 为空）
        query = db.query(Paper).filter(Paper.importance_score.is_(None))

        # 应用最低评分过滤
        if min_score is not None:
            query = query.filter(Paper.importance_score >= min_score)

        papers = query.order_by(Paper.created_at.desc()).limit(limit).all()

        if not papers:
            return {"analyzed": 0, "message": "没有需要分析的论文"}

        # TODO: 实际调用分析模块
        # 这里只是占位符，实际分析逻辑需要调用 LLM
        analyzed_count = len(papers)

        return {
            "analyzed": analyzed_count,
            "total": len(papers),
            "message": f"已分析 {analyzed_count} 篇论文",
        }

    except Exception as e:
        db.rollback()
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
