"""数据采集相关 API 端点"""

from datetime import datetime, timedelta

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

        # TODO: sources 参数用于过滤数据源，这里先忽略，后续实现

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
def get_collection_status() -> dict:
    """获取采集状态

    返回当前系统采集状态和最近采集时间
    """
    # TODO: 实现实际的采集状态查询 (需要 CollectionLog 模型)
    return {
        "status": "idle",
        "last_collection": None,
        "total_sources": 8,
    }
