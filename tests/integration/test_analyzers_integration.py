"""分析层集成测试

测试完整的论文分析工作流程，包括：
- 单篇论文端到端分析
- 批量处理工作流
- 错误恢复和缓存
"""

from unittest import mock

import pytest


@pytest.fixture(autouse=True)
def clear_analysis_cache():
    """每个测试前清理分析缓存"""
    import evo_flywheel.analyzers.batch as batch_module

    batch_module._analysis_cache.clear()
    yield
    batch_module._analysis_cache.clear()


class TestSinglePaperAnalysisE2E:
    """单篇论文端到端分析测试"""

    def test_full_analysis_workflow(self, monkeypatch):
        """测试完整的单篇论文分析工作流"""
        # Arrange - 模拟 OpenAI API 响应
        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock()]
        mock_response.choices[0].message.content = """{
    "taxa": "Drosophila melanogaster",
    "evolutionary_scale": "种群",
    "research_method": "实验",
    "key_findings": [
        "发现了快速适应环境的新机制",
        "验证了自然选择理论",
        "提供了新的实验方法"
    ],
    "evolutionary_mechanism": "自然选择",
    "importance_score": 85,
    "innovation_summary": "首次在实验中观察到快速适应，对进化生物学具有重要意义"
}"""
        mock_response.usage.prompt_tokens = 500
        mock_response.usage.completion_tokens = 300
        mock_response.usage.total_tokens = 800

        mock_client = mock.Mock()
        mock_client.chat.completions.create.return_value = mock_response

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # 准备论文数据
        from evo_flywheel.analyzers import llm

        title = "Experimental Evolution in Drosophila"
        abstract = (
            "We conducted a long-term experiment with Drosophila populations "
            "to study rapid adaptation to environmental changes."
        )

        # Act - 调用 LLM 分析
        result = llm.analyze_paper(title, abstract)

        # Assert - 验证完整结果
        assert result.taxa == "Drosophila melanogaster"
        assert result.evolutionary_scale == "种群"
        assert result.research_method == "实验"
        assert len(result.key_findings) == 3
        assert result.evolutionary_mechanism == "自然选择"
        assert result.importance_score == 85
        assert result.innovation_summary != ""
        assert result.usage.total_tokens == 800

        # 验证 API 被正确调用
        assert mock_client.chat.completions.create.call_count == 1
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "glm-4-flash"
        assert len(call_kwargs["messages"]) == 2  # system + user

    def test_analysis_with_invalid_api_response(self, monkeypatch):
        """测试 API 返回无效响应时的处理"""
        # Arrange - API 返回无效 JSON
        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock()]
        mock_response.choices[0].message.content = "Invalid response"

        mock_client = mock.Mock()
        mock_client.chat.completions.create.return_value = mock_response

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act & Assert
        from evo_flywheel.analyzers import llm

        with pytest.raises(ValueError, match="解析失败|缺少必需字段"):
            llm.analyze_paper("Title", "Abstract")


