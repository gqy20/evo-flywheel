"""LLM 服务单元测试"""

from unittest import mock

import pytest
from evo_flywheel.analyzers.llm import (
    AnalysisResult,
    analyze_paper,
    parse_llm_response,
)


class TestAnalysisResult:
    """AnalysisResult 数据类测试"""

    def test_analysis_result_creation(self):
        """测试 AnalysisResult 创建"""
        # Arrange
        data = {
            "taxa": "Drosophila",
            "evolutionary_scale": "种群",
            "research_method": "实验",
            "key_findings": ["发现1", "发现2"],
            "evolutionary_mechanism": "自然选择",
            "importance_score": 85,
            "innovation_summary": "创新性总结",
        }

        # Act
        result = AnalysisResult(**data)

        # Assert
        assert result.taxa == "Drosophila"
        assert result.evolutionary_scale == "种群"
        assert result.research_method == "实验"
        assert len(result.key_findings) == 2
        assert result.importance_score == 85

    def test_analysis_result_default_values(self):
        """测试 AnalysisResult 默认值"""
        # Arrange & Act
        result = AnalysisResult(
            taxa="",
            evolutionary_scale="",
            research_method="",
            key_findings=[],
            evolutionary_mechanism="",
            importance_score=0,
            innovation_summary="",
        )

        # Assert
        assert result.taxa == ""
        assert result.importance_score == 0
        assert result.key_findings == []


class TestParseLLMResponse:
    """LLM 响应解析测试"""

    def test_parse_valid_json_response(self):
        """测试解析有效的 JSON 响应"""
        # Arrange
        response = """```json
{
    "taxa": "Drosophila melanogaster",
    "evolutionary_scale": "种群",
    "research_method": "实验",
    "key_findings": ["发现1", "发现2", "发现3"],
    "evolutionary_mechanism": "自然选择",
    "importance_score": 85,
    "innovation_summary": "首次观察到快速适应"
}
```"""

        # Act
        result = parse_llm_response(response)

        # Assert
        assert result.taxa == "Drosophila melanogaster"
        assert len(result.key_findings) == 3
        assert result.importance_score == 85

    def test_parse_json_without_markdown(self):
        """测试解析不带 markdown 的 JSON"""
        # Arrange
        response = """{"taxa": "Test", "evolutionary_scale": "个体", "research_method": "比较", "key_findings": ["发现"], "evolutionary_mechanism": "突变", "importance_score": 70, "innovation_summary": "测试"}"""

        # Act
        result = parse_llm_response(response)

        # Assert
        assert result.taxa == "Test"
        assert result.importance_score == 70

    def test_parse_response_with_extra_text(self):
        """测试解析包含额外文本的响应"""
        # Arrange
        response = """以下是分析结果：

{"taxa": "Test", "evolutionary_scale": "分子", "research_method": "系统发育", "key_findings": ["发现"], "evolutionary_mechanism": "基因流", "importance_score": 60, "innovation_summary": "测试"}

以上是分析结果。"""

        # Act
        result = parse_llm_response(response)

        # Assert
        assert result.taxa == "Test"

    def test_parse_malformed_json_raises_error(self):
        """测试解析格式错误的 JSON 抛出异常"""
        # Arrange
        response = '{"taxa": "Test", "invalid": }'

        # Act & Assert
        with pytest.raises(ValueError, match="解析失败"):
            parse_llm_response(response)

    def test_parse_empty_response_raises_error(self):
        """测试解析空响应抛出异常"""
        # Arrange
        response = ""

        # Act & Assert
        with pytest.raises(ValueError, match="响应为空"):
            parse_llm_response(response)

    def test_parse_missing_required_field_raises_error(self):
        """测试缺少必需字段抛出异常"""
        # Arrange
        response = '{"taxa": "Test", "evolutionary_scale": "个体"}'  # 缺少必需字段

        # Act & Assert
        with pytest.raises(ValueError, match="缺少必需字段"):
            parse_llm_response(response)


