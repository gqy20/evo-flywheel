"""批量分析模块

提供批量论文分析功能，支持并发控制、结果缓存和错误处理
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Any

from evo_flywheel.analyzers import llm
from evo_flywheel.logging import get_logger

logger = get_logger(__name__)

# 模块级缓存（使用锁保护线程安全）
_analysis_cache: dict[str, dict[str, Any]] = {}
_cache_lock = Lock()


def is_analyzed(paper: dict[str, Any]) -> bool:
    """检查论文是否已经分析过

    判断标准：
    - 包含所有必需的分析字段
    - importance_score > 0
    - key_findings 非空

    Args:
        paper: 论文数据字典

    Returns:
        bool: 如果论文已分析返回 True，否则返回 False
    """
    required_fields = [
        "taxa",
        "evolutionary_scale",
        "research_method",
        "key_findings",
        "evolutionary_mechanism",
        "importance_score",
        "innovation_summary",
    ]

    # 检查是否包含所有必需字段
    for field in required_fields:
        if field not in paper:
            return False

    # 检查评分为正数
    if not isinstance(paper.get("importance_score"), int) or paper.get("importance_score", 0) <= 0:
        return False

    # 检查 key_findings 是非空列表
    key_findings = paper.get("key_findings", [])
    return isinstance(key_findings, list) and bool(key_findings)


def get_cached_analysis(paper: dict[str, Any]) -> dict[str, Any] | None:
    """获取论文的缓存分析结果

    缓存键优先级：
    1. 使用 paper["id"]（如果存在）
    2. 使用 paper["doi"]（如果存在）
    3. 返回 None（无法生成缓存键）

    Args:
        paper: 论文数据字典

    Returns:
        dict | None: 缓存的分析结果，如果不存在返回 None
    """
    cache_key = _get_cache_key(paper)
    if not cache_key:
        return None

    with _cache_lock:
        return _analysis_cache.get(cache_key)


def _get_cache_key(paper: dict[str, Any]) -> str | None:
    """生成论文的缓存键

    Args:
        paper: 论文数据字典

    Returns:
        str | None: 缓存键，如果无法生成返回 None
    """
    if "id" in paper:
        return f"paper:{paper['id']}"
    if "doi" in paper:
        return f"doi:{paper['doi']}"
    return None


def _set_cache(cache_key: str, result: dict[str, Any]) -> None:
    """设置缓存

    Args:
        cache_key: 缓存键
        result: 分析结果字典
    """
    with _cache_lock:
        _analysis_cache[cache_key] = result


def analyze_papers_batch(
    papers: list[dict[str, Any]],
    max_concurrent: int = 3,
    continue_on_error: bool = True,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """批量分析论文

    功能特性：
    - 自动跳过已分析的论文
    - 使用缓存避免重复分析（相同 DOI 或 ID）
    - 支持并发控制（避免 API 限流）
    - 支持错误处理（单篇失败不影响整体）
    - 支持 dry_run 模式（不调用 API）
    - 追踪统计信息（标记缓存和跳过的论文）

    Args:
        papers: 论文列表
        max_concurrent: 最大并发数（默认 3）
        continue_on_error: 遇到错误是否继续（默认 True）
        dry_run: 是否为 dry_run 模式（默认 False）

    Returns:
        list[dict]: 分析后的论文列表，包含原始数据和分析结果
    """
    if not papers:
        return []

    results = []
    cached_count = 0
    skipped_count = 0

    for paper in papers:
        # 检查是否已分析
        if is_analyzed(paper):
            paper["_cached"] = True
            cached_count += 1
            results.append(paper)
            continue

        # 检查缓存
        cached = get_cached_analysis(paper)
        if cached:
            paper.update(cached)
            paper["_cached"] = True
            cached_count += 1
            results.append(paper)
            continue

        # dry_run 模式：不调用 API，标记跳过
        if dry_run:
            paper["_skipped"] = True
            skipped_count += 1
            results.append(paper)
            continue

        results.append(paper)

    # 筛选需要分析的论文
    papers_to_analyze = [p for p in results if "_cached" not in p and "_skipped" not in p]

    if not papers_to_analyze:
        logger.info(f"所有论文已完成或缓存: cached={cached_count}, skipped={skipped_count}")
        return results

    # 并发分析
    analyzed = _analyze_concurrent(
        papers_to_analyze,
        max_concurrent=max_concurrent,
        continue_on_error=continue_on_error,
    )

    # 合并结果：_analyze_single 返回的是新字典，需要更新原始 paper
    # 使用 id(paper) 作为键来匹配并更新原始对象
    id_to_analyzed = {id(p): a for p, a in zip(papers_to_analyze, analyzed, strict=True)}

    # 更新 results 中的原始 paper 对象
    final_results = []
    for paper in results:
        paper_id = id(paper)
        if paper_id in id_to_analyzed:
            # 使用分析后的新字典替换原始 paper
            final_results.append(id_to_analyzed[paper_id])
        else:
            # 保留原始 paper（已缓存或跳过的）
            final_results.append(paper)

    logger.info(
        f"批量分析完成: total={len(papers)}, cached={cached_count}, "
        f"analyzed={len(papers_to_analyze)}, skipped={skipped_count}"
    )

    return final_results


def _analyze_concurrent(
    papers: list[dict[str, Any]],
    max_concurrent: int,
    continue_on_error: bool,
) -> list[dict[str, Any]]:
    """并发分析论文

    Args:
        papers: 待分析的论文列表
        max_concurrent: 最大并发数
        continue_on_error: 遇到错误是否继续

    Returns:
        list[dict]: 分析后的论文列表
    """

    def _analyze_single(paper: dict[str, Any]) -> dict[str, Any] | None:
        """分析单篇论文

        Args:
            paper: 论文数据

        Returns:
            dict | None: 分析结果，失败返回 None
        """
        try:
            # 提取标题和摘要
            title = paper.get("title", "")
            abstract = paper.get("abstract", "")

            if not title or not abstract:
                logger.warning(f"论文 {paper.get('id', paper.get('doi'))} 缺少标题或摘要")
                return {**paper, "_error": "缺少标题或摘要"}

            # 调用 LLM 分析
            result: llm.AnalysisResult = llm.analyze_paper(title, abstract)

            # 转换为字典
            analysis = {
                "taxa": result.taxa,
                "evolutionary_scale": result.evolutionary_scale,
                "research_method": result.research_method,
                "key_findings": result.key_findings,
                "evolutionary_mechanism": result.evolutionary_mechanism,
                "importance_score": result.importance_score,
                "innovation_summary": result.innovation_summary,
                "_tokens": result.usage.total_tokens,
            }

            # 更新缓存
            cache_key = _get_cache_key(paper)
            if cache_key:
                _set_cache(cache_key, analysis)

            return {**paper, **analysis}

        except Exception as e:
            logger.error(f"分析论文 {paper.get('id', paper.get('doi'))} 失败: {e}")
            if continue_on_error:
                return {**paper, "_error": str(e)}
            raise

    # 使用线程池并发分析
    with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        # 存储 future 到原始索引的映射，保证结果顺序一致
        future_to_index = {
            executor.submit(_analyze_single, paper): i for i, paper in enumerate(papers)
        }

        # 预分配结果列表，保持原始顺序
        results: list[dict[str, Any] | None] = [None] * len(papers)

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                result = future.result()
                results[index] = result if result else {**papers[index], "_error": "分析返回空结果"}
            except Exception as e:
                paper = papers[index]
                logger.error(f"处理论文 {paper.get('id', paper.get('doi'))} 时发生错误: {e}")
                if continue_on_error:
                    results[index] = {**paper, "_error": str(e)}
                else:
                    raise

    # 过滤掉 None 值（理论上不应该有，但为了类型安全）
    return [r for r in results if r is not None]
