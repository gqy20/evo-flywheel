"""报告相关 API 端点"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from evo_flywheel.api.deps import get_db
from evo_flywheel.db.models import Paper

router = APIRouter()


@router.get("/today")
def get_today_report(db: Session = Depends(get_db)) -> dict:
    """获取今日报告

    返回今天采集的论文统计和重点推荐
    """
    today = date.today()

    # 获取今天的论文
    papers = (
        db.query(Paper)
        .filter(Paper.created_at >= today)
        .order_by(Paper.importance_score.desc())
        .limit(20)
        .all()
    )

    return {
        "date": today.isoformat(),
        "count": len(papers),
        "papers": [
            {
                "id": p.id,
                "title": p.title,
                "authors": p.authors_list,
                "abstract": p.abstract,
                "importance_score": p.importance_score,
            }
            for p in papers
        ],
    }


@router.get("/{report_date}")
def get_report_by_date(
    report_date: date,
    db: Session = Depends(get_db),
) -> dict:
    """获取指定日期的报告"""
    papers = (
        db.query(Paper)
        .filter(Paper.created_at >= report_date, Paper.created_at < report_date)
        .order_by(Paper.importance_score.desc())
        .limit(20)
        .all()
    )

    return {
        "date": report_date.isoformat(),
        "count": len(papers),
        "papers": [
            {
                "id": p.id,
                "title": p.title,
                "authors": p.authors_list,
                "abstract": p.abstract,
                "importance_score": p.importance_score,
            }
            for p in papers
        ],
    }


@router.post("/generate")
def generate_report(
    date_str: str | None = Query(None, description="日期字符串 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
) -> dict:
    """手动生成指定日期的报告

    如果不指定日期，生成今天的报告
    """
    from datetime import datetime

    from evo_flywheel.reporters.generator import generate_daily_report

    target_date: date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()

    try:
        report = generate_daily_report(target_date)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成报告失败: {e!s}")