class TestAnalyzePaper:
    """论文分析测试"""

    def test_analyze_paper_calls_openai_api(self, monkeypatch):
        """测试 analyze_paper 调用 OpenAI API"""
        # Arrange
        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock()]
        mock_response.choices[
            0
        ].message.content = '{"taxa": "Test", "evolutionary_scale": "种群", "research_method": "实验", "key_findings": ["发现"], "evolutionary_mechanism": "自然选择", "importance_score": 80, "innovation_summary": "测试"}'
        mock_response.usage.total_tokens = 1000

        mock_client = mock.Mock()
        mock_client.chat.completions.create.return_value = mock_response

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act
        result = analyze_paper("Test Title", "Test Abstract")

        # Assert
        assert mock_client.chat.completions.create.called
        assert result.taxa == "Test"
        assert result.usage.total_tokens == 1000

    def test_analyze_paper_returns_analysis_result(self, monkeypatch):
        """测试 analyze_paper 返回 AnalysisResult"""
        # Arrange
        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock()]
        mock_response.choices[
            0
        ].message.content = '{"taxa": "Drosophila", "evolutionary_scale": "种群", "research_method": "实验", "key_findings": ["发现"], "evolutionary_mechanism": "自然选择", "importance_score": 85, "innovation_summary": "测试"}'
        mock_response.usage.total_tokens = 1000

        mock_client = mock.Mock()
        mock_client.chat.completions.create.return_value = mock_response

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act
        result = analyze_paper("Title", "Abstract")

        # Assert
        assert isinstance(result, AnalysisResult)
        assert result.taxa == "Drosophila"

    def test_analyze_paper_includes_prompt_in_request(self, monkeypatch):
        """测试分析请求包含正确的 Prompt"""
        # Arrange
        title = "Test Paper"
        abstract = "Test abstract"

        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock()]
        mock_response.choices[
            0
        ].message.content = '{"taxa": "T", "evolutionary_scale": "E", "research_method": "M", "key_findings": [], "evolutionary_mechanism": "N", "importance_score": 0, "innovation_summary": ""}'
        mock_response.usage.total_tokens = 1000

        mock_client = mock.Mock()
        mock_client.chat.completions.create.return_value = mock_response

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act
        analyze_paper(title, abstract)

        # Assert
        call_args = mock_client.chat.completions.create.call_args
        assert call_args is not None
        messages = call_args.kwargs.get("messages", [])
        assert len(messages) > 0
        # 验证用户消息包含标题和摘要
        user_message = messages[-1]["content"]
        assert title in user_message
        assert abstract in user_message

    def test_analyze_paper_handles_api_error(self, monkeypatch):
        """测试分析处理 API 错误"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act & Assert
        with pytest.raises(Exception, match="API Error"):
            analyze_paper("Title", "Abstract")

    def test_analyze_paper_retries_on_failure(self, monkeypatch):
        """测试分析失败时重试"""
        # Arrange
        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock()]
        mock_response.choices[
            0
        ].message.content = '{"taxa": "T", "evolutionary_scale": "E", "research_method": "M", "key_findings": [], "evolutionary_mechanism": "N", "importance_score": 0, "innovation_summary": ""}'
        mock_response.usage.total_tokens = 1000

        mock_client = mock.Mock()
        mock_client.chat.completions.create.side_effect = [
            Exception("Temporary error"),
            mock_response,
        ]

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act
        result = analyze_paper("Title", "Abstract", max_retries=2)

        # Assert
        assert mock_client.chat.completions.create.call_count == 2
        assert result.taxa == "T"

    def test_analyze_paper_exceeds_max_retries_raises_error(self, monkeypatch):
        """测试超过最大重试次数抛出错误"""
        # Arrange
        mock_client = mock.Mock()
        mock_client.chat.completions.create.side_effect = Exception("Persistent error")

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act & Assert
        with pytest.raises(Exception, match="Persistent error"):
            analyze_paper("Title", "Abstract", max_retries=2)

    def test_analyze_paper_tracks_token_usage(self, monkeypatch):
        """测试分析追踪 Token 使用"""
        # Arrange
        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock()]
        mock_response.choices[
            0
        ].message.content = '{"taxa": "T", "evolutionary_scale": "E", "research_method": "M", "key_findings": [], "evolutionary_mechanism": "N", "importance_score": 0, "innovation_summary": ""}'
        mock_response.usage.prompt_tokens = 500
        mock_response.usage.completion_tokens = 300
        mock_response.usage.total_tokens = 800

        mock_client = mock.Mock()
        mock_client.chat.completions.create.return_value = mock_response

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act
        result = analyze_paper("Title", "Abstract")

        # Assert
        assert result.usage.prompt_tokens == 500
        assert result.usage.completion_tokens == 300
        assert result.usage.total_tokens == 800
