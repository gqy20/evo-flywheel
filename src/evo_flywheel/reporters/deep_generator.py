"""深度报告生成器

使用 LLM 生成洞察性的每日报告，包含：
- 研究概要
- 热点话题
- 趋势分析
- 推荐论文
"""

import json
from collections import defaultdict
from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from evo_flywheel.analyzers import llm
from evo_flywheel.analyzers.prompts import build_report_prompt
from evo_flywheel.db import crud
from evo_flywheel.db.models import DailyReport, Paper
from evo_flywheel.logging import get_logger

logger = get_logger(__name__)


def generate_deep_report(target_date: date, db: Session) -> DailyReport:
    """生成深度每日报告

    流程：
    1. 查询当天已分析的论文
    2. 按主题聚类
    3. 调用 LLM 生成深度分析
    4. 保存到数据库

    Args:
        target_date: 目标日期
        db: 数据库会话

    Returns:
        DailyReport: 生成的报告对象

    Raises:
        ValueError: 当天没有已分析的论文
    """
    # 1. 查询当天论文（只取已分析的）
    next_day = target_date + timedelta(days=1)
    papers = (
        db.query(Paper)
        .filter(
            Paper.created_at >= target_date,
            Paper.created_at < next_day,
            Paper.importance_score.isnot(None),  # 只取已分析的
        )
        .order_by(Paper.importance_score.desc())
        .all()
    )

    if not papers:
        logger.warning(f"No analyzed papers found for {target_date}")
        raise ValueError(f"{target_date} 没有已分析的论文")

    logger.info(f"Found {len(papers)} analyzed papers for {target_date}")

    # 2. 数据预处理
    paper_dicts = [_paper_to_dict(p) for p in papers]

    # 3. 主题聚类
    clusters = _cluster_papers(paper_dicts)

    # 4. 统计信息
    stats = _calculate_stats(papers, clusters)

    # 5. LLM 生成深度分析（带错误处理）
    try:
        llm_result = _generate_llm_analysis(paper_dicts, clusters, stats)
    except Exception as e:
        logger.error(f"LLM analysis failed: {e}, using fallback")
        # 使用基础结构作为降级方案
        llm_result = {
            "research_summary": f"今天共采集 {stats['total']} 篇论文，其中 {stats['high_value']} 篇高价值论文。",
            "hot_topics": [],
            "trend_analysis": {},
            "recommended_papers": [
                {
                    "paper_id": p["id"],
                    "title": p["title"],
                    "reason": "高价值论文",
                    "priority": "interesting",
                }
                for p in paper_dicts[:5]
            ],
            "top_paper_ids": [p["id"] for p in paper_dicts[:10]],
        }

    # 6. 保存报告
    report = crud.create_daily_report(
        db,
        report_date=target_date.isoformat(),
        total_papers=len(papers),
        high_value_papers=stats["high_value"],
        top_paper_ids=llm_result.get("top_paper_ids", [p["id"] for p in paper_dicts[:10]]),
        report_content=json.dumps(llm_result, ensure_ascii=False),
    )

    # 7. 保存聚类信息
    _save_clusters(db, report.id, clusters)

    logger.info(f"Deep report generated for {target_date}: report_id={report.id}")
    return report


def _paper_to_dict(paper: Paper) -> dict[str, Any]:
    """将 Paper 对象转换为字典

    Args:
        paper: 论文对象

    Returns:
        dict: 论文字典
    """
    return {
        "id": paper.id,
        "title": paper.title,
        "authors": paper.authors_list,
        "abstract": paper.abstract,
        "taxa": paper.taxa,
        "evolutionary_scale": paper.evolutionary_scale,
        "research_method": paper.research_method,
        "key_findings": paper.findings_list,
        "evolutionary_mechanism": paper.evolutionary_mechanism,
        "innovation_summary": paper.innovation_summary,
        "importance_score": paper.importance_score,
        "journal": paper.journal,
        "doi": paper.doi,
    }


