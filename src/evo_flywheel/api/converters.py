"""API 响应转换器

将数据库模型转换为 API 响应格式
"""

import json

from evo_flywheel.api.schemas import DeepReportDetailResponse
from evo_flywheel.db.models import DailyReport


def daily_report_to_response(
    report: DailyReport,
    content: dict | None = None,
) -> DeepReportDetailResponse:
    """将 DailyReport 模型转换为 API 响应

    Args:
        report: 报告数据库模型
        content: 已解析的内容（可选，如未提供则自动解析）

    Returns:
        DeepReportDetailResponse
    """
    # 如果没有提供预解析的内容，则从 report_content 解析
    if content is None and report.report_content:
        try:
            content = json.loads(str(report.report_content))
        except json.JSONDecodeError:
            content = {"raw": str(report.report_content)}
    elif content is None:
        content = {}

    return DeepReportDetailResponse(
        id=int(report.id),
        report_date=str(report.report_date),
        total_papers=int(report.total_papers),
        high_value_papers=int(report.high_value_papers),
        top_paper_ids=report.top_papers_list,
        content=content,
        created_at=report.created_at.isoformat() if report.created_at else "",
    )
