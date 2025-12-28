"""RSS 采集器单元测试"""

from unittest import mock

import feedparser
import pytest
from evo_flywheel.collectors.rss import (
    fetch_rss_feed,
    parse_entry,
    parse_rss_entries,
)


class TestFetchRSSFeed:
    """RSS feed 获取测试"""

    def test_fetch_rss_feed_with_valid_url(self, monkeypatch):
        """测试获取有效的 RSS feed"""
        # Arrange
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.content = (
            b"<rss><channel><item><title>Test Paper</title></item></channel></rss>"
        )

        def mock_get(url, timeout):
            return mock_response

        monkeypatch.setattr("requests.get", mock_get)

        # Act
        result = fetch_rss_feed("https://example.com/feed")

        # Assert
        assert result is not None
        assert result.feed is not None

    def test_fetch_rss_feed_with_invalid_url(self, monkeypatch):
        """测试获取无效的 RSS feed"""

        # Arrange
        def mock_get(url, timeout):
            raise Exception("Network error")

        monkeypatch.setattr("requests.get", mock_get)

        # Act & Assert
        with pytest.raises(Exception, match="Network error"):
            fetch_rss_feed("https://invalid.com/feed")

    def test_fetch_rss_feed_with_timeout(self, monkeypatch):
        """测试 RSS feed 获取超时"""

        # Arrange
        def mock_get(url, timeout):
            raise TimeoutError("Request timeout")

        monkeypatch.setattr("requests.get", mock_get)

        # Act & Assert
        with pytest.raises(TimeoutError):
            fetch_rss_feed("https://example.com/feed")


class TestParseEntry:
    """单个 RSS 条目解析测试"""

    def test_parse_entry_with_complete_data(self):
        """测试解析完整数据的条目"""
        # Arrange
        entry = feedparser.FeedParserDict(
            {
                "title": "Evolution of gene regulation in Drosophila",
                "authors": [{"name": "Smith, J."}, {"name": "Doe, A."}],
                "summary": "This study investigates...",
                "link": "https://example.com/paper/123",
                "published": "Mon, 01 Jan 2024 00:00:00 GMT",
                "dc_identifier": "doi:10.1101/2024.01.01.123456",
            }
        )

        # Act
        result = parse_entry(entry, source="test_source")

        # Assert
        assert result["title"] == "Evolution of gene regulation in Drosophila"
        assert result["authors"] == ["Smith, J.", "Doe, A."]
        assert result["abstract"] == "This study investigates..."
        assert result["url"] == "https://example.com/paper/123"
        assert result["doi"] == "10.1101/2024.01.01.123456"
        assert result["source"] == "test_source"

    def test_parse_entry_with_minimal_data(self):
        """测试解析最小数据的条目"""
        # Arrange
        entry = feedparser.FeedParserDict(
            {
                "title": "Minimal Paper",
                "link": "https://example.com/paper/456",
            }
        )

        # Act
        result = parse_entry(entry, source="test_source")

        # Assert
        assert result["title"] == "Minimal Paper"
        assert result["url"] == "https://example.com/paper/456"
        assert result["source"] == "test_source"
        assert result["authors"] == []
        assert result["abstract"] is None
        assert result["doi"] is None

    def test_parse_entry_extract_doi_from_link(self):
        """测试从链接中提取 DOI"""
        # Arrange
        entry = feedparser.FeedParserDict(
            {
                "title": "Paper with DOI in link",
                "link": "https://doi.org/10.1038/s41586-024-12345-6",
            }
        )

        # Act
        result = parse_entry(entry, source="test_source")

        # Assert
        assert result["doi"] == "10.1038/s41586-024-12345-6"

    def test_parse_entry_extract_doi_from_description(self):
        """测试从描述中提取 DOI"""
        # Arrange
        entry = feedparser.FeedParserDict(
            {
                "title": "Paper with DOI in description",
                "link": "https://example.com/paper",
                "description": "Full text available at: doi:10.1101/2024.12.28.123456",
            }
        )

        # Act
        result = parse_entry(entry, source="test_source")

        # Assert
        assert result["doi"] == "10.1101/2024.12.28.123456"

    def test_parse_entry_with_multiple_authors_string(self):
        """测试解析字符串格式的多作者"""
        # Arrange
        entry = feedparser.FeedParserDict(
            {
                "title": "Multi-author Paper",
                "author": "Smith, J., Doe, A., Johnson, B.",
                "link": "https://example.com/paper",
            }
        )

        # Act
        result = parse_entry(entry, source="test_source")

        # Assert
        assert result["authors"] == ["Smith, J.", "Doe, A.", "Johnson, B."]

    def test_parse_entry_clean_html_from_abstract(self):
        """测试清理摘要中的 HTML 标签"""
        # Arrange
        entry = feedparser.FeedParserDict(
            {
                "title": "Paper with HTML abstract",
                "summary": "<p>This is <strong>important</strong> research.</p>",
                "link": "https://example.com/paper",
            }
        )

        # Act
        result = parse_entry(entry, source="test_source")

        # Assert
        assert "<p>" not in result["abstract"]
        assert "<strong>" not in result["abstract"]
        assert "important" in result["abstract"]


class TestParseRSSEntries:
    """批量 RSS 条目解析测试"""

    def test_parse_rss_entries_with_multiple_entries(self):
        """测试解析多个 RSS 条目"""
        # Arrange
        entries = [
            feedparser.FeedParserDict(
                {
                    "title": "Paper 1",
                    "link": "https://example.com/paper1",
                }
            ),
            feedparser.FeedParserDict(
                {
                    "title": "Paper 2",
                    "link": "https://example.com/paper2",
                }
            ),
            feedparser.FeedParserDict(
                {
                    "title": "Paper 3",
                    "link": "https://example.com/paper3",
                }
            ),
        ]

        # Act
        results = parse_rss_entries(entries, source="test_source")

        # Assert
        assert len(results) == 3
        assert results[0]["title"] == "Paper 1"
        assert results[1]["title"] == "Paper 2"
        assert results[2]["title"] == "Paper 3"

    def test_parse_rss_entries_with_empty_list(self):
        """测试解析空列表"""
        # Arrange
        entries = []

        # Act
        results = parse_rss_entries(entries, source="test_source")

        # Assert
        assert len(results) == 0
        assert results == []

    def test_parse_rss_entries_filters_invalid_entries(self):
        """测试过滤无效条目"""
        # Arrange
        entries = [
            feedparser.FeedParserDict(
                {
                    "title": "Valid Paper",
                    "link": "https://example.com/paper1",
                }
            ),
            feedparser.FeedParserDict(
                {
                    "link": "https://example.com/paper2",  # Missing title
                }
            ),
            feedparser.FeedParserDict(
                {
                    "title": "Another Valid Paper",
                    "link": "https://example.com/paper3",
                }
            ),
        ]

        # Act
        results = parse_rss_entries(entries, source="test_source")

        # Assert
        assert len(results) == 2
        assert all("title" in r for r in results)
