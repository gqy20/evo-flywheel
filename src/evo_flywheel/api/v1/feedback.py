"""用户反馈相关 API 端点"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from evo_flywheel.api.deps import get_db
from evo_flywheel.db import crud
from evo_flywheel.db.models import Feedback

router = APIRouter()


class FeedbackCreate(BaseModel):
    """创建反馈请求模型"""

    paper_id: int = Field(..., description="论文ID", ge=1)
    rating: int = Field(..., description="评分 1-5", ge=1, le=5)
    is_helpful: bool | None = Field(None, description="是否有帮助")
    comment: str | None = Field(None, description="评论", max_length=1000)


class FeedbackResponse(BaseModel):
    """反馈响应模型"""

    id: int
    paper_id: int
    rating: int
    is_helpful: bool | None
    comment: str | None

    model_config = {"from_attributes": True}


@router.post("")
def create_feedback(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    """创建用户反馈

    提交对论文的评分和评论
    """
    # 检查论文是否存在
    from evo_flywheel.db.models import Paper

    if not db.query(Paper).filter(Paper.id == data.paper_id).first():
        raise HTTPException(status_code=404, detail="论文不存在")

    try:
        feedback: Feedback = crud.create_feedback(
            db,
            paper_id=data.paper_id,
            rating=data.rating,
            is_helpful=data.is_helpful,
            comment=data.comment,
        )
        return FeedbackResponse(
            id=feedback.id,
            paper_id=feedback.paper_id,
            rating=feedback.rating,
            is_helpful=feedback.is_helpful,
            comment=feedback.comment,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建反馈失败: {e!s}")


@router.get("")
def get_feedbacks(
    paper_id: int | None = Query(None, description="论文ID"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """获取反馈列表

    支持按论文ID筛选
    """
    if paper_id is not None:
        feedbacks = crud.get_feedbacks_by_paper(db, paper_id)
    else:
        # 获取所有反馈（限制数量）
        feedbacks = db.query(Feedback).order_by(Feedback.created_at.desc()).limit(100).all()

    return {
        "feedbacks": [
            {
                "id": f.id,
                "paper_id": f.paper_id,
                "rating": f.rating,
                "is_helpful": f.is_helpful,
                "comment": f.comment,
            }
            for f in feedbacks
        ]
    }
