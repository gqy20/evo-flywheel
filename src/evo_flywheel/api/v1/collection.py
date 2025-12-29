"""数据采集相关 API 端点"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from evo_flywheel.api.deps import get_db
from evo_flywheel.collectors.orchestrator import collect_from_all_sources
from evo_flywheel.db import crud
from evo_flywheel.scheduler.jobs import load_rss_sources

router = APIRouter()


@router.post("/fetch")
def trigger_fetch(
    days: int = Query(7, ge=1, le=30, description="采集最近几天的论文"),
    sources: str | None = Query(None, description="指定数据源（逗号分隔）"),
    db: Session = Depends(get_db),
) -> dict:
    """触发数据采集

    手动触发从 RSS 和 API 采集论文
    """
    try:
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 加载 RSS 源
        rss_sources = load_rss_sources()

        # 根据 sources 参数过滤数据源
        if sources:
            requested_sources = [s.strip() for s in sources.split(",")]
            rss_sources = [s for s in rss_sources if s.get("name") in requested_sources]

        # 执行采集
        papers = collect_from_all_sources(
            start_date=start_date,
            end_date=end_date,
            rss_sources=rss_sources,
            category="evolutionary_biology",
        )

        # 保存到数据库并统计新增数量
        new_count = 0
        for paper_data in papers:
            # 检查是否已存在
            existing = None
            if paper_data.get("doi"):
                existing = crud.get_paper_by_doi(db, paper_data["doi"])
            elif paper_data.get("url"):
                from evo_flywheel.db.models import Paper

                existing = db.query(Paper).filter(Paper.url == paper_data["url"]).first()

            if not existing:
                crud.create_paper(
                    db,
                    title=paper_data.get("title", ""),
                    doi=paper_data.get("doi"),
                    authors=paper_data.get("authors", []),
                    abstract=paper_data.get("abstract"),
                    url=paper_data.get("url"),
                    publication_date=paper_data.get("publication_date"),
                    journal=paper_data.get("journal"),
                    source=paper_data.get("source"),
                )
                new_count += 1

        db.commit()

        return {"total": len(papers), "new": new_count}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"采集失败: {e!s}")


@router.get("/status")
def get_collection_status(db: Session = Depends(get_db)) -> dict[str, Any]:
    """获取采集状态

    返回当前系统采集状态和最近采集时间
    """
    from evo_flywheel.db import crud

    # 获取最新的采集日志
    latest_log = crud.get_latest_collection_log(db)

    # 确定当前状态
    if latest_log and latest_log.status == "running":
        current_status = "running"
    elif latest_log and latest_log.status == "failed":
        current_status = "failed"
    elif latest_log and latest_log.status == "success":
        current_status = "idle"
    else:
        current_status = "idle"

    # 构建返回数据
    result: dict[str, Any] = {
        "status": current_status,
        "last_collection": None,
        "total_sources": 8,  # 固定值，后续可以从 RSSSource 表获取
    }

    if latest_log:
        result["last_collection"] = {
            "status": latest_log.status,
            "total_papers": latest_log.total_papers,
            "new_papers": latest_log.new_papers,
            "sources": latest_log.sources,
            "error_message": latest_log.error_message,
            "created_at": latest_log.created_at.isoformat() if latest_log.created_at else None,
        }

    return result
