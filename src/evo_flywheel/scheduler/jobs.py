"""采集任务调度模块

使用 APScheduler 实现定时数据采集任务
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml
from apscheduler.schedulers.background import BackgroundScheduler

from evo_flywheel.collectors.orchestrator import collect_from_all_sources
from evo_flywheel.logging import get_logger

logger = get_logger(__name__)


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
        return papers

    except Exception as e:
        logger.error(f"Daily collection failed: {e}")
        return []


def schedule_daily_collection(hour: int = 9, minute: int = 0) -> BackgroundScheduler:
    """配置每日定时采集任务

    Args:
        hour: 采集小时（默认 9:00）
        minute: 采集分钟（默认 0）

    Returns:
        BackgroundScheduler: 配置好的调度器实例
    """
    logger.info(f"Configuring daily collection schedule at {hour:02d}:{minute:02d}")

    scheduler = BackgroundScheduler()

    # 添加每日定时任务
    scheduler.add_job(
        collect_daily_papers,
        trigger="cron",
        hour=hour,
        minute=minute,
        id="daily_collection",
        name="Daily Paper Collection",
        replace_existing=True,
    )

    logger.info("Daily collection scheduler configured")
    return scheduler


def main() -> None:
    """命令行入口

    用法:
        evo-fetch               # 执行一次采集
        evo-fetch --schedule    # 启动调度器
    """
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        # 调度器模式
        logger.info("Starting scheduler mode")
        scheduler = schedule_daily_collection(hour=9, minute=0)
        scheduler.start()

        try:
            logger.info("Scheduler is running. Press Ctrl+C to exit.")
            # 保持程序运行
            import time

            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down scheduler...")
            scheduler.shutdown()

    else:
        # 单次执行模式
        logger.info("Running single collection")
        try:
            papers = collect_daily_papers()
            logger.info(f"Collection completed: {len(papers)} papers")
        except Exception as e:
            logger.error(f"Single collection failed: {e}")
            # 优雅退出，不抛出异常
            return