class TestBatchAnalysisWorkflow:
    """批量分析工作流集成测试"""

    def test_batch_analysis_filters_already_analyzed(self, monkeypatch):
        """测试批量分析正确过滤已分析的论文"""
        # Arrange
        papers = [
            {
                "id": 1,
                "doi": "10.1234/test1",
                "title": "Paper 1",
                "abstract": "Abstract 1",
                "taxa": "Done",
                "evolutionary_scale": "种群",
                "research_method": "实验",
                "key_findings": ["发现"],
                "evolutionary_mechanism": "自然选择",
                "importance_score": 80,
                "innovation_summary": "创新",
            },  # 已分析
            {
                "id": 2,
                "doi": "10.1234/test2",
                "title": "Paper 2",
                "abstract": "Abstract 2",
            },  # 未分析
            {
                "id": 3,
                "doi": "10.1234/test3",
                "title": "Paper 3",
                "abstract": "Abstract 3",
                "taxa": "Done",
                "evolutionary_scale": "个体",
                "research_method": "比较",
                "key_findings": ["发现"],
                "evolutionary_mechanism": "突变",
                "importance_score": 70,
                "innovation_summary": "创新",
            },  # 已分析
        ]

        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock()]
        mock_response.choices[0].message.content = """{
    "taxa": "New",
    "evolutionary_scale": "分子",
    "research_method": "系统发育",
    "key_findings": ["新发现"],
    "evolutionary_mechanism": "基因流",
    "importance_score": 75,
    "innovation_summary": "新研究"
}"""
        mock_response.usage.total_tokens = 1000

        mock_client = mock.Mock()
        mock_client.chat.completions.create.return_value = mock_response

        # 同时模拟 llm 和 batch 中的导入
        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act
        from evo_flywheel.analyzers import batch

        results = batch.analyze_papers_batch(papers)

        # Assert
        assert len(results) == 3
        # 只有论文 2 被分析
        assert mock_client.chat.completions.create.call_count == 1
        # 验证已分析的论文被标记
        assert results[0]["_cached"] is True
        assert results[2]["_cached"] is True
        # 验证新分析的论文有完整字段
        assert results[1]["taxa"] == "New"
        assert results[1]["importance_score"] == 75

    def test_batch_analysis_uses_cache_across_calls(self, monkeypatch):
        """测试批量分析跨调用使用缓存"""
        # Arrange
        papers_batch1 = [{"id": 1000, "doi": "10.1234/cachetest1", "title": "P1", "abstract": "A1"}]
        papers_batch2 = [
            {"id": 1000, "doi": "10.1234/cachetest1", "title": "P1", "abstract": "A1"},
            {"id": 2000, "doi": "10.1234/cachetest2", "title": "P2", "abstract": "A2"},
        ]

        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock()]
        mock_response.choices[0].message.content = """{
    "taxa": "Cached",
    "evolutionary_scale": "种群",
    "research_method": "实验",
    "key_findings": ["发现"],
    "evolutionary_mechanism": "自然选择",
    "importance_score": 80,
    "innovation_summary": "测试"
}"""
        mock_response.usage.total_tokens = 1000

        mock_client = mock.Mock()
        mock_client.chat.completions.create.return_value = mock_response

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act - 第一批调用
        from evo_flywheel.analyzers import batch

        batch.analyze_papers_batch(papers_batch1)

        # Assert - 第一批后 API 被调用 1 次
        assert mock_client.chat.completions.create.call_count == 1

        # Act - 第二批调用（论文 1 应该从缓存获取）
        results2 = batch.analyze_papers_batch(papers_batch2)

        # Assert - 第二批后总共调用 2 次（论文 2 被分析）
        assert mock_client.chat.completions.create.call_count == 2
        # 论文 1 从缓存
        assert results2[0]["_cached"] is True
        assert results2[0]["taxa"] == "Cached"
        # 论文 2 新分析
        assert results2[1]["taxa"] == "Cached"
        assert "_cached" not in results2[1] or not results2[1].get("_cached")

    def test_batch_analysis_handles_partial_failures(self, monkeypatch):
        """测试批量处理部分失败的场景"""
        # Arrange
        papers = [
            {"id": 10, "doi": "10.1234/10", "title": "P1", "abstract": "A1"},
            {"id": 20, "doi": "10.1234/20", "title": "P2", "abstract": "A2"},
            {"id": 30, "doi": "10.1234/30", "title": "P3", "abstract": "A3"},
        ]

        mock_response_success = mock.Mock()
        mock_response_success.choices = [mock.Mock()]
        mock_response_success.choices[0].message.content = """{
    "taxa": "TestSuccess",
    "evolutionary_scale": "种群",
    "research_method": "实验",
    "key_findings": ["发现"],
    "evolutionary_mechanism": "自然选择",
    "importance_score": 80,
    "innovation_summary": "成功"
}"""
        mock_response_success.usage.total_tokens = 1000

        # 创建不同的 mock 实例用于不同的论文
        mock_client = mock.Mock()

        def create_side_effect(**kwargs):
            """根据论文内容返回不同的响应"""
            messages = kwargs.get("messages", [])
            # 从用户消息中提取论文信息
            user_msg = str(messages) if messages else ""
            if "P2" in user_msg or "A2" in user_msg:
                raise Exception("API Error")

            return mock_response_success

        mock_client.chat.completions.create.side_effect = create_side_effect

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act
        from evo_flywheel.analyzers import batch

        results = batch.analyze_papers_batch(papers, continue_on_error=True)

        # Assert
        assert len(results) == 3
        # 论文 1 和 3 应该成功
        successful = [r for r in results if "_error" not in r]
        failed = [r for r in results if "_error" in r]
        assert len(successful) == 2
        assert len(failed) == 1
        assert all(r["taxa"] == "TestSuccess" for r in successful)

    def test_batch_analysis_respects_dry_run(self, monkeypatch):
        """测试批量处理 dry_run 模式"""
        # Arrange
        papers = [
            {"id": 1, "doi": "10.1234/1", "title": "P1", "abstract": "A1"},
            {"id": 2, "doi": "10.1234/2", "title": "P2", "abstract": "A2"},
        ]

        mock_client = mock.Mock()

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act
        from evo_flywheel.analyzers import batch

        results = batch.analyze_papers_batch(papers, dry_run=True)

        # Assert
        assert len(results) == 2
        # dry_run 模式不调用 API
        assert mock_client.chat.completions.create.call_count == 0
        # 所有论文都被标记为跳过（需要分析的论文）
        assert all(r.get("_skipped") for r in results)


