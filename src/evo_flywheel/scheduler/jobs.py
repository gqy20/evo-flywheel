"""采集任务调度模块

使用 APScheduler 实现定时数据采集任务
"""

import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from evo_flywheel.collectors.orchestrator import collect_from_all_sources
from evo_flywheel.logging import get_logger

logger = get_logger(__name__)


def run_daily_flywheel() -> dict[str, Any]:
    """运行完整的飞轮流程

    流程：
    1. 采集新论文
    2. 分析未分析的论文
    3. 生成深度报告（如果有新分析的论文）

    Returns:
        dict: 飞轮运行统计 {collected, analyzed, report_generated}
    """
    logger.info("Starting daily flywheel")

    stats = {
        "collected": 0,
        "analyzed": 0,
        "report_generated": False,
    }

    # 1. 采集论文
    try:
        from evo_flywheel.scheduler.analysis import analyze_unanalyzed_papers

        papers = collect_daily_papers()
        stats["collected"] = len(papers)

        # 2. 分析论文（如果有新论文）
        if papers:
            analysis_result = analyze_unanalyzed_papers(max_papers=100)
            stats["analyzed"] = analysis_result["analyzed"]

    except Exception as e:
        logger.error(f"Collection or analysis failed: {e}")

    # 3. 生成深度报告（如果有新分析的论文）
    if stats["analyzed"] > 0:
        try:
            from evo_flywheel.config import get_settings
            from evo_flywheel.reporters.deep_generator import generate_deep_report

            settings = get_settings()
            engine = create_engine(settings.effective_database_url)

            with Session(engine) as session:
                report = generate_deep_report(date.today(), session)
                stats["report_generated"] = True
                logger.info(f"Deep report generated: report_id={report.id}")

        except Exception as e:
            logger.error(f"Deep report generation failed: {e}")

    logger.info(f"Flywheel completed: {stats}")
    return stats


def load_rss_sources(config_path: str = "config/sources.yaml") -> list[dict[str, Any]]:
    """加载 RSS 源配置

    Args:
        config_path: 配置文件路径

    Returns:
        list[dict]: RSS 源配置列表（仅包含启用的源）
    """
    config_file = Path(config_path)

    if not config_file.exists():
        logger.warning(f"RSS sources config file not found: {config_path}")
        return []

    try:
        with open(config_file, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        sources: list[dict[str, Any]] = []

        for source_name, source_config in config.get("sources", {}).items():
            # 只返回启用的 RSS 源
            if source_config.get("type") == "rss" and source_config.get("enabled", True):
                sources.append(
                    {
                        "name": source_config.get("name", source_name),
                        "url": source_config.get("url", ""),
                        "priority": source_config.get("priority", 999),
                    }
                )

        logger.info(f"Loaded {len(sources)} enabled RSS sources from {config_path}")
        return sources

    except Exception as e:
        logger.error(f"Failed to load RSS sources from {config_path}: {e}")
        return []


def collect_daily_papers(
    rss_sources: list[dict[str, Any]] | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    category: str = "evolutionary_biology",
) -> list[dict[str, Any]]:
    """执行每日论文采集

    Args:
        rss_sources: RSS 源配置列表（可选，默认从配置文件加载）
        start_date: 采集开始日期（可选，默认为7天前）
        end_date: 采集结束日期（可选，默认为今天）
        category: bioRxiv 论文分类

    Returns:
        list[dict]: 采集到的论文列表
    """
    logger.info("Starting daily paper collection")

    # 加载 RSS 源
    if rss_sources is None:
        rss_sources = load_rss_sources()

    # 设置默认日期范围（最近7天）
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=7)

    logger.info(f"Collection period: {start_date} to {end_date}")

    try:
        # 从所有源采集 (参数名与 orchestrator.py 一致)
        papers = collect_from_all_sources(
            start_date=start_date,
            end_date=end_date,
            rss_sources=rss_sources,
            category=category,
        )

        logger.info(f"Daily collection completed: {len(papers)} papers collected")

        # 保存到数据库
        if papers:
            _save_papers_to_db(papers)

        return papers

    except Exception as e:
        logger.error(f"Daily collection failed: {e}")
        return []


