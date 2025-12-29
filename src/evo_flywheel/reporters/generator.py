"""报告生成器模块

TODO: 里程碑 3 - 实现完整的 LLM 分析和报告生成功能
"""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from evo_flywheel.db.models import Paper
from evo_flywheel.logging import get_logger

logger = get_logger(__name__)


def generate_daily_report(target_date: date, db: Session) -> dict:
    """生成指定日期的每日报告

    Args:
        target_date: 目标日期
        db: 数据库会话

    Returns:
        dict: 包含日期和论文列表的报告
    """
    # 计算日期范围（target_date 当天 00:00 到 23:59）
    next_day = target_date + timedelta(days=1)

    # 查询指定日期采集的论文，按重要性评分降序排列
    papers = (
        db.query(Paper)
        .filter(Paper.created_at >= target_date, Paper.created_at < next_day)
        .order_by(Paper.importance_score.desc(), Paper.id.desc())
        .all()
    )

    logger.info(f"生成 {target_date} 的报告，找到 {len(papers)} 篇论文")

    # 构建报告数据
    report_papers = []
    for paper in papers:
        report_papers.append(
            {
                "id": paper.id,
                "title": paper.title,
                "authors": paper.authors_list,
                "abstract": paper.abstract,
                "taxa": paper.taxa,
                "evolutionary_scale": paper.evolutionary_scale,
                "research_method": paper.research_method,
                "key_findings": paper.key_findings,
                "evolutionary_mechanism": paper.evolutionary_mechanism,
                "innovation_summary": paper.innovation_summary,
                "importance_score": paper.importance_score,
                "doi": paper.doi,
                "url": paper.url,
                "publication_date": paper.publication_date,  # Text 类型，直接返回
                "journal": paper.journal,
            }
        )

    return {
        "date": target_date.isoformat(),
        "count": len(report_papers),
        "papers": report_papers,
    }
