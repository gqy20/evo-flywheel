"""bioRxiv API 采集器单元测试"""

from datetime import datetime
from unittest import mock

import pytest
from evo_flywheel.collectors.biorxiv import (
    build_api_url,
    fetch_biorxiv_papers,
    parse_biorxiv_date,
    parse_biorxiv_paper,
)


class TestBuildAPIUrl:
    """API URL 构建测试"""

    def test_build_api_url_with_date_range(self):
        """测试构建指定日期范围的 URL"""
        # Arrange
        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 31)

        # Act
        url = build_api_url(start_date, end_date)

        # Assert
        assert "https://api.biorxiv.org/details/biorxiv/" in url
        assert "2024-12-01" in url
        assert "2024-12-31" in url
        assert "category=evolutionary_biology" in url

    def test_build_api_url_with_category(self):
        """测试构建指定分类的 URL"""
        # Arrange
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        category = "microbiology"

        # Act
        url = build_api_url(start_date, end_date, category)

        # Assert
        assert "category=microbiology" in url

    def test_build_api_url_default_category(self):
        """测试默认分类为 evolutionary_biology"""
        # Arrange
        start_date = datetime(2024, 6, 1)
        end_date = datetime(2024, 6, 30)

        # Act
        url = build_api_url(start_date, end_date)

        # Assert
        assert "category=evolutionary_biology" in url


class TestParseBiorxivDate:
    """bioRxiv 日期解析测试"""

    def test_parse_biorxiv_date_valid_format(self):
        """测试解析有效日期格式"""
        # Arrange
        date_str = "2024-12-28"

        # Act
        result = parse_biorxiv_date(date_str)

        # Assert
        assert result == "2024-12-28"

    def test_parse_biorxiv_date_invalid_format(self):
        """测试解析无效日期格式"""
        # Arrange
        date_str = "Invalid Date"

        # Act
        result = parse_biorxiv_date(date_str)

        # Assert
        assert result is None

    def test_parse_biorxiv_date_none_input(self):
        """测试 None 输入"""
        # Arrange & Act
        result = parse_biorxiv_date(None)

        # Assert
        assert result is None


class TestParseBiorxivPaper:
    """bioRxiv 论文解析测试"""

    def test_parse_biorxiv_paper_complete_data(self):
        """测试解析完整的论文数据"""
        # Arrange
        paper_data = {
            "title": "Evolution of gene regulation in Drosophila",
            "authors": "Smith J; Doe A; Johnson B",
            "abstract": "This study investigates gene regulation evolution...",
            "doi": "10.1101/2024.12.28.123456",
            "date": "2024-12-28",
            "version": 1,
            "category": "Evolutionary Biology",
        }

        # Act
        result = parse_biorxiv_paper(paper_data)

        # Assert
        assert result["title"] == "Evolution of gene regulation in Drosophila"
        assert result["authors"] == ["Smith J", "Doe A", "Johnson B"]
        assert result["abstract"] == "This study investigates gene regulation evolution..."
        assert result["doi"] == "10.1101/2024.12.28.123456"
        assert result["publication_date"] == "2024-12-28"
        assert result["source"] == "bioRxiv"

    def test_parse_biorxiv_paper_minimal_data(self):
        """测试解析最小数据"""
        # Arrange
        paper_data = {
            "title": "Minimal Paper",
            "doi": "10.1101/2024.12.28.789012",
        }

        # Act
        result = parse_biorxiv_paper(paper_data)

        # Assert
        assert result["title"] == "Minimal Paper"
        assert result["doi"] == "10.1101/2024.12.28.789012"
        assert result["authors"] == []
        assert result["abstract"] is None
        assert result["publication_date"] is None
        assert result["source"] == "bioRxiv"

    def test_parse_biorxiv_paper_no_title(self):
        """测试缺少标题的论文"""
        # Arrange
        paper_data = {
            "doi": "10.1101/2024.12.28.345678",
        }

        # Act
        result = parse_biorxiv_paper(paper_data)

        # Assert
        assert result == {}

    def test_parse_biorxiv_paper_with_version(self):
        """测试包含版本信息的论文"""
        # Arrange
        paper_data = {
            "title": "Versioned Paper",
            "doi": "10.1101/2024.12.28.111111",
            "version": 3,
        }

        # Act
        result = parse_biorxiv_paper(paper_data)

        # Assert
        assert result["title"] == "Versioned Paper"
        assert result["doi"] == "10.1101/2024.12.28.111111"
        assert result["source"] == "bioRxiv"


class TestFetchBiorxivPapers:
    """bioRxiv API 调用测试"""

    def test_fetch_biorxiv_papers_success(self, monkeypatch):
        """测试成功获取论文"""
        # Arrange
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "collection": [
                {
                    "title": "Paper 1",
                    "doi": "10.1101/2024.12.28.111111",
                },
                {
                    "title": "Paper 2",
                    "doi": "10.1101/2024.12.28.222222",
                },
            ]
        }

        def mock_get(url, params, timeout):
            return mock_response

        monkeypatch.setattr("requests.get", mock_get)

        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 31)

        # Act
        results = fetch_biorxiv_papers(start_date, end_date)

        # Assert
        assert len(results) == 2
        assert results[0]["title"] == "Paper 1"
        assert results[1]["title"] == "Paper 2"

    def test_fetch_biorxiv_papers_empty_response(self, monkeypatch):
        """测试空响应"""
        # Arrange
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"collection": []}

        def mock_get(url, params, timeout):
            return mock_response

        monkeypatch.setattr("requests.get", mock_get)

        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 31)

        # Act
        results = fetch_biorxiv_papers(start_date, end_date)

        # Assert
        assert len(results) == 0

    def test_fetch_biorxiv_papers_network_error(self, monkeypatch):
        """测试网络错误"""

        # Arrange
        def mock_get(url, params, timeout):
            raise Exception("Network error")

        monkeypatch.setattr("requests.get", mock_get)

        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 31)

        # Act & Assert
        with pytest.raises(Exception, match="Network error"):
            fetch_biorxiv_papers(start_date, end_date)
