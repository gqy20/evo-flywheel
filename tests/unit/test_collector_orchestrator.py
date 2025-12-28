"""采集编排器单元测试"""

from datetime import datetime
from unittest import mock

from evo_flywheel.collectors.orchestrator import (
    collect_from_all_sources,
    collect_from_biorxiv,
    collect_from_rss_sources,
)


class TestCollectFromBiorxiv:
    """bioRxiv 采集测试"""

    def test_collect_from_biorxiv_success(self, monkeypatch):
        """测试成功从 bioRxiv 采集"""
        # Arrange
        mock_papers = [
            {"title": "Paper 1", "doi": "10.1101/2024.12.28.111111"},
            {"title": "Paper 2", "doi": "10.1101/2024.12.28.222222"},
        ]

        def mock_fetch(start, end, category):
            return mock_papers

        monkeypatch.setattr("evo_flywheel.collectors.orchestrator.fetch_biorxiv_papers", mock_fetch)

        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 31)

        # Act
        results = collect_from_biorxiv(start_date, end_date)

        # Assert
        assert len(results) == 2
        assert results[0]["title"] == "Paper 1"

    def test_collect_from_biorxiv_with_dedup(self, monkeypatch):
        """测试 bioRxiv 采集去重"""
        # Arrange
        mock_papers = [
            {"title": "Paper 1", "doi": "10.1101/2024.12.28.111111"},
            {"title": "Paper 2", "doi": "10.1101/2024.12.28.222222"},
            {"title": "Paper 1", "doi": "10.1101/2024.12.28.111111"},  # 重复
        ]

        def mock_fetch(start, end, category):
            return mock_papers

        monkeypatch.setattr("evo_flywheel.collectors.orchestrator.fetch_biorxiv_papers", mock_fetch)

        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 31)

        # Act
        results = collect_from_biorxiv(start_date, end_date)

        # Assert
        assert len(results) == 2  # 去重后只有2篇


class TestCollectFromRSSSources:
    """RSS 源采集测试"""

    def test_collect_from_rss_sources_success(self, monkeypatch):
        """测试成功从 RSS 源采集"""
        # Arrange
        sources = [
            {"name": "Source A", "url": "https://example.com/a.rss"},
            {"name": "Source B", "url": "https://example.com/b.rss"},
        ]

        # Mock RSS fetch results - 使用字典模拟 feedparser.Entry
        def mock_fetch_rss(url):
            mock_feed = mock.Mock()
            mock_feed.entries = [
                {"title": f"Paper from {url}", "link": f"https://example.com/{url}"}
            ]
            return mock_feed

        monkeypatch.setattr("evo_flywheel.collectors.orchestrator.fetch_rss_feed", mock_fetch_rss)

        # Act
        results = collect_from_rss_sources(sources)

        # Assert
        assert len(results) == 2

    def test_collect_from_rss_sources_empty_list(self):
        """测试空源列表"""
        # Arrange
        sources = []

        # Act
        results = collect_from_rss_sources(sources)

        # Assert
        assert results == []

    def test_collect_from_rss_sources_with_failure(self, monkeypatch):
        """测试部分源失败"""
        # Arrange
        sources = [
            {"name": "Good Source", "url": "https://example.com/good.rss"},
            {"name": "Bad Source", "url": "https://example.com/bad.rss"},
        ]

        call_count = {"count": 0}

        def mock_fetch_rss(url):
            call_count["count"] += 1
            if "bad" in url:
                raise Exception("Network error")
            mock_feed = mock.Mock()
            mock_feed.entries = [{"title": "Good Paper", "link": "https://example.com/good"}]
            return mock_feed

        monkeypatch.setattr("evo_flywheel.collectors.orchestrator.fetch_rss_feed", mock_fetch_rss)

        # Act
        results = collect_from_rss_sources(sources)

        # Assert
        # 应该跳过失败的源，继续处理其他源
        assert len(results) == 1
        assert results[0]["title"] == "Good Paper"


class TestCollectFromAllSources:
    """全源采集测试"""

    def test_collect_from_all_sources(self, monkeypatch):
        """测试从所有源采集"""

        # Arrange
        # Mock bioRxiv
        def mock_biorxiv(start, end, category):
            return [{"title": "BioRxiv Paper", "doi": "10.1101/2024.12.28.999999"}]

        monkeypatch.setattr(
            "evo_flywheel.collectors.orchestrator.fetch_biorxiv_papers", mock_biorxiv
        )

        # Mock RSS sources
        def mock_collect_rss(sources):
            return [{"title": "RSS Paper", "doi": "10.1234/rss.001"}]

        monkeypatch.setattr(
            "evo_flywheel.collectors.orchestrator.collect_from_rss_sources", mock_collect_rss
        )

        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 31)

        # Act
        results = collect_from_all_sources(start_date, end_date)

        # Assert
        assert len(results) == 2

    def test_collect_from_all_sources_dedup_across_sources(self, monkeypatch):
        """测试跨源去重"""

        # Arrange
        # Mock bioRxiv
        def mock_biorxiv(start, end, category):
            return [
                {"title": "Shared Paper", "doi": "10.1101/2024.12.28.123456"},
                {"title": "BioRxiv Only", "doi": "10.1101/2024.12.28.111111"},
            ]

        monkeypatch.setattr(
            "evo_flywheel.collectors.orchestrator.fetch_biorxiv_papers", mock_biorxiv
        )

        # Mock RSS sources (包含相同 DOI 的论文)
        def mock_collect_rss(sources):
            return [
                {"title": "Shared Paper", "doi": "10.1101/2024.12.28.123456"},
                {"title": "RSS Only", "doi": "10.1234/rss.001"},
            ]

        monkeypatch.setattr(
            "evo_flywheel.collectors.orchestrator.collect_from_rss_sources", mock_collect_rss
        )

        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 31)

        # Act
        results = collect_from_all_sources(start_date, end_date)

        # Assert
        # 应该有3篇论文 (BioRxiv Only + RSS Only + Shared Paper)
        assert len(results) == 3
        dois = [p.get("doi") for p in results]
        assert "10.1101/2024.12.28.111111" in dois
        assert "10.1234/rss.001" in dois
        assert "10.1101/2024.12.28.123456" in dois
