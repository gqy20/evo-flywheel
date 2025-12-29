"""论文相关 API 端点"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from evo_flywheel.analyzers.llm import analyze_paper
from evo_flywheel.api.deps import get_db
from evo_flywheel.api.schemas import PaperListResponse, PaperResponse
from evo_flywheel.db.models import Paper

router = APIRouter()


@router.get("", response_model=PaperListResponse)
def list_papers(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    taxa: str | None = Query(None, description="筛选分类群"),
    min_score: int | None = Query(None, ge=0, le=100, description="最低重要性评分"),
    db: Session = Depends(get_db),
) -> PaperListResponse:
    """获取论文列表

    支持分页和按 taxa/importance_score 筛选
    """
    query = db.query(Paper)

    if taxa:
        query = query.filter(Paper.taxa == taxa)
    if min_score is not None:
        query = query.filter(Paper.importance_score >= min_score)

    total = query.count()
    papers = query.order_by(Paper.publication_date.desc()).offset(skip).limit(limit).all()

    return PaperListResponse(
        total=total,
        papers=[PaperResponse.from_orm_with_authors(p) for p in papers],
    )


@router.get("/{paper_id}", response_model=PaperResponse)
def get_paper(paper_id: int, db: Session = Depends(get_db)) -> PaperResponse:
    """获取单篇论文详情"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="论文不存在")
    return PaperResponse.from_orm_with_authors(paper)


@router.post("/{paper_id}/analyze")
def analyze_single_paper(paper_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """分析单篇论文

    使用 LLM 分析论文的进化生物学特征
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="论文不存在")

    if not paper.abstract:
        raise HTTPException(status_code=400, detail="论文摘要为空，无法分析")

    try:
        result = analyze_paper(paper.title, paper.abstract)

        # 更新论文记录
        paper.taxa = result.taxa
        paper.evolutionary_scale = result.evolutionary_scale
        paper.research_method = result.research_method
        paper.findings_list = result.key_findings
        paper.evolutionary_mechanism = result.evolutionary_mechanism
        paper.innovation_summary = result.innovation_summary
        paper.importance_score = result.importance_score

        db.commit()
        db.refresh(paper)

        return {
            "paper_id": paper.id,
            "taxa": paper.taxa,
            "importance_score": paper.importance_score,
            "key_findings": paper.findings_list,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"分析失败: {e!s}")


@router.post("/analyze-batch")
def analyze_batch_papers(
    limit: int = Query(10, ge=1, le=50, description="批量分析数量"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """批量分析未分析的论文

    按优先级分析未处理的论文
    """
    from evo_flywheel.analyzers.batch import analyze_papers_batch

    # 获取未分析的论文
    papers = (
        db.query(Paper)
        .filter(Paper.importance_score.is_(None))
        .filter(Paper.abstract.isnot(None))
        .order_by(Paper.publication_date.desc())
        .limit(limit)
        .all()
    )

    if not papers:
        return {"analyzed": 0, "message": "没有待分析的论文"}

    # 转换为字典格式
    paper_dicts = [
        {
            "id": p.id,
            "title": p.title,
            "abstract": p.abstract or "",
        }
        for p in papers
    ]

    try:
        # 批量分析
        results = analyze_papers_batch(paper_dicts)

        # 更新数据库
        analyzed_count = 0
        for paper_data, result in zip(paper_dicts, results, strict=True):
            # 检查是否成功分析（result 包含分析结果字段）
            if "taxa" not in result:
                continue

            paper = db.query(Paper).filter(Paper.id == paper_data["id"]).first()
            if paper:
                paper.taxa = result.get("taxa")
                paper.evolutionary_scale = result.get("evolutionary_scale")
                paper.research_method = result.get("research_method")
                paper.evolutionary_mechanism = result.get("evolutionary_mechanism")
                paper.innovation_summary = result.get("innovation_summary")
                paper.importance_score = result.get("importance_score")
                # key_findings 在 batch 返回中可能是字符串或列表
                key_findings = result.get("key_findings")
                if isinstance(key_findings, list):
                    paper.findings_list = key_findings
                else:
                    paper.key_findings = key_findings
                analyzed_count += 1

        db.commit()

        return {"analyzed": analyzed_count, "total": len(paper_dicts)}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"批量分析失败: {e!s}")
