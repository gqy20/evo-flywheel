"""语义搜索 API 端点"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from evo_flywheel.api.deps import get_db
from evo_flywheel.db.models import Paper
from evo_flywheel.vector.client import get_chroma_client
from evo_flywheel.vector.embeddings import generate_embedding

router = APIRouter()


@router.get("/semantic")
def semantic_search(
    q: str = Query(..., min_length=1, description="搜索查询"),
    limit: int = Query(10, ge=1, le=50, description="返回结果数"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """语义搜索论文

    使用向量嵌入进行语义相似度搜索
    """
    try:
        # 生成查询向量
        query_vector = generate_embedding(q)

        # 查询 Chroma
        client = get_chroma_client()
        collection = client.get_or_create_collection("evolutionary_papers")

        results = collection.query(
            query_embeddings=[query_vector],
            n_results=limit,
        )

        # 格式化结果
        papers = []
        for i, paper_id in enumerate(results["ids"][0]):
            paper = db.query(Paper).filter(Paper.id == int(paper_id)).first()
            if paper:
                papers.append(
                    {
                        "id": paper.id,
                        "title": results["metadatas"][0][i].get("title", paper.title),
                        "abstract": paper.abstract,
                        "similarity": 1 - results["distances"][0][i],  # 转换为相似度
                    }
                )

        return {"results": papers}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {e!s}")


@router.post("/similar")
def find_similar_papers(
    paper_id: int = Query(..., description="参考论文 ID"),
    limit: int = Query(5, ge=1, le=20, description="返回结果数"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """查找相似论文

    基于指定论文查找相似研究
    """
    # 获取参考论文
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="论文不存在")

    if not paper.abstract:
        raise HTTPException(status_code=400, detail="论文摘要为空，无法查找相似论文")

    try:
        # 生成向量
        query_vector = generate_embedding(paper.abstract)

        # 查询 Chroma
        client = get_chroma_client()
        collection = client.get_or_create_collection("evolutionary_papers")

        results = collection.query(
            query_embeddings=[query_vector],
            n_results=limit + 1,  # +1 因为结果包含自己
        )

        # 格式化结果（排除自己）
        similar_papers = []
        for i, result_id in enumerate(results["ids"][0]):
            if int(result_id) == paper_id:
                continue  # 跳过自己

            similar_paper = db.query(Paper).filter(Paper.id == int(result_id)).first()
            if similar_paper:
                similar_papers.append(
                    {
                        "id": similar_paper.id,
                        "title": similar_paper.title,
                        "abstract": similar_paper.abstract,
                        "similarity": 1 - results["distances"][0][i],
                    }
                )

        return {"similar_papers": similar_papers}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查找失败: {e!s}")
