"""采集编排器模块

协调多个数据源，统一论文采集流程
"""

from datetime import datetime
from typing import Any

from evo_flywheel.collectors.biorxiv import fetch_biorxiv_papers
from evo_flywheel.collectors.dedup import remove_duplicate_papers
from evo_flywheel.collectors.rss import fetch_rss_feed, parse_rss_entries
from evo_flywheel.logging import get_logger

logger = get_logger(__name__)


def collect_from_biorxiv(
    start_date: datetime,
    end_date: datetime,
    category: str = "evolutionary_biology",
) -> list[dict[str, Any]]:
    """从 bioRxiv 采集论文

    Args:
        start_date: 开始日期
        end_date: 结束日期
        category: 论文分类

    Returns:
        list[dict]: 去重后的论文列表
    """
    logger.info(f"Collecting from bioRxiv: {start_date} to {end_date}")

    try:
        papers = fetch_biorxiv_papers(start_date, end_date, category)
        # 去重
        papers = remove_duplicate_papers(papers)
        logger.info(f"Collected {len(papers)} papers from bioRxiv")
        return papers
    except Exception as e:
        logger.error(f"Failed to collect from bioRxiv: {e}")
        return []


def collect_from_rss_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """从多个 RSS 源采集论文

    Args:
        sources: RSS 源配置列表，每个源包含 name 和 url

    Returns:
        list[dict]: 去重后的论文列表
    """
    all_papers: list[dict[str, Any]] = []

    for source in sources:
        url = source.get("url")
        name = source.get("name", "Unknown")

        if not url:
            logger.warning(f"RSS source {name} has no URL, skipping")
            continue

        logger.info(f"Collecting from RSS source: {name}")

        try:
            feed = fetch_rss_feed(url)
            papers = parse_rss_entries(feed.entries, source=name)
            all_papers.extend(papers)
            logger.info(f"Collected {len(papers)} papers from {name}")
        except Exception as e:
            logger.error(f"Failed to collect from {name}: {e}")
            # 继续处理其他源
            continue

    # 跨源去重
    all_papers = remove_duplicate_papers(all_papers)
    logger.info(f"Total {len(all_papers)} unique papers from RSS sources")

    return all_papers


def collect_from_all_sources(
    start_date: datetime,
    end_date: datetime,
    rss_sources: list[dict[str, Any]] | None = None,
    category: str = "evolutionary_biology",
) -> list[dict[str, Any]]:
    """从所有源采集论文

    Args:
        start_date: 开始日期
        end_date: 结束日期
        rss_sources: RSS 源配置列表（可选，默认从配置文件读取）
        category: bioRxiv 论文分类

    Returns:
        list[dict]: 去重后的论文列表
    """
    logger.info(f"Starting collection from all sources: {start_date} to {end_date}")

    all_papers: list[dict[str, Any]] = []

    # 1. 从 bioRxiv 采集
    biorxiv_papers = collect_from_biorxiv(start_date, end_date, category)
    all_papers.extend(biorxiv_papers)

    # 2. 从 RSS 源采集
    if rss_sources is None:
        # 如果没有提供源，使用默认空列表
        rss_sources = []

    rss_papers = collect_from_rss_sources(rss_sources)
    all_papers.extend(rss_papers)

    # 3. 跨源去重
    all_papers = remove_duplicate_papers(all_papers)

    logger.info(f"Total {len(all_papers)} unique papers collected from all sources")

    return all_papers
