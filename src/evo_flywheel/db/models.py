"""SQLAlchemy 数据库模型定义"""

import json
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()  # type: ignore


class Paper(Base):
    """论文表"""

    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    authors = Column(Text)  # 存储为分号分隔的字符串
    abstract = Column(Text)
    doi = Column(Text, unique=True)
    url = Column(Text)
    publication_date = Column(Text)
    journal = Column(Text)
    source = Column(Text)

    # 进化生物学字段
    taxa = Column(Text)
    evolutionary_scale = Column(Text)
    research_method = Column(Text)
    evolutionary_mechanism = Column(Text)  # 存储为分号分隔

    # AI分析结果
    importance_score = Column(Integer)
    key_findings = Column(Text)  # 存储为JSON字符串
    innovation_summary = Column(Text)
    tags = Column(Text)  # 存储为分号分隔

    # 向量搜索
    embedding_id = Column(Text)  # Chroma中的ID (与id相同)
    embedded = Column(Boolean, default=False)  # 是否已生成向量

    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        return f"<Paper(id={self.id}, title='{self.title[:30]}...')>"

    @property
    def authors_list(self) -> list[str]:
        """获取作者列表"""
        if self.authors:
            return [a.strip() for a in self.authors.split(";")]
        return []

    @authors_list.setter
    def authors_list(self, value: list[str]) -> None:
        """设置作者列表"""
        self.authors = ";".join(value)

    @property
    def findings_list(self) -> list[str]:
        """获取关键发现列表"""
        if self.key_findings:
            try:
                return json.loads(self.key_findings)
            except json.JSONDecodeError:
                return []
        return []

    @findings_list.setter
    def findings_list(self, value: list[str]) -> None:
        """设置关键发现列表"""
        self.key_findings = json.dumps(value)

    @property
    def tags_list(self) -> list[str]:
        """获取标签列表"""
        if self.tags:
            return [t.strip() for t in self.tags.split(";")]
        return []

    @tags_list.setter
    def tags_list(self, value: list[str]) -> None:
        """设置标签列表"""
        self.tags = ";".join(value)


class DailyReport(Base):
    """每日报告表"""

    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(Text, unique=True, nullable=False)
    total_papers = Column(Integer)
    high_value_papers = Column(Integer)
    top_paper_ids = Column(Text)  # 存储为逗号分隔的ID
    report_content = Column(Text)  # JSON格式，包含深度分析内容
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # 关系
    clusters = relationship("PaperCluster", back_populates="report", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<DailyReport(date={self.report_date}, total={self.total_papers})>"

    @property
    def top_papers_list(self) -> list[int]:
        """获取顶级论文ID列表"""
        if self.top_paper_ids:
            return [int(i.strip()) for i in self.top_paper_ids.split(",") if i.strip()]
        return []

    @top_papers_list.setter
    def top_papers_list(self, value: list[int]) -> None:
        """设置顶级论文ID列表"""
        self.top_paper_ids = ",".join(map(str, value))

    @property
    def report_data(self) -> dict:
        """获取报告内容（解析JSON）"""
        if self.report_content:
            try:
                return json.loads(self.report_content)
            except json.JSONDecodeError:
                return {}
        return {}

    @report_data.setter
    def report_data(self, value: dict) -> None:
        """设置报告内容（序列化为JSON）"""
        self.report_content = json.dumps(value, ensure_ascii=False)


class PaperCluster(Base):
    """论文聚类表

    用于存储深度报告中的主题聚类信息
    """

    __tablename__ = "paper_clusters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey("daily_reports.id"), nullable=False)
    cluster_name = Column(Text, nullable=False)
    paper_ids = Column(Text, nullable=False)  # 逗号分隔的ID
    cluster_summary = Column(Text)  # LLM生成的聚类摘要
    key_findings = Column(Text)  # JSON格式
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # 关系
    report = relationship("DailyReport", back_populates="clusters")

    def __repr__(self) -> str:
        return (
            f"<PaperCluster(id={self.id}, name='{self.cluster_name}', report_id={self.report_id})>"
        )

    @property
    def paper_ids_list(self) -> list[int]:
        """获取论文ID列表"""
        if self.paper_ids:
            return [int(i.strip()) for i in self.paper_ids.split(",") if i.strip()]
        return []

    @paper_ids_list.setter
    def paper_ids_list(self, value: list[int]) -> None:
        """设置论文ID列表"""
        self.paper_ids = ",".join(map(str, value))

    @property
    def findings_list(self) -> list[str]:
        """获取关键发现列表"""
        if self.key_findings:
            try:
                return json.loads(self.key_findings)
            except json.JSONDecodeError:
                return []
        return []

    @findings_list.setter
    def findings_list(self, value: list[str]) -> None:
        """设置关键发现列表"""
        self.key_findings = json.dumps(value, ensure_ascii=False)


class Feedback(Base):
    """反馈表"""

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    rating = Column(Integer)  # 1-5 分
    is_helpful = Column(Boolean)
    comment = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # 关系
    paper = relationship("Paper", backref="feedbacks")

    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),)

    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, paper_id={self.paper_id}, rating={self.rating})>"


class RSSSource(Base):
    """RSS源配置表"""

    __tablename__ = "rss_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    url = Column(Text)
    source_type = Column(Text)  # 'rss' or 'api'
    priority = Column(Integer)
    enabled = Column(Boolean, default=True)
    last_fetch = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        return f"<RSSSource(id={self.id}, name='{self.name}', enabled={self.enabled})>"


class CollectionLog(Base):
    """数据采集日志表"""

    __tablename__ = "collection_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(Text, nullable=False)  # 'running', 'success', 'failed'
    total_papers = Column(Integer, default=0)
    new_papers = Column(Integer, default=0)
    sources = Column(Text)  # 逗号分隔的数据源列表
    error_message = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        return f"<CollectionLog(id={self.id}, status='{self.status}', total={self.total_papers})>"
