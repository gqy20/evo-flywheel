"""报告相关 API 端点"""

import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from evo_flywheel.api.deps import get_db
from evo_flywheel.db import crud
from evo_flywheel.db.models import DailyReport

router = APIRouter()


class DeepReportResponse(BaseModel):
    """深度报告响应"""

    id: int = Field(description="报告ID")
    report_date: str = Field(description="报告日期")
    total_papers: int = Field(description="总论文数")
    high_value_papers: int = Field(description="高价值论文数")


class DeepReportDetailResponse(BaseModel):
    """深度报告详情响应"""

    id: int = Field(description="报告ID")
    report_date: str = Field(description="报告日期")
    total_papers: int = Field(description="总论文数")
    high_value_papers: int = Field(description="高价值论文数")
    top_paper_ids: list[int] = Field(description="顶级论文ID列表")
    content: dict = Field(description="报告内容（研究概要、热点话题等）")
    created_at: str = Field(description="创建时间")


# ============================================================================
# 重要：具体路由必须放在参数化路由之前，否则会匹配错误
# ============================================================================


# 简单报告路由
@router.get("/today")
def get_today_report(db: Session = Depends(get_db)) -> dict:
    """获取今日报告

    返回今天采集的论文统计和重点推荐
    """
    today = date.today()

    # 获取今天的论文
    papers = crud.get_papers_by_date_range(db, today, limit=20)

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


# 深度报告路由 - 必须在 /{report_date} 之前
@router.get("/deep", response_model=list[DeepReportDetailResponse])
def list_deep_reports(
    limit: int = Query(10, description="返回数量限制", ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[DeepReportDetailResponse]:
    """获取深度报告列表（按创建时间倒序）

    由于飞轮每4小时运行一次，同一天可能有多份报告

    Args:
        limit: 返回数量限制
        db: 数据库会话

    Returns:
        深度报告列表
    """
    reports = db.query(DailyReport).order_by(DailyReport.created_at.desc()).limit(limit).all()

    result = []
    for report in reports:
        content = {}
        if report.report_content:
            try:
                content = json.loads(str(report.report_content))
            except json.JSONDecodeError:
                content = {"raw": str(report.report_content)}

        result.append(
            DeepReportDetailResponse(
                id=int(report.id),
                report_date=str(report.report_date),
                total_papers=int(report.total_papers),
                high_value_papers=int(report.high_value_papers),
                top_paper_ids=report.top_papers_list,
                content=content,
                created_at=report.created_at.isoformat() if report.created_at else "",
            )
        )

    return result


@router.get("/deep/{report_id}", response_model=DeepReportDetailResponse)
def get_deep_report_by_id(
    report_id: int,
    db: Session = Depends(get_db),
) -> DeepReportDetailResponse:
    """获取指定 ID 的深度报告详情

    Args:
        report_id: 报告 ID
        db: 数据库会话

    Returns:
        DeepReportDetailResponse: 深度报告详情

    Raises:
        HTTPException: 报告不存在
    """
    report = db.query(DailyReport).filter(DailyReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail=f"未找到 ID 为 {report_id} 的深度报告")

    # 解析报告内容
    content = {}
    if report.report_content:
        try:
            content = json.loads(str(report.report_content))
        except json.JSONDecodeError:
            content = {"raw": str(report.report_content)}

    return DeepReportDetailResponse(
        id=int(report.id),
        report_date=str(report.report_date),
        total_papers=int(report.total_papers),
        high_value_papers=int(report.high_value_papers),
        top_paper_ids=report.top_papers_list,
        content=content,
        created_at=report.created_at.isoformat() if report.created_at else "",
    )


@router.get("/deep/date/{report_date}", response_model=list[DeepReportDetailResponse])
def get_deep_reports_by_date(
    report_date: date,
    db: Session = Depends(get_db),
) -> list[DeepReportDetailResponse]:
    """获取指定日期的所有深度报告

    由于飞轮每 4 小时运行一次，同一天可能有多份报告

    Args:
        report_date: 报告日期
        db: 数据库会话

    Returns:
        按创建时间倒序排列的报告列表
    """
    reports = (
        db.query(DailyReport)
        .filter(DailyReport.report_date == report_date.isoformat())
        .order_by(DailyReport.created_at.desc())
        .all()
    )

    result = []
    for report in reports:
        content = {}
        if report.report_content:
            try:
                content = json.loads(str(report.report_content))
            except json.JSONDecodeError:
                content = {"raw": str(report.report_content)}

        result.append(
            DeepReportDetailResponse(
                id=int(report.id),
                report_date=str(report.report_date),
                total_papers=int(report.total_papers),
                high_value_papers=int(report.high_value_papers),
                top_paper_ids=report.top_papers_list,
                content=content,
                created_at=report.created_at.isoformat() if report.created_at else "",
            )
        )

    return result


# ============================================================================
# 参数化路由 - 必须放在最后
# ============================================================================


@router.get("/{report_date}")
def get_report_by_date(
    report_date: date,
    db: Session = Depends(get_db),
) -> dict:
    """获取指定日期的报告（简单版：论文列表）"""
    papers = crud.get_papers_by_date_range(db, report_date, limit=20)

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
        report = generate_daily_report(target_date, db)
        return report
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"生成报告失败: {e!s}")


@router.post("/generate-deep", response_model=DeepReportResponse)
def generate_deep_report_endpoint(
    date_str: str | None = Query(None, description="日期字符串 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
) -> DeepReportResponse:
    """生成深度报告

    使用 LLM 生成包含研究概要、热点话题、趋势分析的深度报告

    Args:
        date_str: 目标日期字符串 (YYYY-MM-DD)，默认为今天
        db: 数据库会话

    Returns:
        DeepReportResponse: 生成的报告信息

    Raises:
        HTTPException: 日期格式错误或生成失败
    """
    from datetime import datetime

    from evo_flywheel.reporters.deep_generator import generate_deep_report

    # 解析日期
    target_date: date
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"无效的日期格式: {date_str}，应为 YYYY-MM-DD"
            )
    else:
        target_date = date.today()

    try:
        report = generate_deep_report(target_date, db)
        return DeepReportResponse(
            id=int(report.id),
            report_date=str(report.report_date),
            total_papers=int(report.total_papers),
            high_value_papers=int(report.high_value_papers),
        )
    except ValueError as e:
        # 没有论文等业务逻辑错误
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger = __import__("evo_flywheel.logging", fromlist=["get_logger"]).get_logger(__name__)
        logger.error(f"深度报告生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成深度报告失败: {e!s}")