def _save_papers_to_db(papers: list[dict[str, Any]]) -> int:
    """保存论文到数据库

    Args:
        papers: 论文列表

    Returns:
        int: 实际保存的论文数量
    """
    from evo_flywheel.config import get_settings
    from evo_flywheel.db import crud
    from evo_flywheel.db.models import Paper

    settings = get_settings()
    engine = create_engine(settings.effective_database_url)

    saved_count = 0
    skipped_count = 0

    with Session(engine) as session:
        for paper_data in papers:
            try:
                # 检查是否已存在（通过 DOI 或 URL）
                existing = None
                if paper_data.get("doi"):
                    existing = crud.get_paper_by_doi(session, paper_data["doi"])
                elif paper_data.get("url"):
                    # 从 URL 提取 ID 作为唯一标识
                    existing = session.query(Paper).filter(Paper.url == paper_data["url"]).first()

                if existing:
                    skipped_count += 1
                    continue

                # 创建新论文记录
                crud.create_paper(
                    session,
                    title=paper_data.get("title", ""),
                    doi=paper_data.get("doi"),
                    authors=paper_data.get("authors", []),
                    abstract=paper_data.get("abstract"),
                    url=paper_data.get("url"),
                    publication_date=paper_data.get("publication_date"),
                    journal=paper_data.get("journal"),
                    source=paper_data.get("source"),
                )
                saved_count += 1

            except Exception as e:
                logger.error(f"Failed to save paper: {paper_data.get('title', 'Unknown')}: {e}")
                continue

        session.commit()
        logger.info(
            f"Saved {saved_count} new papers to database (skipped {skipped_count} duplicates)"
        )

    return saved_count


def schedule_flywheel(interval_hours: int = 4) -> BackgroundScheduler:
    """配置飞轮定时任务

    Args:
        interval_hours: 执行间隔（小时，默认 4 小时）

    Returns:
        BackgroundScheduler: 配置好的调度器实例
    """
    logger.info(f"Configuring flywheel schedule: every {interval_hours} hours")

    scheduler = BackgroundScheduler()

    # 添加周期性飞轮任务
    scheduler.add_job(
        run_daily_flywheel,
        trigger="interval",
        hours=interval_hours,
        id="flywheel",
        name="Evolutionary Biology Flywheel",
        replace_existing=True,
    )

    logger.info(f"Flywheel scheduler configured (runs every {interval_hours} hours)")
    return scheduler


def main() -> None:
    """命令行入口

    用法:
        evo-fetch               # 执行一次飞轮（采集+分析+报告）
        evo-fetch --schedule    # 启动调度器（4小时间隔）
        evo-fetch --interval 2  # 自定义间隔（2小时）
    """
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        # 调度器模式
        interval_hours = 4  # 默认4小时

        # 检查是否有自定义间隔
        if len(sys.argv) > 2 and sys.argv[2] == "--interval" and len(sys.argv) > 3:
            interval_hours = int(sys.argv[3])

        logger.info(f"Starting flywheel scheduler mode (every {interval_hours} hours)")
        scheduler = schedule_flywheel(interval_hours=interval_hours)
        scheduler.start()

        try:
            logger.info("Flywheel scheduler is running. Press Ctrl+C to exit.")
            # 保持程序运行
            import time

            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down scheduler...")
            scheduler.shutdown()

    else:
        # 单次执行模式
        logger.info("Running single flywheel execution")
        try:
            stats = run_daily_flywheel()
            logger.info(
                f"Flywheel completed: "
                f"collected={stats['collected']}, "
                f"analyzed={stats['analyzed']}, "
                f"report_generated={stats['report_generated']}"
            )
        except Exception as e:
            logger.error(f"Single flywheel execution failed: {e}")
            # 优雅退出，不抛出异常
            return
