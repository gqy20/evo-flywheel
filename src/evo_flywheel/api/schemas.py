"""API Pydantic 模型定义"""

from pydantic import BaseModel, ConfigDict, field_serializer


class PaperResponse(BaseModel):
    """论文响应模型"""

    id: int
    title: str
    authors: list[str] = []
    abstract: str | None
    doi: str | None
    url: str
    publication_date: str
    journal: str | None
    source: str | None
    taxa: str | None
    evolutionary_scale: str | None
    research_method: str | None
    evolutionary_mechanism: str | None
    importance_score: int | None
    key_findings: str | None
    innovation_summary: str | None
    embedded: bool = False

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_serializer("authors", mode="plain")
    def serialize_authors(self, value: list[str] | None) -> list[str]:
        """序列化作者列表"""
        if value is None:
            return []
        return value

    @classmethod
    def from_orm_with_authors(cls, paper) -> "PaperResponse":
        """从 ORM 模型创建，处理 authors 字段"""
        return cls(
            id=paper.id,
            title=paper.title,
            authors=paper.authors_list,
            abstract=paper.abstract,
            doi=paper.doi,
            url=paper.url,
            publication_date=str(paper.publication_date),
            journal=paper.journal,
            source=paper.source,
            taxa=paper.taxa,
            evolutionary_scale=paper.evolutionary_scale,
            research_method=paper.research_method,
            evolutionary_mechanism=paper.evolutionary_mechanism,
            importance_score=paper.importance_score,
            key_findings=paper.key_findings,
            innovation_summary=paper.innovation_summary,
            embedded=paper.embedded,
        )


class PaperListResponse(BaseModel):
    """论文列表响应模型"""

    total: int
    papers: list[PaperResponse]
