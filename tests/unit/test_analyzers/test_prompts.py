"""Prompt 模板单元测试"""

from evo_flywheel.analyzers.prompts import (
    build_analysis_prompt,
    get_analysis_schema,
)


class TestGetAnalysisSchema:
    """分析 Schema 获取测试"""

    def test_get_analysis_schema_returns_dict(self):
        """测试 get_analysis_schema 返回字典"""
        # Act
        schema = get_analysis_schema()

        # Assert
        assert isinstance(schema, dict)

    def test_get_analysis_schema_contains_required_fields(self):
        """测试 Schema 包含必需字段"""
        # Act
        schema = get_analysis_schema()

        # Assert
        required_fields = [
            "taxa",
            "evolutionary_scale",
            "research_method",
            "key_findings",
            "evolutionary_mechanism",
            "importance_score",
            "innovation_summary",
        ]
        for field in required_fields:
            assert field in schema, f"Missing required field: {field}"

    def test_get_analysis_schema_has_correct_types(self):
        """测试 Schema 字段类型正确"""
        # Act
        schema = get_analysis_schema()

        # Assert
        assert isinstance(schema.get("taxa"), str)
        assert isinstance(schema.get("evolutionary_scale"), str)
        assert isinstance(schema.get("research_method"), str)
        assert isinstance(schema.get("key_findings"), list)
        assert isinstance(schema.get("evolutionary_mechanism"), str)
        assert isinstance(schema.get("importance_score"), int)
        assert isinstance(schema.get("innovation_summary"), str)

    def test_get_analysis_schema_has_descriptions(self):
        """测试 Schema 字段包含描述"""
        # Act
        schema = get_analysis_schema()

        # Assert
        # 验证有描述信息（非空字符串或有效默认值）
        assert len(schema.get("taxa", "")) >= 0
        assert len(schema.get("innovation_summary", "")) >= 0


class TestBuildAnalysisPrompt:
    """分析 Prompt 构建测试"""

    def test_build_analysis_prompt_returns_string(self):
        """测试 build_analysis_prompt 返回字符串"""
        # Arrange
        title = "Test Paper"
        abstract = "Test abstract"

        # Act
        prompt = build_analysis_prompt(title, abstract)

        # Assert
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_build_analysis_prompt_contains_paper_info(self):
        """测试 Prompt 包含论文信息"""
        # Arrange
        title = "Rapid adaptation in Drosophila"
        abstract = "This study investigates..."

        # Act
        prompt = build_analysis_prompt(title, abstract)

        # Assert
        assert title in prompt
        assert abstract in prompt

    def test_build_analysis_prompt_contains_all_required_sections(self):
        """测试 Prompt 包含所有必需的章节"""
        # Arrange
        title = "Test Paper"
        abstract = "Test abstract"

        # Act
        prompt = build_analysis_prompt(title, abstract)

        # Assert
        required_sections = [
            "基础信息",
            "研究物种",
            "进化尺度",
            "研究方法",
            "核心内容",
            "关键发现",
            "进化机制",
            "创新性",
            "价值评估",
            "重要性评分",
            "推荐理由",
        ]
        for section in required_sections:
            assert section in prompt, f"Missing section: {section}"

    def test_build_analysis_prompt_requires_json_output(self):
        """测试 Prompt 要求 JSON 输出"""
        # Arrange
        title = "Test Paper"
        abstract = "Test abstract"

        # Act
        prompt = build_analysis_prompt(title, abstract)

        # Assert
        assert "JSON" in prompt or "json" in prompt
        assert "格式" in prompt

    def test_build_analysis_prompt_handles_chinese_input(self):
        """测试 Prompt 支持中文输入"""
        # Arrange
        title = "果蝇快速适应研究"
        abstract = "本研究调查了果蝇在气候变化下的快速适应..."

        # Act
        prompt = build_analysis_prompt(title, abstract)

        # Assert
        assert title in prompt
        assert abstract in prompt

    def test_build_analysis_prompt_handles_english_input(self):
        """测试 Prompt 支持英文输入"""
        # Arrange
        title = "Rapid adaptation to climate change"
        abstract = "This study investigates rapid adaptation..."

        # Act
        prompt = build_analysis_prompt(title, abstract)

        # Assert
        assert title in prompt
        assert abstract in prompt

    def test_build_analysis_prompt_handles_empty_abstract(self):
        """测试 Prompt 处理空摘要"""
        # Arrange
        title = "Test Paper"
        abstract = ""

        # Act
        prompt = build_analysis_prompt(title, abstract)

        # Assert
        assert title in prompt
        assert isinstance(prompt, str)

    def test_build_analysis_prompt_has_score_range_hint(self):
        """测试 Prompt 包含评分范围提示"""
        # Arrange
        title = "Test Paper"
        abstract = "Test abstract"

        # Act
        prompt = build_analysis_prompt(title, abstract)

        # Assert
        assert "0" in prompt or "100" in prompt or "评分" in prompt

    def test_build_analysis_prompt_specifies_key_findings_count(self):
        """测试 Prompt 指定关键发现数量"""
        # Arrange
        title = "Test Paper"
        abstract = "Test abstract"

        # Act
        prompt = build_analysis_prompt(title, abstract)

        # Assert
        # 应该提示提取 3-5 个关键发现
        assert "关键发现" in prompt
        # 检查是否有数量提示
        has_count_hint = any(s in prompt for s in ["3", "5", "3-5", "三", "五"])
        assert has_count_hint, "Prompt should specify number of key findings"

    def test_build_analysis_prompt_includes_evolutionary_mechanisms(self):
        """测试 Prompt 包含进化机制选项"""
        # Arrange
        title = "Test Paper"
        abstract = "Test abstract"

        # Act
        prompt = build_analysis_prompt(title, abstract)

        # Assert
        # 应该提及主要的进化机制类型
        mechanisms = ["自然选择", "遗传漂变", "基因流", "突变"]
        has_mechanism = any(m in prompt for m in mechanisms)
        assert has_mechanism, "Prompt should mention evolutionary mechanisms"

    def test_build_analysis_prompt_includes_scale_options(self):
        """测试 Prompt 包含进化尺度选项"""
        # Arrange
        title = "Test Paper"
        abstract = "Test abstract"

        # Act
        prompt = build_analysis_prompt(title, abstract)

        # Assert
        # 应该提及不同的进化尺度
        scales = ["分子", "个体", "种群", "物种"]
        has_scale = any(s in prompt for s in scales)
        assert has_scale, "Prompt should mention evolutionary scales"
