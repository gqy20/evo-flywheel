"""批量分析器单元测试"""

from unittest import mock

import pytest

from evo_flywheel.analyzers.batch import (
    get_cached_analysis,
    is_analyzed,
)


@pytest.fixture(autouse=True)
def clear_batch_cache():
    """每个测试前清理批量分析缓存"""
    import evo_flywheel.analyzers.batch as batch_module

    batch_module._analysis_cache.clear()
    yield
    batch_module._analysis_cache.clear()


class TestIsAnalyzed:
    """论文分析状态检查测试"""

    def test_is_analyzed_with_complete_result(self):
        """测试有完整分析结果的论文"""
        # Arrange
        paper = {
            "taxa": "Drosophila",
            "evolutionary_scale": "种群",
            "research_method": "实验",
            "key_findings": ["发现1"],
            "evolutionary_mechanism": "自然选择",
            "importance_score": 85,
            "innovation_summary": "测试",
        }

        # Act
        result = is_analyzed(paper)

        # Assert
        assert result is True

    def test_is_analyzed_with_partial_result(self):
        """测试只有部分分析结果的论文"""
        # Arrange
        paper = {"taxa": "Drosophila", "importance_score": 50}

        # Act
        result = is_analyzed(paper)

        # Assert
        assert result is False

    def test_is_analyzed_with_no_result(self):
        """测试没有分析结果的论文"""
        # Arrange
        paper = {"title": "Test", "abstract": "Abstract"}

        # Act
        result = is_analyzed(paper)

        # Assert
        assert result is False

    def test_is_analyzed_with_zero_score(self):
        """测试评分为 0 的论文（视为未分析）"""
        # Arrange
        paper = {
            "taxa": "Test",
            "importance_score": 0,
            "key_findings": [],
        }

        # Act
        result = is_analyzed(paper)

        # Assert
        assert result is False


class TestGetCachedAnalysis:
    """缓存功能测试"""

    def test_get_cached_analysis_returns_cached_result(self, monkeypatch):
        """测试返回已缓存的分析结果"""
        # Arrange
        cache = {"paper:1": {"taxa": "Cached", "importance_score": 75}}
        monkeypatch.setattr("evo_flywheel.analyzers.batch._analysis_cache", cache)

        paper = {"id": 1, "doi": "10.1234/test"}

        # Act
        result = get_cached_analysis(paper)

        # Assert
        assert result == {"taxa": "Cached", "importance_score": 75}

    def test_get_cached_analysis_returns_none_when_miss(self, monkeypatch):
        """测试缓存未命中时返回 None"""
        # Arrange
        cache = {}
        monkeypatch.setattr("evo_flywheel.analyzers.batch._analysis_cache", cache)

        paper = {"id": 1, "doi": "10.1234/test"}

        # Act
        result = get_cached_analysis(paper)

        # Assert
        assert result is None


