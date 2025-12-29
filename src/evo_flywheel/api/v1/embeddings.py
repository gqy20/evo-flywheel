"""向量嵌入相关 API 端点"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from evo_flywheel.api.deps import get_db
from evo_flywheel.db.models import Paper
from evo_flywheel.logging import get_logger
from evo_flywheel.vector.client import get_chroma_client
from evo_flywheel.vector.embeddings import generate_embedding

router = APIRouter()
logger = get_logger(__name__)


@router.post("/rebuild")
def rebuild_embeddings(
    force: bool = Query(False, description="强制重建所有论文的向量"),
    db: Session = Depends(get_db),
) -> dict:
    """重建向量索引

    为所有论文重新生成并存储向量嵌入
    """
    client = get_chroma_client()

    # 获取或创建集合
    collection = client.get_or_create_collection("evolutionary_papers")

    # 如果强制重建，清空现有集合
    if force:
        client.delete_collection("evolutionary_papers")
        collection = client.get_or_create_collection("evolutionary_papers")

    # 获取需要向量化的论文
    if force:
        papers = db.query(Paper).filter(Paper.abstract.isnot(None)).all()
    else:
        papers = (
            db.query(Paper)
            .filter(Paper.embedded.is_(False))
            .filter(Paper.abstract.isnot(None))
            .all()
        )

    if not papers:
        return {"rebuilt": 0, "message": "没有需要向量化的论文"}

    try:
        # 批量生成向量
        ids = []
        embeddings = []
        metadatas = []
        skipped = 0

        for paper in papers:
            if not paper.abstract:
                skipped += 1
                continue

            try:
                embedding = generate_embedding(paper.abstract)  # type: ignore[arg-type]
                ids.append(str(paper.id))
                embeddings.append(embedding)
                metadatas.append(
                    {
                        "title": paper.title,
                        "authors": paper.authors or "",
                        "publication_date": (
                            paper.publication_date if paper.publication_date else None
                        ),
                    }
                )

                # 标记为已向量化
                paper.embedded = True  # type: ignore[assignment]

            except Exception as e:
                # 单个论文失败不影响整体，记录日志
                logger.warning(f"论文 {paper.id} 向量化失败: {e}")
                skipped += 1

        # 批量添加到 Chroma
        if embeddings:
            collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas)  # type: ignore[arg-type]

        db.commit()

        return {
            "rebuilt": len(embeddings),
            "total": len(papers),
            "skipped": skipped,
            "message": f"成功向量化 {len(embeddings)} 篇论文，跳过 {skipped} 篇",
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"重建向量索引失败: {e!s}")


@router.get("/status")
def get_embeddings_status(db: Session = Depends(get_db)) -> dict[str, Any]:
    """获取向量索引状态

    返回论文向量化统计信息
    """
    # 统计未向量化的论文
    unembedded = (
        db.query(Paper).filter(Paper.embedded.is_(False)).filter(Paper.abstract.isnot(None)).count()
    )
    total_with_abstract = db.query(Paper).filter(Paper.abstract.isnot(None)).count()
    embedded = total_with_abstract - unembedded

    return {
        "total": total_with_abstract,
        "embedded": embedded,
        "unembedded": unembedded,
        "progress": round(embedded / total_with_abstract * 100, 2)
        if total_with_abstract > 0
        else 0,
    }
