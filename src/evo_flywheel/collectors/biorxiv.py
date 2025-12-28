"""bioRxiv API 采集器模块

通过 bioRxiv 官方 API 获取预印本论文
"""

from datetime import datetime
from typing import Any

import requests

from evo_flywheel.logging import get_logger

logger = get_logger(__name__)

# bioRxiv API 基础 URL
BIORXIV_API_BASE = "https://api.biorxiv.org/details/biorxiv"
DEFAULT_CATEGORY = "evolutionary_biology"


def build_api_url(
    start_date: datetime,
    end_date: datetime,
    category: str = DEFAULT_CATEGORY,
) -> str:
    """构建 bioRxiv API URL

    Args:
        start_date: 开始日期
        end_date: 结束日期
        category: 论文分类 (默认: evolutionary_biology)

    Returns:
        str: 完整的 API URL
    """
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    url = f"{BIORXIV_API_BASE}/{start_str}/{end_str}?category={category}"
    logger.debug(f"Built bioRxiv API URL: {url}")

    return url


def parse_biorxiv_date(date_str: str | None) -> str | None:
    """解析 bioRxiv 日期字符串

    Args:
        date_str: 日期字符串 (YYYY-MM-DD 格式)

    Returns:
        str | None: 解析后的日期字符串，无效返回 None
    """
    if not date_str:
        return None

    try:
        # 尝试解析日期
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        logger.warning(f"Invalid date format: {date_str}")
        return None


def parse_biorxiv_paper(paper_data: dict[str, Any]) -> dict[str, Any]:
    """解析 bioRxiv 论文数据

    Args:
        paper_data: bioRxiv API 返回的论文数据

    Returns:
        dict: 解析后的论文数据，无效返回空字典
    """
    # 提取标题（必需字段）
    title = paper_data.get("title", "").strip()
    if not title:
        logger.debug("Skipping paper without title")
        return {}

    # 提取 DOI
    doi = paper_data.get("doi", "")

    # 解析作者（分号分隔）
    authors_str = paper_data.get("authors", "")
    authors = []
    if authors_str:
        authors = [a.strip() for a in authors_str.split(";") if a.strip()]

    # 提取摘要
    abstract = paper_data.get("abstract", "").strip() or None

    # 解析日期
    date_str = paper_data.get("date")
    publication_date = parse_biorxiv_date(date_str)

    # 构建结果
    result = {
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "doi": doi,
        "url": f"https://doi.org/{doi}" if doi else None,
        "publication_date": publication_date,
        "source": "bioRxiv",
    }

    return result


def fetch_biorxiv_papers(
    start_date: datetime,
    end_date: datetime,
    category: str = DEFAULT_CATEGORY,
    timeout: int = 60,
) -> list[dict[str, Any]]:
    """从 bioRxiv API 获取论文列表

    Args:
        start_date: 开始日期
        end_date: 结束日期
        category: 论文分类
        timeout: 请求超时时间（秒）

    Returns:
        list[dict]: 解析后的论文列表

    Raises:
        Exception: 网络请求失败
        TimeoutError: 请求超时
    """
    url = build_api_url(start_date, end_date, category)

    logger.info(f"Fetching bioRxiv papers from {url}")

    try:
        response = requests.get(url, params={"format": "json"}, timeout=timeout)
        response.raise_for_status()
    except TimeoutError:
        logger.error(f"Timeout fetching bioRxiv API: {url}")
        raise
    except Exception as e:
        logger.error(f"Failed to fetch bioRxiv papers: {e}")
        raise

    data = response.json()

    # 解析论文列表
    papers = []
    collection = data.get("collection", [])

    for paper_data in collection:
        try:
            paper = parse_biorxiv_paper(paper_data)
            if paper:  # 跳过无效论文
                papers.append(paper)
        except Exception as e:
            logger.warning(f"Failed to parse paper: {e}")
            continue

    logger.info(f"Fetched {len(papers)} papers from bioRxiv")
    return papers
