"""RSS 采集器模块

解析 RSS feeds 并提取论文元数据
"""

import re
from typing import Any

import feedparser
import requests
from bs4 import BeautifulSoup

from evo_flywheel.logging import get_logger

logger = get_logger(__name__)


def fetch_rss_feed(url: str, timeout: int = 60) -> feedparser.FeedParserDict:
    """获取 RSS feed

    Args:
        url: RSS feed URL
        timeout: 请求超时时间（秒），默认 60 秒

    Returns:
        FeedParserDict: 解析后的 feed 对象

    Raises:
        Exception: 网络请求失败
        TimeoutError: 请求超时
    """
    logger.debug(f"Fetching RSS feed: {url}")

    # 使用浏览器 User-Agent 避免被 403 拒绝
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()
    except TimeoutError:
        logger.error(f"Timeout fetching RSS feed: {url}")
        raise
    except Exception as e:
        logger.error(f"Failed to fetch RSS feed {url}: {e}")
        raise

    return feedparser.parse(response.content)


def extract_doi(text: str | None) -> str | None:
    """从文本中提取 DOI

    Args:
        text: 输入文本

    Returns:
        str | None: 提取的 DOI，未找到返回 None
    """
    if not text:
        return None

    # 匹配 DOI 格式: 10.xxxx/xxxxx
    doi_patterns = [
        r"\b10\.\d{4,9}/[^\s\]\"\'<>]+",  # 标准 DOI 格式
        r"doi:(10\.\d{4,9}/[^\s\"\'<>]+)",  # doi: 前缀
        r"doi\.org/(10\.\d{4,9}/[^\s\"\'<>]+)",  # doi.org 域名
    ]

    for pattern in doi_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            doi = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
            # 清理可能的后缀
            doi = re.sub(r"[.,;:\s]+$", "", doi)
            return doi

    return None


def clean_html(text: str | None) -> str:
    """清理文本中的 HTML 标签

    Args:
        text: 包含 HTML 的文本

    Returns:
        str: 清理后的纯文本
    """
    if not text:
        return ""

    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def parse_authors(entry: feedparser.FeedParserDict) -> list[str]:
    """解析作者信息

    Args:
        entry: RSS 条目

    Returns:
        list[str]: 作者列表
    """
    authors = []

    # 尝试从 authors 字段获取
    if "authors" in entry and entry.authors:
        authors = [author.get("name", "") for author in entry.authors if author.get("name")]

    # 尝试从 author 字段获取（单个字符串）
    if not authors and "author" in entry and entry.author:
        author_str = entry.author
        # 优先使用分号分割（这是最常见的作者分隔符）
        if ";" in author_str:
            authors = [a.strip() for a in author_str.split(";")]
        # 其次使用 " & " 分割
        elif " & " in author_str:
            authors = [a.strip() for a in author_str.split(" & ")]
        else:
            authors = [author_str]

    # 过滤空字符串
    return [a for a in authors if a]


def parse_entry(
    entry: feedparser.FeedParserDict,
    source: str,
) -> dict[str, Any]:
    """解析单个 RSS 条目

    Args:
        entry: RSS 条目
        source: 数据源名称

    Returns:
        dict: 解析后的论文数据
    """
    # 基础字段
    title = entry.get("title", "").strip()
    url = entry.get("link", "")

    # 跳过没有标题的条目
    if not title:
        logger.debug("Skipping entry without title")
        return {}

    # 提取 DOI
    doi = None
    # 1. 从 dc_identifier 字段
    if "dc_identifier" in entry:
        doi = extract_doi(entry.dc_identifier)
    # 2. 从 description 字段
    if not doi and "description" in entry:
        doi = extract_doi(entry.description)
    # 3. 从 link 字段
    if not doi and url:
        doi = extract_doi(url)

    # 清理 DOI（去掉可能的前缀）
    if doi:
        doi = re.sub(r"^doi:", "", doi, flags=re.IGNORECASE)

    # 解析作者
    authors = parse_authors(entry)

    # 解析摘要（清理 HTML）
    abstract = None
    summary = entry.get("summary") or entry.get("description")
    if summary:
        abstract = clean_html(summary)

    # 解析发布日期
    publication_date = None
    if "published" in entry:
        publication_date = entry.published
    elif "updated" in entry:
        publication_date = entry.updated

    return {
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "doi": doi,
        "url": url,
        "publication_date": publication_date,
        "source": source,
    }


def parse_rss_entries(
    entries: list[feedparser.FeedParserDict],
    source: str,
) -> list[dict[str, Any]]:
    """批量解析 RSS 条目

    Args:
        entries: RSS 条目列表
        source: 数据源名称

    Returns:
        list[dict]: 解析后的论文数据列表
    """
    results = []

    for entry in entries:
        try:
            paper_data = parse_entry(entry, source)
            # 跳过无效条目
            if paper_data and "title" in paper_data:
                results.append(paper_data)
        except Exception as e:
            logger.warning(f"Failed to parse entry: {e}")
            continue

    logger.info(f"Parsed {len(results)} valid entries from {len(entries)} total entries")
    return results