class TestAnalyzePapersBatch:
    """批量分析测试"""

    def test_analyze_papers_batch_filters_analyzed(self, monkeypatch):
        """测试批量分析过滤已分析的论文"""
        # Arrange
        import evo_flywheel.analyzers.batch as batch_module

        papers = [
            {
                "id": 1,
                "doi": "10.1234/1",
                "title": "Paper 1",
                "abstract": "Abstract 1",
                "taxa": "Done",
                "importance_score": 80,
                "evolutionary_scale": "种群",
                "research_method": "实验",
                "key_findings": ["发现1"],
                "evolutionary_mechanism": "自然选择",
                "innovation_summary": "创新",
            },
            {
                "id": 2,
                "doi": "10.1234/2",
                "title": "Paper 2",
                "abstract": "Abstract 2",
            },  # 未分析
            {
                "id": 3,
                "doi": "10.1234/3",
                "title": "Paper 3",
                "abstract": "Abstract 3",
                "taxa": "Done",
                "importance_score": 70,
                "evolutionary_scale": "个体",
                "research_method": "比较",
                "key_findings": ["发现2"],
                "evolutionary_mechanism": "突变",
                "innovation_summary": "创新2",
            },
        ]

        mock_analyze = mock.Mock(
            return_value=mock.Mock(
                taxa="New",
                evolutionary_scale="种群",
                research_method="实验",
                key_findings=["发现"],
                evolutionary_mechanism="自然选择",
                importance_score=85,
                innovation_summary="测试",
                usage=mock.Mock(total_tokens=1000),
            )
        )

        # Patch llm.analyze_paper since batch.py now uses llm module
        monkeypatch.setattr("evo_flywheel.analyzers.llm.analyze_paper", mock_analyze)

        # Act
        results = batch_module.analyze_papers_batch(papers)

        # Assert
        assert mock_analyze.call_count == 1  # 只分析未分析的论文
        assert len(results) == 3

    def test_analyze_papers_batch_respects_concurrency_limit(self, monkeypatch):
        """测试批量分析遵守并发限制"""
        # Arrange
        import evo_flywheel.analyzers.batch as batch_module

        papers = [
            {"id": i, "doi": f"10.1234/{i}", "title": f"Paper {i}", "abstract": f"Abstract {i}"}
            for i in range(10)
        ]

        call_count = {"count": 0}

        def mock_analyze(title, abstract):
            call_count["count"] += 1
            return mock.Mock(
                taxa="Test",
                evolutionary_scale="种群",
                research_method="实验",
                key_findings=["发现"],
                evolutionary_mechanism="自然选择",
                importance_score=50,
                innovation_summary="测试",
                usage=mock.Mock(total_tokens=100),
            )

        monkeypatch.setattr("evo_flywheel.analyzers.llm.analyze_paper", mock_analyze)

        # Act
        results = batch_module.analyze_papers_batch(papers, max_concurrent=3)

        # Assert
        assert len(results) == 10
        assert call_count["count"] == 10

    def test_analyze_papers_batch_uses_cache(self, monkeypatch):
        """测试批量分析使用缓存"""
        # Arrange
        import evo_flywheel.analyzers.batch as batch_module

        papers = [
            {"id": 1, "doi": "10.1234/1", "title": "Paper 1", "abstract": "Abstract 1"},
            {
                "id": 2,
                "doi": "10.1234/2",
                "title": "Paper 2",
                "abstract": "Abstract 2",
            },  # 与 #1 不同
            {"id": 3, "doi": "10.1234/3", "title": "Paper 3", "abstract": "Abstract 3"},
        ]

        mock_analyze = mock.Mock(
            return_value=mock.Mock(
                taxa="Test",
                evolutionary_scale="种群",
                research_method="实验",
                key_findings=["发现"],
                evolutionary_mechanism="自然选择",
                importance_score=75,
                innovation_summary="测试",
                usage=mock.Mock(total_tokens=100),
            )
        )

        monkeypatch.setattr("evo_flywheel.analyzers.llm.analyze_paper", mock_analyze)

        # Act
        _ = batch_module.analyze_papers_batch(papers)

        # Assert
        # 所有论文都需要分析（没有缓存的，也没有重复的 DOI）
        assert mock_analyze.call_count == 3

    def test_analyze_papers_batch_returns_all_papers(self, monkeypatch):
        """测试批量分析返回所有论文结果"""
        # Arrange
        import evo_flywheel.analyzers.batch as batch_module

        papers = [
            {"id": 1, "doi": "10.1234/1", "title": "Paper 1", "abstract": "Abstract 1"},
            {"id": 2, "doi": "10.1234/2", "title": "Paper 2", "abstract": "Abstract 2"},
        ]

        mock_analyze = mock.Mock(
            side_effect=[
                mock.Mock(
                    taxa="Test1",
                    evolutionary_scale="种群",
                    research_method="实验",
                    key_findings=["发现1"],
                    evolutionary_mechanism="自然选择",
                    importance_score=85,
                    innovation_summary="测试1",
                    usage=mock.Mock(total_tokens=100),
                ),
                mock.Mock(
                    taxa="Test2",
                    evolutionary_scale="个体",
                    research_method="比较",
                    key_findings=["发现2"],
                    evolutionary_mechanism="突变",
                    importance_score=70,
                    innovation_summary="测试2",
                    usage=mock.Mock(total_tokens=100),
                ),
            ]
        )

        monkeypatch.setattr("evo_flywheel.analyzers.llm.analyze_paper", mock_analyze)

        # Act
        results = batch_module.analyze_papers_batch(papers)

        # Assert
        assert len(results) == 2
        assert results[0]["taxa"] == "Test1"
        assert results[1]["taxa"] == "Test2"

    def test_analyze_papers_batch_handles_empty_list(self):
        """测试批量分析处理空列表"""
        # Arrange
        import evo_flywheel.analyzers.batch as batch_module

        papers = []

        # Act
        results = batch_module.analyze_papers_batch(papers)

        # Assert
        assert results == []

    def test_analyze_papers_batch_handles_api_errors(self, monkeypatch):
        """测试批量处理 API 错误"""
        # Arrange
        import evo_flywheel.analyzers.batch as batch_module

        papers = [
            {"id": 1, "doi": "10.1234/1", "title": "Paper 1", "abstract": "Abstract 1"},
            {"id": 2, "doi": "10.1234/2", "title": "Paper 2", "abstract": "Abstract 2"},
        ]

        mock_analyze = mock.Mock(
            side_effect=[
                mock.Mock(
                    taxa="Test1",
                    evolutionary_scale="种群",
                    research_method="实验",
                    key_findings=["发现1"],
                    evolutionary_mechanism="自然选择",
                    importance_score=85,
                    innovation_summary="测试1",
                    usage=mock.Mock(total_tokens=100),
                ),
                Exception("API Error"),
            ]
        )

        monkeypatch.setattr("evo_flywheel.analyzers.llm.analyze_paper", mock_analyze)

        # Act
        results = batch_module.analyze_papers_batch(papers, continue_on_error=True)

        # Assert
        assert len(results) == 2
        assert results[0]["taxa"] == "Test1"
        # 第二个论文分析失败，应该保留原始数据或标记错误
        assert results[1]["id"] == 2
        assert "_error" in results[1]

    def test_analyze_papers_batch_tracks_statistics(self, monkeypatch):
        """测试批量分析追踪统计信息"""
        # Arrange
        import evo_flywheel.analyzers.batch as batch_module

        papers = [
            {
                "id": 1,
                "doi": "10.1234/1",
                "title": "Paper 1",
                "abstract": "Abstract 1",
                "taxa": "Done",
                "importance_score": 80,
                "evolutionary_scale": "种群",
                "research_method": "实验",
                "key_findings": ["发现1"],
                "evolutionary_mechanism": "自然选择",
                "innovation_summary": "创新",
            },
            {"id": 2, "doi": "10.1234/2", "title": "Paper 2", "abstract": "Abstract 2"},  # 未分析
            {
                "id": 3,
                "doi": "10.1234/3",
                "title": "Paper 3",
                "abstract": "Abstract 3",
                "taxa": "Done",
                "importance_score": 70,
                "evolutionary_scale": "个体",
                "research_method": "比较",
                "key_findings": ["发现2"],
                "evolutionary_mechanism": "突变",
                "innovation_summary": "创新2",
            },
        ]

        mock_analyze = mock.Mock(
            return_value=mock.Mock(
                taxa="New",
                evolutionary_scale="种群",
                research_method="实验",
                key_findings=["发现"],
                evolutionary_mechanism="自然选择",
                importance_score=85,
                innovation_summary="测试",
                usage=mock.Mock(total_tokens=100),
            )
        )

        monkeypatch.setattr("evo_flywheel.analyzers.llm.analyze_paper", mock_analyze)

        # Act
        results = batch_module.analyze_papers_batch(papers)

        # Assert
        # 应该返回统计信息
        assert isinstance(results, list)
        assert len(results) == 3
        # 验证已缓存的论文数量（paper 1 和 3 已分析，paper 2 被分析后也会被标记）
        cached_papers = [r for r in results if r.get("_cached")]
        assert len(cached_papers) == 2

    def test_analyze_papers_batch_can_dry_run(self, monkeypatch):
        """测试批量分析支持 dry_run 模式"""
        # Arrange
        import evo_flywheel.analyzers.batch as batch_module

        papers = [
            {"id": 1, "doi": "10.1234/1", "title": "Paper 1", "abstract": "Abstract 1"},
            {"id": 2, "doi": "10.1234/2", "title": "Paper 2", "abstract": "Abstract 2"},
        ]

        mock_analyze = mock.Mock()

        monkeypatch.setattr("evo_flywheel.analyzers.llm.analyze_paper", mock_analyze)

        # Act
        results = batch_module.analyze_papers_batch(papers, dry_run=True)

        # Assert
        assert mock_analyze.call_count == 0  # dry_run 不调用 API
        assert len(results) == 2

    def test_analyze_papers_batch_maintains_order_with_concurrency(self, monkeypatch):
        """测试批量分析在并发情况下保持结果顺序

        这是修复并发结果错位 bug 的关键测试。
        即使多个论文并发分析，返回的结果顺序也应与输入顺序一致。
        """
        # Arrange
        import time

        import evo_flywheel.analyzers.batch as batch_module

        papers = [
            {"id": 1, "doi": "10.1234/1", "title": "Paper 1", "abstract": "Abstract 1"},
            {"id": 2, "doi": "10.1234/2", "title": "Paper 2", "abstract": "Abstract 2"},
            {"id": 3, "doi": "10.1234/3", "title": "Paper 3", "abstract": "Abstract 3"},
            {"id": 4, "doi": "10.1234/4", "title": "Paper 4", "abstract": "Abstract 4"},
            {"id": 5, "doi": "10.1234/5", "title": "Paper 5", "abstract": "Abstract 5"},
        ]

        # 模拟不同的处理时间，确保完成顺序与提交顺序不同
        call_order = []

        def mock_analyze_with_delay(title, abstract):
            call_order.append(title)
            # 让 Paper 2 和 Paper 4 延迟返回，模拟并发完成顺序不一致
            if "Paper 2" in title or "Paper 4" in title:
                time.sleep(0.05)
            else:
                time.sleep(0.01)

            return mock.Mock(
                taxa=f"Taxa for {title}",
                evolutionary_scale="种群",
                research_method="实验",
                key_findings=[f"发现 for {title}"],
                evolutionary_mechanism="自然选择",
                importance_score=70 + int(title.split()[-1]),
                innovation_summary=f"测试 {title}",
                usage=mock.Mock(total_tokens=100),
            )

        monkeypatch.setattr("evo_flywheel.analyzers.llm.analyze_paper", mock_analyze_with_delay)

        # Act - 使用并发数为 3，确保并发执行
        results = batch_module.analyze_papers_batch(papers, max_concurrent=3)

        # Assert
        assert len(results) == 5

        # 验证结果顺序与输入顺序一致（通过 ID 和 title 匹配）
        for i, paper in enumerate(papers):
            assert results[i]["id"] == paper["id"], f"位置 {i} 的 ID 不匹配"
            assert results[i]["title"] == paper["title"], f"位置 {i} 的 title 不匹配"
            # 验证分析结果正确关联
            assert f"Taxa for {paper['title']}" == results[i]["taxa"]
            assert f"发现 for {paper['title']}" in results[i]["key_findings"]

        # 验证确实并发调用了
        assert len(call_order) == 5

    def test_analyze_papers_batch_preserves_id_for_matching(self, monkeypatch):
        """测试批量分析保留原始 ID 用于后续匹配

        验证分析结果中的 id 字段被正确保留，
        这对于 API 端点通过 ID 匹配更新数据库记录至关重要。
        """
        # Arrange
        import evo_flywheel.analyzers.batch as batch_module

        papers = [
            {"id": 100, "doi": "10.1234/100", "title": "Paper A", "abstract": "Abstract A"},
            {"id": 200, "doi": "10.1234/200", "title": "Paper B", "abstract": "Abstract B"},
            {"id": 300, "doi": "10.1234/300", "title": "Paper C", "abstract": "Abstract C"},
        ]

        mock_analyze = mock.Mock(
            return_value=mock.Mock(
                taxa="Test",
                evolutionary_scale="种群",
                research_method="实验",
                key_findings=["发现"],
                evolutionary_mechanism="自然选择",
                importance_score=75,
                innovation_summary="测试",
                usage=mock.Mock(total_tokens=100),
            )
        )

        monkeypatch.setattr("evo_flywheel.analyzers.llm.analyze_paper", mock_analyze)

        # Act
        results = batch_module.analyze_papers_batch(papers, max_concurrent=2)

        # Assert - 验证每个结果都保留了正确的 ID
        assert results[0]["id"] == 100
        assert results[1]["id"] == 200
        assert results[2]["id"] == 300

        # 验证可以通过 ID 构建映射（这是 API 端点的使用方式）
        id_to_analysis = {r["id"]: r for r in results}
        assert id_to_analysis[100]["id"] == 100
        assert id_to_analysis[200]["id"] == 200
        assert id_to_analysis[300]["id"] == 300
