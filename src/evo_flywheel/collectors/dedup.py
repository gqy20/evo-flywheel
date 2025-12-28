"""数据去重模块

基于 DOI 和标题的论文去重逻辑
"""

import re
import unicodedata
from typing import Any

from evo_flywheel.logging import get_logger

logger = get_logger(__name__)


def normalize_title(title: str) -> str:
    """规范化标题用于去重

    Args:
        title: 原始标题

    Returns:
        str: 规范化后的标题
    """
    # 替换 Unicode 分数字符 (先处理)
    unicode_fractions = {
        "½": "1/2",
        "⅓": "1/3",
        "⅔": "2/3",
        "¼": "1/4",
        "¾": "3/4",
        "⅕": "1/5",
        "⅛": "1/8",
        "⅜": "3/8",
        "⅝": "5/8",
        "⅞": "7/8",
    }
    for unicode_char, replacement in unicode_fractions.items():
        title = title.replace(unicode_char, replacement)

    # 转换为小写
    title = title.lower()
    # Unicode 规范化 (NFKD 分解组合字符)
    title = unicodedata.normalize("NFKD", title)
    # 移除变音符号
    title = "".join(c for c in title if not unicodedata.combining(c))
    # 压缩空白字符
    title = re.sub(r"\s+", " ", title)
    # 去除首尾空白
    title = title.strip()

    return title


def extract_paper_key(paper: dict[str, Any]) -> str | None:
    """提取论文唯一键

    优先使用 DOI，其次使用规范化后的标题

    Args:
        paper: 论文数据字典

    Returns:
        str | None: 论文键 (格式: "doi:xxx" 或 "title:xxx")，无效返回 None
    """
    # 优先使用 DOI
    doi = paper.get("doi") or ""
    if doi:
        doi = str(doi).strip()
        if doi:
            return f"doi:{doi}"

    # 其次使用标题
    title = paper.get("title") or ""
    if title:
        title = str(title).strip()
        if title:
            normalized = normalize_title(title)
            return f"title:{normalized}"

    # 无法提取键
    logger.warning("Paper has no DOI or title")
    return None


def is_duplicate_paper(paper: dict[str, Any], existing_keys: set[str]) -> bool:
    """判断论文是否重复

    Args:
        paper: 待检查的论文
        existing_keys: 已存在的论文键集合

    Returns:
        bool: True 表示重复，False 表示不重复
    """
    key = extract_paper_key(paper)
    if key is None:
        # 无法提取键，视为重复（跳过）
        return True

    return key in existing_keys


def remove_duplicate_papers(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """移除重复论文

    保留第一次出现的论文，后续重复的将被移除

    Args:
        papers: 论文列表

    Returns:
        list[dict]: 去重后的论文列表
    """
    result: list[dict[str, Any]] = []
    seen_keys: set[str] = set()

    for paper in papers:
        key = extract_paper_key(paper)

        if key is None:
            # 无效论文，跳过
            logger.debug("Skipping invalid paper without DOI or title")
            continue

        if key not in seen_keys:
            # 首次出现，保留
            seen_keys.add(key)
            result.append(paper)
        else:
            # 重复论文，跳过
            logger.debug(f"Duplicate paper found: {key}")

    removed_count = len(papers) - len(result)
    if removed_count > 0:
        logger.info(f"Removed {removed_count} duplicate papers")

    return result
