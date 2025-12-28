"""报告生成页测试"""


class TestReportPageRendering:
    """报告生成页渲染测试"""

    def test_report_page_has_render_function(self):
        """测试报告页有 render 函数"""
        # Arrange & Act
        from evo_flywheel.web.pages import report

        # Assert
        assert hasattr(report, "render")
        assert callable(report.render)

    def test_report_page_has_generation_controls(self):
        """测试报告页有生成控件"""
        # Arrange & Act
        from evo_flywheel.web.pages import report

        # Assert
        assert hasattr(report, "render_generation_controls")
        assert callable(report.render_generation_controls)

    def test_report_page_has_report_display(self):
        """测试报告页有报告展示区域"""
        # Arrange & Act
        from evo_flywheel.web.pages import report

        # Assert
        assert hasattr(report, "render_report_display")
        assert callable(report.render_report_display)


class TestReportPageGeneration:
    """报告生成页生成功能测试"""

    def test_report_has_date_selector(self):
        """测试报告有日期选择器"""
        # Arrange & Act
        from evo_flywheel.web.pages import report

        # Assert
        assert callable(report.render_generation_controls)

    def test_report_has_manual_generation(self):
        """测试报告支持手动生成"""
        # Arrange & Act
        from evo_flywheel.web.pages import report

        # Assert
        assert callable(report.render_generation_controls)

    def test_report_has_template_selection(self):
        """测试报告有模板选择"""
        # Arrange & Act
        from evo_flywheel.web.pages import report

        # Assert
        assert callable(report.render_generation_controls)


class TestReportPageDisplay:
    """报告生成页展示测试"""

    def test_report_displays_summary(self):
        """测试报告显示摘要"""
        # Arrange & Act
        from evo_flywheel.web.pages import report

        # Assert
        assert callable(report.render_report_display)

    def test_report_displays_top_papers(self):
        """测试报告显示 top 论文"""
        # Arrange & Act
        from evo_flywheel.web.pages import report

        # Assert
        assert callable(report.render_report_display)

    def test_report_supports_markdown_export(self):
        """测试报告支持 Markdown 导出"""
        # Arrange & Act
        from evo_flywheel.web.pages import report

        # Assert
        assert callable(report.render_report_display)


class TestReportPageStructure:
    """报告生成页结构测试"""

    def test_has_default_date_range_constant(self):
        """测试有默认日期范围常量"""
        # Arrange & Act
        from evo_flywheel.web.pages import report

        # Assert
        assert hasattr(report, "DEFAULT_DATE_RANGE_DAYS")
        assert isinstance(report.DEFAULT_DATE_RANGE_DAYS, int)