def _cluster_papers(papers: list[dict[str, Any]]) -> dict[str, list[dict]]:
    """按主题聚类论文

    聚类维度：
    1. 物种 (taxa)
    2. 研究方法 (research_method)

    Args:
        papers: 论文列表

    Returns:
        dict: 聚类字典，key 为 "物种_方法"
    """
    clusters = defaultdict(list)

    for paper in papers:
        # 获取字段，使用默认值处理空值
        taxa = paper.get("taxa") or "Unknown"
        method = paper.get("research_method") or "Unknown"

        # 清理字段名中的空格，用于生成聚类key
        taxa_clean = taxa.replace(" ", "_")
        method_clean = method.replace(" ", "_")

        cluster_key = f"{taxa_clean}_{method_clean}"
        clusters[cluster_key].append(paper)

    return dict(clusters)


def _calculate_stats(papers: list[Paper], clusters: dict) -> dict[str, Any]:
    """计算统计信息

    Args:
        papers: 论文列表
        clusters: 聚类字典

    Returns:
        dict: 统计信息
    """
    high_value = [p for p in papers if p.importance_score and p.importance_score >= 80]

    taxa_set = {p.taxa for p in papers if p.taxa}
    method_set = {p.research_method for p in papers if p.research_method}

    return {
        "total": len(papers),
        "high_value": len(high_value),
        "taxa_count": len(taxa_set),
        "methods_count": len(method_set),
        "cluster_count": len(clusters),
    }


def _generate_llm_analysis(
    papers: list[dict[str, Any]],
    clusters: dict[str, list[dict]],
    stats: dict[str, Any],
) -> dict[str, Any]:
    """调用 LLM 生成深度分析

    Args:
        papers: 论文列表
        clusters: 聚类字典
        stats: 统计信息

    Returns:
        dict: LLM 生成的分析结果
    """
    prompt = build_report_prompt(papers, clusters, stats)

    try:
        # 调用 LLM（复用现有客户端）
        client = llm.get_openai_client()
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=3000,
        )

        # 解析响应（报告结构与论文分析不同，直接解析 JSON）
        import json
        import re

        content = response.choices[0].message.content

        # 提取 JSON（处理 markdown 代码块）
        json_str = content.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        json_str = json_str.strip()

        # 从文本中提取 JSON 对象
        json_match = re.search(r"\{.*\}", json_str, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)

        # 修复常见 JSON 问题（复用 llm 模块的修复逻辑）
        json_str = llm._fix_json(json_str)

        # 解析 JSON
        result: dict[str, Any] = json.loads(json_str)

        # 确保 top_paper_ids 存在
        if "top_paper_ids" not in result:
            result["top_paper_ids"] = [p["id"] for p in papers[:10]]

        return result

    except Exception as e:
        logger.error(f"LLM analysis failed: {e}")
        # 返回基础结构
        return {
            "research_summary": f"今天共采集 {stats['total']} 篇论文，其中 {stats['high_value']} 篇高价值论文。",
            "hot_topics": [],
            "trend_analysis": {},
            "recommended_papers": [
                {
                    "paper_id": p["id"],
                    "title": p["title"],
                    "reason": "高价值论文",
                    "priority": "interesting",
                }
                for p in papers[:5]
            ],
            "top_paper_ids": [p["id"] for p in papers[:10]],
        }


def _save_clusters(
    db: Session,
    report_id: int,
    clusters: dict[str, list[dict]],
) -> None:
    """保存论文聚类信息

    Args:
        db: 数据库会话
        report_id: 报告ID
        clusters: 聚类字典
    """
    for cluster_name, cluster_papers in clusters.items():
        paper_ids = [p["id"] for p in cluster_papers]

        # 使用聚类名称作为摘要（可以后续用 LLM 增强）
        summary = f"{cluster_name.replace('_', ' ')} 相关研究，共 {len(paper_ids)} 篇"

        crud.create_paper_cluster(
            db,
            report_id=report_id,
            cluster_name=cluster_name,
            paper_ids=paper_ids,
            cluster_summary=summary,
        )

    logger.info(f"Saved {len(clusters)} clusters for report {report_id}")
