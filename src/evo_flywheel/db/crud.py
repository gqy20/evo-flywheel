"""数据库 CRUD 操作

提供论文、报告、反馈的增删改查操作
"""

from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from evo_flywheel.db.models import CollectionLog, DailyReport, Feedback, Paper, PaperCluster
from evo_flywheel.logging import get_logger

logger = get_logger(__name__)

# ============================================================================
# Paper CRUD
# ============================================================================


def create_paper(
    db: Session,
    *,
    title: str,
    doi: str | None = None,
    authors: list[str] | None = None,
    abstract: str | None = None,
    url: str | None = None,
    publication_date: str | None = None,
    journal: str | None = None,
    source: str | None = None,
    taxa: str | None = None,
    evolutionary_scale: str | None = None,
    research_method: str | None = None,
    evolutionary_mechanism: str | None = None,
    importance_score: int | None = None,
    key_findings: list[str] | None = None,
    innovation_summary: str | None = None,
    tags: list[str] | None = None,
) -> Paper:
    """创建新论文

    Args:
        db: 数据库会话
        title: 论文标题
        doi: DOI
        authors: 作者列表
        abstract: 摘要
        url: 论文链接
        publication_date: 发表日期
        journal: 期刊
        source: 来源
        taxa: 研究物种
        evolutionary_scale: 进化尺度
        research_method: 研究方法
        evolutionary_mechanism: 进化机制
        importance_score: 重要性评分
        key_findings: 关键发现列表
        innovation_summary: 创新性总结
        tags: 标签列表

    Returns:
        Paper: 创建的论文对象
    """
    paper = Paper(
        title=title,
        doi=doi,
        abstract=abstract,
        url=url,
        publication_date=publication_date,
        journal=journal,
        source=source,
        taxa=taxa,
        evolutionary_scale=evolutionary_scale,
        research_method=research_method,
        evolutionary_mechanism=evolutionary_mechanism,
        importance_score=importance_score,
        innovation_summary=innovation_summary,
    )

    # 设置列表属性
    if authors:
        paper.authors_list = authors
    if key_findings:
        paper.findings_list = key_findings
    if tags:
        paper.tags_list = tags

    db.add(paper)
    db.commit()
    db.refresh(paper)

    return paper


def get_paper_by_id(db: Session, paper_id: int) -> Paper | None:
    """根据 ID 获取论文

    Args:
        db: 数据库会话
        paper_id: 论文 ID

    Returns:
        Paper | None: 论文对象，不存在返回 None
    """
    return db.query(Paper).filter(Paper.id == paper_id).first()


def get_paper_by_doi(db: Session, doi: str) -> Paper | None:
    """根据 DOI 获取论文

    Args:
        db: 数据库会话
        doi: DOI

    Returns:
        Paper | None: 论文对象，不存在返回 None
    """
    return db.query(Paper).filter(Paper.doi == doi).first()


def get_papers(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    journal: str | None = None,
    source: str | None = None,
    min_score: int | None = None,
    taxa: str | None = None,
) -> list[Paper]:
    """获取论文列表

    Args:
        db: 数据库会话
        skip: 跳过数量
        limit: 返回数量限制
        journal: 期刊过滤
        source: 来源过滤
        min_score: 最低评分
        taxa: 物种过滤

    Returns:
        list[Paper]: 论文列表
    """
    query = db.query(Paper)

    # 应用过滤条件
    if journal:
        query = query.filter(Paper.journal == journal)
    if source:
        query = query.filter(Paper.source == source)
    if min_score is not None:
        query = query.filter(Paper.importance_score >= min_score)
    if taxa:
        query = query.filter(Paper.taxa == taxa)

    # 按评分和日期排序
    query = query.order_by(Paper.importance_score.desc(), Paper.publication_date.desc())

    return query.offset(skip).limit(limit).all()


def update_paper(
    db: Session,
    paper_id: int,
    **kwargs: Any,
) -> Paper | None:
    """更新论文

    Args:
        db: 数据库会话
        paper_id: 论文 ID
        **kwargs: 要更新的字段

    Returns:
        Paper | None: 更新后的论文对象，不存在返回 None
    """
    paper = get_paper_by_id(db, paper_id)
    if paper is None:
        return None

    # 处理列表字段
    if "authors" in kwargs:
        paper.authors_list = kwargs.pop("authors")
    if "key_findings" in kwargs:
        paper.findings_list = kwargs.pop("key_findings")
    if "tags" in kwargs:
        paper.tags_list = kwargs.pop("tags")

    # 更新其他字段
    for key, value in kwargs.items():
        if hasattr(paper, key):
            setattr(paper, key, value)

    db.commit()
    db.refresh(paper)

    return paper


def delete_paper(db: Session, paper_id: int) -> bool:
    """删除论文

    Args:
        db: 数据库会话
        paper_id: 论文 ID

    Returns:
        bool: 是否删除成功
    """
    paper = get_paper_by_id(db, paper_id)
    if paper is None:
        return False

    db.delete(paper)
    db.commit()

    return True


def get_papers_by_date_range(
    db: Session,
    start_date: date,
    end_date: date | None = None,
    only_analyzed: bool = False,
    limit: int | None = None,
    order_by_score: bool = True,
) -> list[Paper]:
    """按日期范围查询论文

    Args:
        db: 数据库会话
        start_date: 开始日期（包含）
        end_date: 结束日期（不包含），默认为 start_date + 1 天
        only_analyzed: 是否只返回已分析的论文
        limit: 限制返回数量
        order_by_score: 是否按重要性评分排序

    Returns:
        论文列表
    """
    if end_date is None:
        end_date = start_date + timedelta(days=1)

    query = db.query(Paper).filter(
        Paper.created_at >= start_date,
        Paper.created_at < end_date,
    )

    if only_analyzed:
        query = query.filter(Paper.importance_score.isnot(None))

    if order_by_score:
        query = query.order_by(Paper.importance_score.desc())

    if limit:
        query = query.limit(limit)

    return query.all()


