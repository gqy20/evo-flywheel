"""论文相关 API 端点"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

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