class TestAnalysisQuality:
    """分析质量验证测试"""

    def test_analysis_produces_structured_output(self, monkeypatch):
        """测试分析产生结构化的输出"""
        # Arrange
        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock()]
        mock_response.choices[0].message.content = """{
    "taxa": "Homo sapiens",
    "evolutionary_scale": "分子",
    "research_method": "系统发育分析",
    "key_findings": [
        "发现了新的基因变异位点",
        "重建了进化历史",
        "验证了分子钟假设"
    ],
    "evolutionary_mechanism": "基因流动",
    "importance_score": 90,
    "innovation_summary": "使用新的测序技术，提供了更精确的进化时间估计"
}"""
        mock_response.usage.prompt_tokens = 600
        mock_response.usage.completion_tokens = 400
        mock_response.usage.total_tokens = 1000

        mock_client = mock.Mock()
        mock_client.chat.completions.create.return_value = mock_response

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act
        from evo_flywheel.analyzers import llm

        result = llm.analyze_paper(
            "Human Evolutionary Genomics", "Genomic analysis of human populations"
        )

        # Assert - 验证输出结构
        assert isinstance(result.taxa, str)
        assert isinstance(result.evolutionary_scale, str)
        assert isinstance(result.research_method, str)
        assert isinstance(result.key_findings, list)
        assert all(isinstance(f, str) for f in result.key_findings)
        assert isinstance(result.evolutionary_mechanism, str)
        assert isinstance(result.importance_score, int)
        assert 0 <= result.importance_score <= 100
        assert isinstance(result.innovation_summary, str)

        # 验证 Token 使用
        assert result.usage.prompt_tokens > 0
        assert result.usage.completion_tokens > 0
        assert result.usage.total_tokens > 0

    def test_batch_handles_various_paper_types(self, monkeypatch):
        """测试批量处理处理不同类型的论文"""
        # Arrange - 不同进化尺度和方法
        papers = [
            {
                "id": 1,
                "title": "Molecular Evolution",
                "abstract": "DNA sequence analysis",
            },
            {
                "id": 2,
                "title": "Population Genetics",
                "abstract": "Allele frequency study",
            },
            {
                "id": 3,
                "title": "Experimental Evolution",
                "abstract": "Lab selection experiment",
            },
        ]

        def create_mock_response(scale, method, mechanism):
            mock_resp = mock.Mock()
            mock_resp.choices = [mock.Mock()]
            mock_resp.choices[0].message.content = f"""{{
    "taxa": "Various",
    "evolutionary_scale": "{scale}",
    "research_method": "{method}",
    "key_findings": ["发现"],
    "evolutionary_mechanism": "{mechanism}",
    "importance_score": 75,
    "innovation_summary": "研究"
}}"""
            mock_resp.usage.total_tokens = 800
            return mock_resp

        mock_client = mock.Mock()
        mock_client.chat.completions.create.side_effect = [
            create_mock_response("分子", "系统发育", "突变"),
            create_mock_response("种群", "群体遗传", "自然选择"),
            create_mock_response("个体", "实验", "基因流动"),
        ]

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act
        from evo_flywheel.analyzers import batch

        results = batch.analyze_papers_batch(papers)

        # Assert - 验证至少有不同类型的分析结果
        assert len(results) == 3
        # 收集所有的进化尺度
        scales = {r["evolutionary_scale"] for r in results}
        methods = {r["research_method"] for r in results}
        # 验证有不同的结果
        assert len(scales) > 1
        assert len(methods) > 1
        # 验证包含预期的值
        assert "分子" in scales
        assert "种群" in scales
        assert "实验" in methods


