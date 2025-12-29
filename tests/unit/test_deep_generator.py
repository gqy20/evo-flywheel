"""深度报告生成器单元测试

测试 deep_generator 模块的核心功能
"""

from datetime import UTC, date, datetime
from unittest import mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from evo_flywheel.db.models import Base, Paper


@pytest.fixture
def db_session_with_papers(temp_db_path):
    """创建包含论文数据的测试会话"""
    engine = create_engine(f"sqlite:///{temp_db_path}")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # 创建测试论文
        today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

        papers = [
            Paper(
                title=f"Test Paper {i}",
                authors=f"Author {i}",
                abstract=f"Abstract {i}",
                taxa="Drosophila" if i % 2 == 0 else "Homo sapiens",
                evolutionary_scale="Population",
                research_method="Experimental Evolution",
                key_findings='["finding1", "finding2"]',
                evolutionary_mechanism="Natural Selection",
                importance_score=80 + i,
                innovation_summary=f"Innovation {i}",
                journal="bioRxiv",
                created_at=today,
            )
            for i in range(1, 6)
        ]

        session.add_all(papers)
        session.commit()

        yield session


class TestGenerateDeepReport:
    """深度报告生成功能测试"""

    def test_generate_deep_report_creates_report_record(self, db_session_with_papers):
        """测试生成报告创建数据库记录"""
        # Arrange
        from evo_flywheel.reporters.deep_generator import generate_deep_report

        target_date = date.today()

        # Act
        report = generate_deep_report(target_date, db_session_with_papers)

        # Assert
        assert report is not None
        assert report.id is not None
        assert report.report_date == target_date.isoformat()
        assert report.total_papers == 5
        assert report.high_value_papers == 5  # 所有论文都 >= 80

    def test_generate_deep_report_raises_error_when_no_papers(self, db_session_with_papers):
        """测试当天没有论文时抛出错误"""
        # Arrange
        from evo_flywheel.reporters.deep_generator import generate_deep_report

        # 使用一个没有论文的日期
        empty_date = date(2020, 1, 1)

        # Act & Assert
        with pytest.raises(ValueError, match="没有已分析的论文"):
            generate_deep_report(empty_date, db_session_with_papers)

    def test_generate_deep_report_saves_llm_content(self, db_session_with_papers):
        """测试报告保存 LLM 生成的内容"""
        # Arrange
        from evo_flywheel.reporters.deep_generator import generate_deep_report

        target_date = date.today()

        # Act
        report = generate_deep_report(target_date, db_session_with_papers)

        # Assert
        assert report.report_content is not None
        report_data = report.report_data
        assert "research_summary" in report_data
        assert "hot_topics" in report_data
        assert "recommended_papers" in report_data

    def test_generate_deep_report_creates_clusters(self, db_session_with_papers):
        """测试报告创建聚类记录"""
        # Arrange
        from evo_flywheel.reporters.deep_generator import generate_deep_report

        target_date = date.today()

        # Act
        report = generate_deep_report(target_date, db_session_with_papers)

        # Assert
        assert len(report.clusters) > 0

        # 验证聚类属性
        cluster = report.clusters[0]
        assert cluster.cluster_name is not None
        assert len(cluster.paper_ids_list) > 0
        assert cluster.report_id == report.id

    def test_generate_deep_report_filters_analyzed_papers_only(self, db_session_with_papers):
        """测试只处理已分析的论文"""
        # Arrange
        from evo_flywheel.reporters.deep_generator import generate_deep_report

        # 添加一篇未分析的论文
        unanalyzed = Paper(
            title="Unanalyzed Paper",
            authors="Test",
            abstract="No analysis",
            created_at=datetime.now(UTC),
        )
        db_session_with_papers.add(unanalyzed)
        db_session_with_papers.commit()

        target_date = date.today()

        # Act
        report = generate_deep_report(target_date, db_session_with_papers)

        # Assert - 只计算已分析的论文
        assert report.total_papers == 5  # 不包含未分析的

    def test_generate_deep_report_handles_llm_failure_gracefully(self, db_session_with_papers):
        """测试 LLM 失败时的降级处理"""
        # Arrange
        from evo_flywheel.reporters.deep_generator import generate_deep_report

        target_date = date.today()

        # Mock LLM 失败
        with mock.patch(
            "evo_flywheel.reporters.deep_generator._generate_llm_analysis",
            side_effect=Exception("LLM API Error"),
        ):
            # Act & Assert - 应该返回基础结构而不是抛出异常
            report = generate_deep_report(target_date, db_session_with_papers)
            assert report is not None
            assert report.total_papers == 5


