"""统计相关 API 端点"""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from evo_flywheel.api.deps import get_db
from evo_flywheel.db.models import Paper

router = APIRouter()


@router.get("/overview")
def get_overview_stats(db: Session = Depends(get_db)) -> dict:
    """获取系统概览统计

    返回论文总数、分析数、向量化数等统计信息
    """
    total = db.query(func.count(Paper.id)).scalar()

    analyzed = db.query(func.count(Paper.id)).filter(Paper.importance_score.isnot(None)).scalar()

    embedded = db.query(func.count(Paper.id)).filter(Paper.embedded.is_(True)).scalar()

    # 今日新增
    from datetime import date

    today = date.today()
    today_new = db.query(func.count(Paper.id)).filter(Paper.created_at >= today).scalar()

    return {
        "total_papers": total,
        "analyzed_papers": analyzed,
        "embedded_papers": embedded,
        "today_new": today_new,
        "analysis_rate": round(analyzed / total * 100, 2) if total > 0 else 0,
        "embedding_rate": round(embedded / total * 100, 2) if total > 0 else 0,
    }