class TestErrorRecovery:
    """错误恢复和边界情况测试"""

    def test_analysis_retries_on_transient_failure(self, monkeypatch):
        """测试瞬态失败时的重试机制"""
        # Arrange
        mock_response_success = mock.Mock()
        mock_response_success.choices = [mock.Mock()]
        mock_response_success.choices[0].message.content = """{
    "taxa": "Test",
    "evolutionary_scale": "种群",
    "research_method": "实验",
    "key_findings": ["发现"],
    "evolutionary_mechanism": "自然选择",
    "importance_score": 80,
    "innovation_summary": "测试"
}"""
        mock_response_success.usage.total_tokens = 1000

        mock_client = mock.Mock()
        # 第一次失败，第二次成功
        mock_client.chat.completions.create.side_effect = [
            Exception("Rate limit"),
            mock_response_success,
        ]

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act
        from evo_flywheel.analyzers import llm

        result = llm.analyze_paper("Title", "Abstract", max_retries=3)

        # Assert
        assert result.taxa == "Test"
        assert mock_client.chat.completions.create.call_count == 2

    def test_batch_includes_error_metadata(self, monkeypatch):
        """测试批量处理在失败时包含错误元数据"""
        # Arrange
        papers = [
            {"id": 100, "doi": "10.1234/100", "title": "Success", "abstract": "A"},
            {"id": 200, "doi": "10.1234/200", "title": "Fail", "abstract": "B"},
        ]

        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock()]
        mock_response.choices[0].message.content = """{
    "taxa": "TestSuccess",
    "evolutionary_scale": "种群",
    "research_method": "实验",
    "key_findings": ["发现"],
    "evolutionary_mechanism": "自然选择",
    "importance_score": 80,
    "innovation_summary": "成功"
}"""
        mock_response.usage.total_tokens = 1000

        # 根据消息内容决定成功或失败
        mock_client = mock.Mock()

        def side_effect_func(**kwargs):
            messages = kwargs.get("messages", [])
            msg_str = str(messages)
            if "Fail" in msg_str:
                raise Exception("Network error")
            return mock_response

        mock_client.chat.completions.create.side_effect = side_effect_func

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act
        from evo_flywheel.analyzers import batch

        results = batch.analyze_papers_batch(papers, continue_on_error=True)

        # Assert
        successful = [r for r in results if "_error" not in r]
        failed = [r for r in results if "_error" in r]
        assert len(successful) == 1
        assert len(failed) == 1
        # 验证失败论文保留原始数据
        assert failed[0]["title"] == "Fail"

    def test_handles_malformed_api_response(self, monkeypatch):
        """测试处理格式错误的 API 响应"""
        # Arrange
        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock()]
        mock_response.choices[0].message.content = "Not valid JSON"

        mock_client = mock.Mock()
        mock_client.chat.completions.create.return_value = mock_response

        monkeypatch.setattr("evo_flywheel.analyzers.llm.get_openai_client", lambda: mock_client)

        # Act & Assert
        from evo_flywheel.analyzers import batch

        # 使用唯一的 ID 避免缓存干扰
        papers = [{"id": 999, "doi": "10.1234/malformed", "title": "Bad", "abstract": "A"}]
        results = batch.analyze_papers_batch(papers, continue_on_error=True)

        # 应该捕获错误并继续
        assert len(results) == 1
        assert "_error" in results[0]
        # 验证错误信息提到解析失败
        assert "解析" in results[0]["_error"] or "JSON" in results[0]["_error"]
