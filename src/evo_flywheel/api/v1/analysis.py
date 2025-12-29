"""论文分析调度 API 端点"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from evo_flywheel.analyzers.batch import analyze_papers_batch
from evo_flywheel.api.deps import get_db
from evo_flywheel.db.models import Paper
from evo_flywheel.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/trigger")
def trigger_analysis(
    limit: int = Query(50, ge=1, le=1000, description="分析论文数量限制"),
    min_score: int | None = Query(None, description="最低重要性评分过滤"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """触发论文分析

    对未分析的论文进行批量分析，使用 LLM 提取关键信息
    """
    try:
        # 获取未分析的论文（importance_score 为空且 abstract 不为空）
        query = db.query(Paper).filter(
            Paper.importance_score.is_(None),
            Paper.abstract.isnot(None),
            Paper.abstract != "",
        )

        # 应用最低评分过滤
        if min_score is not None:
            query = query.filter(Paper.importance_score >= min_score)

        papers = query.order_by(Paper.created_at.desc()).limit(limit).all()

        if not papers:
            return {"analyzed": 0, "total": 0, "message": "没有需要分析的论文"}

        # 转换为字典格式供批量分析使用
        papers_dicts = []
        for p in papers:
            papers_dicts.append(
                {
                    "id": p.id,
                    "title": p.title,
                    "abstract": p.abstract,
                    "authors": p.authors,
                    "doi": p.doi,
                    "publication_date": p.publication_date,  # 已经是字符串
                }
            )

        logger.info(f"开始分析 {len(papers_dicts)} 篇论文")

        # 调用批量分析模块
        analyzed_papers = analyze_papers_batch(
            papers_dicts,
            max_concurrent=3,  # 并发控制，避免 API 限流
            continue_on_error=True,
        )

        # 构建 ID 到分析结果的映射（更安全，不依赖顺序）
        id_to_analysis = {}
        for paper_dict in analyzed_papers:
            paper_id = paper_dict.get("id")
            if paper_id is not None:
                id_to_analysis[paper_id] = paper_dict

        # 更新数据库
        analyzed_count = 0
        for paper_obj in papers:
            paper_id = paper_obj.id
            analysis_result: dict[str, Any] | None = id_to_analysis.get(paper_id)

            if not analysis_result:
                logger.warning(f"论文 {paper_id} 的分析结果未找到")
                continue

            # 类型断言：我们已经检查了 analysis_result 不是 None
            assert analysis_result is not None  # noqa: B011

            # 检查分析是否成功
            if "_error" in analysis_result:
                logger.warning(f"论文 {paper_id} 分析失败: {analysis_result['_error']}")
                continue

            # 更新数据库记录
            paper_obj.taxa = analysis_result.get("taxa")  # type: ignore
            paper_obj.evolutionary_scale = analysis_result.get("evolutionary_scale")  # type: ignore
            paper_obj.research_method = analysis_result.get("research_method")  # type: ignore
            # key_findings 是列表，需要使用 key_findings_list 属性存储为 JSON
            key_findings = analysis_result.get("key_findings")
            if key_findings:
                paper_obj.key_findings_list = key_findings  # type: ignore
            paper_obj.evolutionary_mechanism = analysis_result.get("evolutionary_mechanism")  # type: ignore
            paper_obj.importance_score = analysis_result.get("importance_score")  # type: ignore
            paper_obj.innovation_summary = analysis_result.get("innovation_summary")  # type: ignore

            analyzed_count += 1

        db.commit()

        logger.info(f"分析完成: {analyzed_count}/{len(papers)} 篇论文")

        return {
            "analyzed": analyzed_count,
            "total": len(papers),
            "message": f"已分析 {analyzed_count} 篇论文",
        }

    except Exception as e:
        db.rollback()
        logger.error(f"分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {e!s}")


@router.get("/status")
def get_analysis_status(db: Session = Depends(get_db)) -> dict[str, Any]:
    """获取分析状态

    返回论文分析统计信息
    """
    # 统计未分析的论文
    unanalyzed = db.query(Paper).filter(Paper.importance_score.is_(None)).count()
    total = db.query(Paper).count()
    analyzed = total - unanalyzed

    return {
        "total": total,
        "analyzed": analyzed,
        "unanalyzed": unanalyzed,
        "progress": round(analyzed / total * 100, 2) if total > 0 else 0,
    }