# ============================================================================
# DailyReport CRUD
# ============================================================================


def create_daily_report(
    db: Session,
    *,
    report_date: str,
    total_papers: int,
    high_value_papers: int = 0,
    top_paper_ids: list[int] | None = None,
    report_content: str | None = None,
) -> DailyReport:
    """创建每日报告

    Args:
        db: 数据库会话
        report_date: 报告日期
        total_papers: 总论文数
        high_value_papers: 高价值论文数
        top_paper_ids: 顶级论文 ID 列表
        report_content: 报告内容

    Returns:
        DailyReport: 创建的每日报告对象
    """
    report = DailyReport(
        report_date=report_date,
        total_papers=total_papers,
        high_value_papers=high_value_papers,
        report_content=report_content,
    )

    if top_paper_ids:
        report.top_papers_list = top_paper_ids

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


def get_daily_report_by_date(db: Session, report_date: str) -> DailyReport | None:
    """根据日期获取每日报告

    Args:
        db: 数据库会话
        report_date: 报告日期

    Returns:
        DailyReport | None: 每日报告对象，不存在返回 None
    """
    return db.query(DailyReport).filter(DailyReport.report_date == report_date).first()


def get_latest_daily_report(db: Session) -> DailyReport | None:
    """获取最新的每日报告

    Args:
        db: 数据库会话

    Returns:
        DailyReport | None: 最新的每日报告对象
    """
    return db.query(DailyReport).order_by(DailyReport.report_date.desc()).first()


# ============================================================================
# Feedback CRUD
# ============================================================================


def create_feedback(
    db: Session,
    *,
    paper_id: int,
    rating: int,
    is_helpful: bool | None = None,
    comment: str | None = None,
) -> Feedback:
    """创建反馈

    Args:
        db: 数据库会话
        paper_id: 论文 ID
        rating: 评分 (1-5)
        is_helpful: 是否有帮助
        comment: 评论内容

    Returns:
        Feedback: 创建的反馈对象
    """
    feedback = Feedback(
        paper_id=paper_id,
        rating=rating,
        is_helpful=is_helpful,
        comment=comment,
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback


def get_feedbacks_by_paper(db: Session, paper_id: int) -> list[Feedback]:
    """获取论文的所有反馈

    Args:
        db: 数据库会话
        paper_id: 论文 ID

    Returns:
        list[Feedback]: 反馈列表
    """
    return (
        db.query(Feedback)
        .filter(Feedback.paper_id == paper_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )


# ============================================================================
# CollectionLog CRUD
# ============================================================================


def create_collection_log(
    db: Session,
    *,
    status: str,
    total_papers: int = 0,
    new_papers: int = 0,
    sources: str | None = None,
    error_message: str | None = None,
) -> CollectionLog:
    """创建采集日志

    Args:
        db: 数据库会话
        status: 采集状态 (running, success, failed)
        total_papers: 总论文数
        new_papers: 新增论文数
        sources: 数据源列表（逗号分隔）
        error_message: 错误信息

    Returns:
        CollectionLog: 创建的采集日志对象
    """
    log = CollectionLog(
        status=status,
        total_papers=total_papers,
        new_papers=new_papers,
        sources=sources,
        error_message=error_message,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


def get_latest_collection_log(db: Session) -> CollectionLog | None:
    """获取最新的采集日志

    Args:
        db: 数据库会话

    Returns:
        CollectionLog | None: 最新的采集日志对象
    """
    return db.query(CollectionLog).order_by(CollectionLog.created_at.desc()).first()


def get_collection_logs(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
) -> list[CollectionLog]:
    """获取采集日志列表

    Args:
        db: 数据库会话
        skip: 跳过数量
        limit: 返回数量限制

    Returns:
        list[CollectionLog]: 采集日志列表
    """
    return (
        db.query(CollectionLog)
        .order_by(CollectionLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# ============================================================================
# PaperCluster CRUD
# ============================================================================


def create_paper_cluster(
    db: Session,
    *,
    report_id: int,
    cluster_name: str,
    paper_ids: list[int],
    cluster_summary: str | None = None,
    key_findings: list[str] | None = None,
) -> PaperCluster:
    """创建论文聚类

    Args:
        db: 数据库会话
        report_id: 关联的报告ID
        cluster_name: 聚类名称
        paper_ids: 论文ID列表
        cluster_summary: 聚类摘要
        key_findings: 关键发现列表

    Returns:
        PaperCluster: 创建的聚类对象
    """
    cluster = PaperCluster(
        report_id=report_id,
        cluster_name=cluster_name,
        cluster_summary=cluster_summary,
    )

    # 设置列表属性
    cluster.paper_ids_list = paper_ids
    if key_findings:
        cluster.findings_list = key_findings

    db.add(cluster)
    db.commit()
    db.refresh(cluster)

    return cluster


def get_clusters_by_report(db: Session, report_id: int) -> list[PaperCluster]:
    """获取报告的所有聚类

    Args:
        db: 数据库会话
        report_id: 报告ID

    Returns:
        list[PaperCluster]: 聚类列表
    """
    return (
        db.query(PaperCluster)
        .filter(PaperCluster.report_id == report_id)
        .order_by(PaperCluster.id)
        .all()
    )
