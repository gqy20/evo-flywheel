"""Web API 客户端单元测试"""

from unittest.mock import Mock, patch

import pytest
import requests


@pytest.fixture
def mock_settings():
    """Mock settings"""
    settings = Mock()
    settings.api_base_url = "http://localhost:8000"
    settings.api_timeout = 30
    return settings


class TestAPIClientInit:
    """APIClient 初始化测试"""

    @patch("evo_flywheel.web.api_client.get_settings")
    def test_init_with_default_settings(self, mock_get_settings, mock_settings):
        """测试使用默认配置初始化"""
        mock_get_settings.return_value = mock_settings

        from evo_flywheel.web.api_client import APIClient

        client = APIClient()

        assert client.base_url == "http://localhost:8000"
        assert client.timeout == 30


class TestAPIClientGetStats:
    """APIClient.get_stats_overview 测试"""

    @patch("evo_flywheel.web.api_client.get_settings")
    def test_get_stats_overview_returns_data(self, mock_get_settings, mock_settings):
        """测试获取统计数据成功"""
        mock_get_settings.return_value = mock_settings

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_papers": 100,
            "analyzed_papers": 80,
            "embedded_papers": 60,
            "today_new": 5,
            "analysis_rate": 80.0,
            "embedding_rate": 60.0,
        }

        with patch("requests.get", return_value=mock_response):
            from evo_flywheel.web.api_client import APIClient

            client = APIClient()
            result = client.get_stats_overview()

            assert result["total_papers"] == 100
            assert result["analyzed_papers"] == 80
            assert result["today_new"] == 5


class TestAPIClientGetPapers:
    """APIClient.get_papers 测试"""

    @patch("evo_flywheel.web.api_client.get_settings")
    def test_get_papers_returns_list(self, mock_get_settings, mock_settings):
        """测试获取论文列表成功"""
        mock_get_settings.return_value = mock_settings

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 50,
            "papers": [
                {
                    "id": 1,
                    "title": "Test Paper",
                    "authors": ["Author A"],
                    "abstract": "Test abstract",
                    "importance_score": 85,
                }
            ],
        }

        with patch("requests.get", return_value=mock_response):
            from evo_flywheel.web.api_client import APIClient

            client = APIClient()
            result = client.get_papers(skip=0, limit=20)

            assert result["total"] == 50
            assert len(result["papers"]) == 1
            assert result["papers"][0]["title"] == "Test Paper"

    @patch("evo_flywheel.web.api_client.get_settings")
    def test_get_papers_with_filters(self, mock_get_settings, mock_settings):
        """测试带筛选条件的论文查询"""
        mock_get_settings.return_value = mock_settings

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"total": 10, "papers": []}

        with patch("requests.get", return_value=mock_response) as mock_get:
            from evo_flywheel.web.api_client import APIClient

            client = APIClient()
            client.get_papers(skip=0, limit=20, taxa="Mammalia", min_score=80)

            # 验证请求参数
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "taxa=Mammalia" in call_args[0][0]
            assert "min_score=80" in call_args[0][0]


class TestAPIClientSemanticSearch:
    """APIClient.semantic_search 测试"""

    @patch("evo_flywheel.web.api_client.get_settings")
    def test_semantic_search_returns_results(self, mock_get_settings, mock_settings):
        """测试语义搜索成功"""
        mock_get_settings.return_value = mock_settings

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": 1,
                    "title": "Similar Paper",
                    "similarity": 0.92,
                    "importance_score": 85,
                }
            ]
        }

        with patch("requests.get", return_value=mock_response):
            from evo_flywheel.web.api_client import APIClient

            client = APIClient()
            result = client.semantic_search(query="evolutionary genetics", limit=10)

            assert len(result["results"]) == 1
            assert result["results"][0]["similarity"] == 0.92


class TestAPIClientErrorHandling:
    """APIClient 错误处理测试"""

    @patch("evo_flywheel.web.api_client.get_settings")
    def test_http_404_returns_none(self, mock_get_settings, mock_settings):
        """测试 404 错误处理"""
        mock_get_settings.return_value = mock_settings

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404")

        with patch("requests.get", return_value=mock_response):
            from evo_flywheel.web.api_client import APIClient

            client = APIClient()
            result = client.get_paper(999)

            assert result is None

    @patch("evo_flywheel.web.api_client.get_settings")
    def test_http_500_returns_none(self, mock_get_settings, mock_settings):
        """测试 500 错误处理"""
        mock_get_settings.return_value = mock_settings

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("500")

        with patch("requests.get", return_value=mock_response):
            from evo_flywheel.web.api_client import APIClient

            client = APIClient()
            result = client.get_stats_overview()

            assert result is None

    @patch("evo_flywheel.web.api_client.get_settings")
    def test_connection_error_returns_none(self, mock_get_settings, mock_settings):
        """测试连接错误处理"""
        mock_get_settings.return_value = mock_settings

        with patch("requests.get", side_effect=requests.ConnectionError("Connection failed")):
            from evo_flywheel.web.api_client import APIClient

            client = APIClient()
            result = client.get_stats_overview()

            assert result is None