class TestPaperToDict:
    """论文转换功能测试"""

    def test_paper_to_dict_converts_all_fields(self):
        """测试论文转换为字典包含所有字段"""
        # Arrange
        from evo_flywheel.reporters.deep_generator import _paper_to_dict

        paper = Paper(
            id=123,
            title="Test Paper",
            authors="Author1;Author2",
            abstract="Test Abstract",
            taxa="Drosophila",
            evolutionary_scale="Population",
            research_method="Experimental",
            key_findings='["f1", "f2"]',
            evolutionary_mechanism="Selection",
            importance_score=85,
            innovation_summary="Innovative",
            journal="Nature",
            doi="10.1234/test",
        )

        # Act
        result = _paper_to_dict(paper)

        # Assert
        assert result["id"] == 123
        assert result["title"] == "Test Paper"
        assert result["authors"] == ["Author1", "Author2"]
        assert result["taxa"] == "Drosophila"
        assert result["importance_score"] == 85
        assert result["key_findings"] == ["f1", "f2"]


class TestClusterPapers:
    """论文聚类功能测试"""

    def test_cluster_papers_groups_by_taxa_and_method(self):
        """测试按物种和方法聚类"""
        # Arrange
        from evo_flywheel.reporters.deep_generator import _cluster_papers

        papers = [
            {"taxa": "Drosophila", "research_method": "Experimental", "id": 1},
            {"taxa": "Drosophila", "research_method": "Experimental", "id": 2},
            {"taxa": "Homo sapiens", "research_method": "Experimental", "id": 3},
            {"taxa": "Drosophila", "research_method": "Comparative", "id": 4},
        ]

        # Act
        clusters = _cluster_papers(papers)

        # Assert
        assert "Drosophila_Experimental" in clusters
        assert len(clusters["Drosophila_Experimental"]) == 2
        assert "Homo_sapiens_Experimental" in clusters
        assert "Drosophila_Comparative" in clusters

    def test_cluster_papers_handles_missing_fields(self):
        """测试处理缺失字段"""
        # Arrange
        from evo_flywheel.reporters.deep_generator import _cluster_papers

        papers = [
            {"taxa": "Drosophila", "id": 1},
            {"research_method": "Experimental", "id": 2},
            {"id": 3},
        ]

        # Act
        clusters = _cluster_papers(papers)

        # Assert - 应该使用 Unknown 作为默认值
        assert "Drosophila_Unknown" in clusters
        assert "Unknown_Experimental" in clusters
        assert "Unknown_Unknown" in clusters


class TestCalculateStats:
    """统计计算功能测试"""

    def test_calculate_stats_returns_correct_counts(self, db_session_with_papers):
        """测试统计计算正确"""
        # Arrange
        from evo_flywheel.reporters.deep_generator import _calculate_stats

        from evo_flywheel.db.models import Paper

        papers = db_session_with_papers.query(Paper).all()
        clusters = {"Drosophila_Experimental": [1, 2], "Homo_sapiens_Experimental": [3, 4, 5]}

        # Act
        stats = _calculate_stats(papers, clusters)

        # Assert
        assert stats["total"] == 5
        assert stats["high_value"] == 5  # 都 >= 80
        assert stats["cluster_count"] == 2

    def test_calculate_stats_counts_unique_taxa_and_methods(self, db_session_with_papers):
        """测试统计唯一的物种和方法数量"""
        # Arrange
        from evo_flywheel.reporters.deep_generator import _calculate_stats

        from evo_flywheel.db.models import Paper

        papers = db_session_with_papers.query(Paper).all()
        clusters = {}

        # Act
        stats = _calculate_stats(papers, clusters)

        # Assert - 2个物种(Drosophila, Homo sapiens)，1个方法
        assert stats["taxa_count"] == 2
        assert stats["methods_count"] == 1


class TestGenerateLLMAnalysis:
    """LLM 分析生成测试"""

    def test_generate_llm_analysis_returns_structure(self, db_session_with_papers):
        """测试 LLM 分析返回正确结构"""
        # Arrange
        from evo_flywheel.reporters.deep_generator import _generate_llm_analysis

        from evo_flywheel.db.models import Paper

        papers = db_session_with_papers.query(Paper).limit(3).all()
        paper_dicts = [_paper_to_dict(p) for p in papers]
        clusters = {"Drosophila_Experimental": paper_dicts[:2]}
        stats = {"total": 3, "high_value": 3}

        # Act
        result = _generate_llm_analysis(paper_dicts, clusters, stats)

        # Assert
        assert "research_summary" in result
        assert "hot_topics" in result
        assert "trend_analysis" in result
        assert "recommended_papers" in result
        assert "top_paper_ids" in result

    def test_generate_llm_analysis_includes_top_paper_ids(self, db_session_with_papers):
        """测试 LLM 分析包含顶级论文ID"""
        # Arrange
        from evo_flywheel.reporters.deep_generator import _generate_llm_analysis

        from evo_flywheel.db.models import Paper

        papers = db_session_with_papers.query(Paper).all()
        paper_dicts = [_paper_to_dict(p) for p in papers]

        # Act
        result = _generate_llm_analysis(paper_dicts, {}, {"total": 5, "high_value": 5})

        # Assert
        assert "top_paper_ids" in result
        assert len(result["top_paper_ids"]) <= 10


# Helper function for tests
def _paper_to_dict(paper: Paper) -> dict:
    """简化版的论文转换（测试用）"""
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
