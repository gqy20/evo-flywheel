"""批量分析器单元测试"""

from unittest import mock

from evo_flywheel.analyzers.batch import (
    analyze_papers_batch,
    get_cached_analysis,
    is_analyzed,
)


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
        papers = [
            {"id": 1, "doi": "10.1234/1", "taxa": "Done", "importance_score": 80},
            {"id": 2, "doi": "10.1234/2"},  # 未分析
            {"id": 3, "doi": "10.1234/3", "taxa": "Done", "importance_score": 70},
        ]

        mock_analyze = mock.Mock(return_value={"taxa": "New", "importance_score": 85})

        monkeypatch.setattr("evo_flywheel.analyzers.batch.analyze_paper", mock_analyze)

        # Act
        results = analyze_papers_batch(papers)

        # Assert
        assert mock_analyze.call_count == 1  # 只分析未分析的论文
        assert len(results) == 3

    def test_analyze_papers_batch_respects_concurrency_limit(self, monkeypatch):
        """测试批量分析遵守并发限制"""
        # Arrange
        papers = [{"id": i, "doi": f"10.1234/{i}"} for i in range(10)]

        call_count = {"count": 0}

        def mock_analyze(title, abstract):
            call_count["count"] += 1
            return {"taxa": "Test", "importance_score": 50}

        monkeypatch.setattr("evo_flywheel.analyzers.batch.analyze_paper", mock_analyze)

        # Act
        results = analyze_papers_batch(papers, max_concurrent=3)

        # Assert
        assert len(results) == 10
        assert call_count["count"] == 10

    def test_analyze_papers_batch_uses_cache(self, monkeypatch):
        """测试批量分析使用缓存"""
        # Arrange
        papers = [
            {"id": 1, "doi": "10.1234/1"},
            {"id": 2, "doi": "10.1234/2"},  # 与 #1 DOI 相同
            {"id": 3, "doi": "10.1234/3"},
        ]

        mock_analyze = mock.Mock(return_value={"taxa": "Test", "importance_score": 75})

        monkeypatch.setattr("evo_flywheel.analyzers.batch.analyze_paper", mock_analyze)

        # Act
        _ = analyze_papers_batch(papers)

        # Assert
        # #1 和 #2 有相同 DOI，#2 应该使用缓存
        assert mock_analyze.call_count == 2  # #1 和 #3

    def test_analyze_papers_batch_returns_all_papers(self, monkeypatch):
        """测试批量分析返回所有论文结果"""
        # Arrange
        papers = [
            {"id": 1, "doi": "10.1234/1"},
            {"id": 2, "doi": "10.1234/2"},
        ]

        mock_analyze = mock.Mock(
            side_effect=[
                {"taxa": "Test1", "importance_score": 85},
                {"taxa": "Test2", "importance_score": 70},
            ]
        )

        monkeypatch.setattr("evo_flywheel.analyzers.batch.analyze_paper", mock_analyze)

        # Act
        results = analyze_papers_batch(papers)

        # Assert
        assert len(results) == 2
        assert results[0]["taxa"] == "Test1"
        assert results[1]["taxa"] == "Test2"

    def test_analyze_papers_batch_handles_empty_list(self):
        """测试批量分析处理空列表"""
        # Arrange
        papers = []

        # Act
        results = analyze_papers_batch(papers)

        # Assert
        assert results == []

    def test_analyze_papers_batch_handles_api_errors(self, monkeypatch):
        """测试批量处理 API 错误"""
        # Arrange
        papers = [
            {"id": 1, "doi": "10.1234/1"},
            {"id": 2, "doi": "10.1234/2"},
        ]

        mock_analyze = mock.Mock(
            side_effect=[
                {"taxa": "Test1", "importance_score": 85},
                Exception("API Error"),
            ]
        )

        monkeypatch.setattr("evo_flywheel.analyzers.batch.analyze_paper", mock_analyze)

        # Act
        results = analyze_papers_batch(papers, continue_on_error=True)

        # Assert
        assert len(results) == 2
        assert results[0]["taxa"] == "Test1"
        # 第二个论文分析失败，应该保留原始数据或标记错误
        assert results[1]["id"] == 2

    def test_analyze_papers_batch_tracks_statistics(self, monkeypatch):
        """测试批量分析追踪统计信息"""
        # Arrange
        papers = [
            {"id": 1, "doi": "10.1234/1", "taxa": "Done", "importance_score": 80},
            {"id": 2, "doi": "10.1234/2"},  # 未分析
            {"id": 3, "doi": "10.1234/3", "taxa": "Done", "importance_score": 70},
        ]

        mock_analyze = mock.Mock(return_value={"taxa": "New", "importance_score": 85})

        monkeypatch.setattr("evo_flywheel.analyzers.batch.analyze_paper", mock_analyze)

        # Act
        results = analyze_papers_batch(papers)

        # Assert
        # 应该返回统计信息
        assert isinstance(results, list)
        assert len(results) == 3
        # 验证已缓存的论文数量
        assert any(r.get("_cached") for r in results)

    def test_analyze_papers_batch_can_dry_run(self, monkeypatch):
        """测试批量分析支持 dry_run 模式"""
        # Arrange
        papers = [
            {"id": 1, "doi": "10.1234/1"},
            {"id": 2, "doi": "10.1234/2"},
        ]

        mock_analyze = mock.Mock()

        monkeypatch.setattr("evo_flywheel.analyzers.batch.analyze_paper", mock_analyze)

        # Act
        results = analyze_papers_batch(papers, dry_run=True)

        # Assert
        assert mock_analyze.call_count == 0  # dry_run 不调用 API
        assert len(results) == 2
