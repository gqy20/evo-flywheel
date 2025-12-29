"""论文详情页测试"""

from unittest import mock


class TestDetailPageAPIIntegration:
    """论文详情页 API 集成测试"""

    @mock.patch("evo_flywheel.web.views.detail.APIClient")
    def test_get_paper_detail_uses_api_client(self, mock_api_client_class):
        """测试获取论文详情使用 APIClient"""
        # Arrange - Mock API 返回
        mock_client = mock.Mock()
        mock_client.get_paper_detail.return_value = {
            "id": 1,
            "title": "Test Paper",
            "authors": ["Author A", "Author B"],
            "abstract": "Test abstract",
            "journal": "Nature",
            "publication_date": "2024-01-01",
            "importance_score": 85,
            "taxa": "Drosophila melanogaster",
            "doi": "10.1234/test.doi",
            "url": "https://example.com/paper",
            "key_findings": ["Finding 1", "Finding 2"],
            "evolutionary_mechanism": "Natural selection",
            "analysis_date": "2024-01-02",
        }
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.detail import get_paper_detail

        result = get_paper_detail(paper_id=1)

        # Assert - 验证返回论文详情
        assert result is not None
        assert result["title"] == "Test Paper"
        assert result["importance_score"] == 85

    @mock.patch("evo_flywheel.web.views.detail.APIClient")
    def test_get_paper_detail_passes_paper_id(self, mock_api_client_class):
        """测试获取论文详情传递论文 ID"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.get_paper_detail.return_value = {"id": 42, "title": "Paper"}
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.detail import get_paper_detail

        get_paper_detail(paper_id=42)

        # Assert - 验证 get_paper_detail 被调用
        mock_client.get_paper_detail.assert_called_once()
        call_kwargs = mock_client.get_paper_detail.call_args.kwargs
        assert call_kwargs.get("paper_id") == 42

    @mock.patch("evo_flywheel.web.views.detail.APIClient")
    def test_get_paper_detail_returns_none_on_error(self, mock_api_client_class):
        """测试 API 错误时返回 None"""
        # Arrange - Mock API 返回 None (错误情况)
        mock_client = mock.Mock()
        mock_client.get_paper_detail.return_value = None
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.detail import get_paper_detail

        result = get_paper_detail(paper_id=999)

        # Assert - 应返回 None 表示失败
        assert result is None

    @mock.patch("evo_flywheel.web.views.detail.APIClient")
    def test_submit_feedback_uses_api_client(self, mock_api_client_class):
        """测试提交反馈使用 APIClient"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.submit_feedback.return_value = {"success": True, "message": "Feedback received"}
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.detail import submit_feedback

        result = submit_feedback(
            paper_id=1,
            rating=5,
            comment="Great paper!",
        )

        # Assert - 验证返回成功
        assert result is True

    @mock.patch("evo_flywheel.web.views.detail.APIClient")
    def test_submit_feedback_passes_all_params(self, mock_api_client_class):
        """测试提交反馈传递所有参数"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.submit_feedback.return_value = {"success": True}
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.detail import submit_feedback

        submit_feedback(
            paper_id=123,
            rating=4,
            comment="Interesting findings",
        )

        # Assert - 验证 submit_feedback 被调用
        mock_client.submit_feedback.assert_called_once()
        call_kwargs = mock_client.submit_feedback.call_args.kwargs
        assert call_kwargs.get("paper_id") == 123
        assert call_kwargs.get("rating") == 4
        assert call_kwargs.get("comment") == "Interesting findings"

    @mock.patch("evo_flywheel.web.views.detail.APIClient")
    def test_submit_feedback_handles_api_error(self, mock_api_client_class):
        """测试提交反馈处理 API 错误"""
        # Arrange - Mock API 返回 None (错误情况)
        mock_client = mock.Mock()
        mock_client.submit_feedback.return_value = None
        mock_api_client_class.return_value = mock_client

        # Act
        from evo_flywheel.web.views.detail import submit_feedback

        result = submit_feedback(
            paper_id=1,
            rating=3,
            comment="Average",
        )

        # Assert - 应返回 False 表示失败
        assert result is False


class TestDetailPageRendering:
    """论文详情页渲染测试"""

    def test_detail_page_has_render_function(self):
        """测试详情页有 render 函数"""
        # Arrange & Act
        from evo_flywheel.web.views import detail

        # Assert
        assert hasattr(detail, "render")
        assert callable(detail.render)

    def test_detail_page_has_get_paper_detail_function(self):
        """测试详情页有获取论文详情函数"""
        # Arrange & Act
        from evo_flywheel.web.views import detail

        # Assert
        assert hasattr(detail, "get_paper_detail")
        assert callable(detail.get_paper_detail)

    def test_detail_page_has_submit_feedback_function(self):
        """测试详情页有提交反馈函数"""
        # Arrange & Act
        from evo_flywheel.web.views import detail

        # Assert
        assert hasattr(detail, "submit_feedback")
        assert callable(detail.submit_feedback)

    def test_detail_page_has_render_feedback_section_function(self):
        """测试详情页有渲染反馈区域函数"""
        # Arrange & Act
        from evo_flywheel.web.views import detail

        # Assert
        assert hasattr(detail, "render_feedback_section")
        assert callable(detail.render_feedback_section)


class TestDetailPageStructure:
    """论文详情页结构测试"""

    def test_module_exists(self):
        """测试模块存在"""
        # Arrange & Act
        from evo_flywheel.web.views import detail

        # Assert - 模块应能正常导入
        assert detail is not None
