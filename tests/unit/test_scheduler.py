"""采集调度器单元测试"""

import contextlib
from datetime import datetime
from unittest import mock

from evo_flywheel.scheduler.jobs import (
    collect_daily_papers,
    load_rss_sources,
    main,
    schedule_daily_collection,
)


class TestLoadRSSSources:
    """RSS 源加载测试"""

    def test_load_rss_sources_success(self, monkeypatch, tmp_path):
        """测试成功加载 RSS 源配置"""
        # Arrange
        yaml_content = """
sources:
  test_source:
    type: rss
    name: Test Source
    url: https://example.com/feed.rss
    priority: 1
    enabled: true
"""
        config_file = tmp_path / "sources.yaml"
        config_file.write_text(yaml_content)

        monkeypatch.setattr("evo_flywheel.scheduler.jobs.Path", lambda p: config_file)

        # Act
        sources = load_rss_sources(str(config_file))

        # Assert
        assert len(sources) == 1
        assert sources[0]["name"] == "Test Source"
        assert sources[0]["url"] == "https://example.com/feed.rss"

    def test_load_rss_sources_filters_disabled(self, monkeypatch, tmp_path):
        """测试过滤禁用的源"""
        # Arrange
        yaml_content = """
sources:
  enabled_source:
    type: rss
    name: Enabled Source
    url: https://example.com/enabled.rss
    priority: 1
    enabled: true
  disabled_source:
    type: rss
    name: Disabled Source
    url: https://example.com/disabled.rss
    priority: 2
    enabled: false
"""
        config_file = tmp_path / "sources.yaml"
        config_file.write_text(yaml_content)

        monkeypatch.setattr("evo_flywheel.scheduler.jobs.Path", lambda p: config_file)

        # Act
        sources = load_rss_sources(str(config_file))

        # Assert
        assert len(sources) == 1
        assert sources[0]["name"] == "Enabled Source"

    def test_load_rss_sources_empty_file(self, monkeypatch, tmp_path):
        """测试空配置文件"""
        # Arrange
        yaml_content = """
sources: {}
"""
        config_file = tmp_path / "sources.yaml"
        config_file.write_text(yaml_content)

        monkeypatch.setattr("evo_flywheel.scheduler.jobs.Path", lambda p: config_file)

        # Act
        sources = load_rss_sources(str(config_file))

        # Assert
        assert sources == []

    def test_load_rss_sources_missing_file(self, monkeypatch, tmp_path):
        """测试配置文件不存在"""
        # Arrange
        config_file = tmp_path / "nonexistent.yaml"

        monkeypatch.setattr("evo_flywheel.scheduler.jobs.Path", lambda p: config_file)

        # Act
        sources = load_rss_sources(str(config_file))

        # Assert
        assert sources == []


class TestCollectDailyPapers:
    """每日采集任务测试"""

    def test_collect_daily_papers_success(self, monkeypatch):
        """测试成功执行每日采集"""
        # Arrange
        mock_sources = [{"name": "Test Source", "url": "https://example.com/feed.rss"}]

        def mock_collect_all(start_date, end_date, rss_sources, category):
            return [{"title": "Test Paper", "doi": "10.1234/test.001"}]

        monkeypatch.setattr(
            "evo_flywheel.scheduler.jobs.collect_from_all_sources", mock_collect_all
        )

        # Act
        papers = collect_daily_papers(mock_sources)

        # Assert
        assert len(papers) == 1
        assert papers[0]["title"] == "Test Paper"

    def test_collect_daily_papers_with_default_date_range(self, monkeypatch):
        """测试使用默认日期范围（最近7天）"""
        # Arrange
        mock_sources = []

        call_args = {"captured": None}

        def mock_collect_all(start_date, end_date, rss_sources, category):
            call_args["captured"] = (start_date, end_date)
            return []

        monkeypatch.setattr(
            "evo_flywheel.scheduler.jobs.collect_from_all_sources", mock_collect_all
        )

        # Act
        collect_daily_papers(mock_sources)

        # Assert
        start, end = call_args["captured"]
        assert (end - start).days == 7

    def test_collect_daily_papers_custom_date_range(self, monkeypatch):
        """测试自定义日期范围"""
        # Arrange
        mock_sources = []

        call_args = {"captured": None}

        def mock_collect_all(start_date, end_date, rss_sources, category):
            call_args["captured"] = (start_date, end_date)
            return []

        monkeypatch.setattr(
            "evo_flywheel.scheduler.jobs.collect_from_all_sources", mock_collect_all
        )

        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 31)

        # Act
        collect_daily_papers(mock_sources, start_date, end_date)

        # Assert
        start, end = call_args["captured"]
        assert start == start_date
        assert end == end_date


class TestScheduleDailyCollection:
    """调度器配置测试"""

    def test_schedule_daily_collection_configures_scheduler(self, monkeypatch):
        """测试调度器配置"""
        # Arrange
        mock_scheduler_cls = mock.Mock()
        mock_scheduler = mock.Mock()
        mock_scheduler_cls.return_value = mock_scheduler

        monkeypatch.setattr("evo_flywheel.scheduler.jobs.BackgroundScheduler", mock_scheduler_cls)

        # Act
        scheduler = schedule_daily_collection(hour=9, minute=0)

        # Assert
        mock_scheduler_cls.assert_called_once()
        mock_scheduler.add_job.assert_called_once()
        assert scheduler == mock_scheduler

    def test_schedule_daily_collection_with_custom_time(self, monkeypatch):
        """测试自定义采集时间"""
        # Arrange
        mock_scheduler_cls = mock.Mock()
        mock_scheduler = mock.Mock()
        mock_scheduler_cls.return_value = mock_scheduler

        monkeypatch.setattr("evo_flywheel.scheduler.jobs.BackgroundScheduler", mock_scheduler_cls)

        # Act
        schedule_daily_collection(hour=14, minute=30)

        # Assert
        mock_scheduler.add_job.assert_called_once()
        # 检查 add_job 被调用时的参数
        call_kwargs = mock_scheduler.add_job.call_args.kwargs
        assert call_kwargs.get("trigger") == "cron"
        assert call_kwargs.get("hour") == 14
        assert call_kwargs.get("minute") == 30


class TestMain:
    """命令行入口测试"""

    def test_main_collects_papers(self, monkeypatch):
        """测试 main 函数执行采集"""
        # Arrange
        collected_papers = [{"title": "Paper 1", "doi": "10.1234/test.001"}]
        call_count = {"count": 0}

        def mock_collect_daily(sources=None, start=None, end=None):
            call_count["count"] += 1
            return collected_papers

        monkeypatch.setattr("evo_flywheel.scheduler.jobs.collect_daily_papers", mock_collect_daily)

        # Act
        main()

        # Assert
        assert call_count["count"] == 1

    def test_main_handles_exceptions_gracefully(self, monkeypatch):
        """测试 main 函数异常处理"""
        # Arrange
        call_count = {"count": 0}

        def mock_collect_daily(sources=None, start=None, end=None):
            call_count["count"] += 1
            raise Exception("Network error")

        monkeypatch.setattr("evo_flywheel.scheduler.jobs.collect_daily_papers", mock_collect_daily)

        # Act & Assert
        # 不应该抛出异常，应该优雅处理
        try:
            main()
        except Exception as e:
            raise AssertionError(f"main() should handle exceptions, but raised: {e}") from e

        assert call_count["count"] == 1

    def test_main_with_scheduler_mode(self, monkeypatch):
        """测试调度器模式启动调度器配置"""
        # Arrange
        mock_scheduler = mock.Mock()
        mock_scheduler.start = mock.Mock()
        mock_scheduler.shutdown = mock.Mock()

        # 模拟调度器启动后的无限循环 - 让它立即抛出 KeyboardInterrupt
        def mock_sleep_side_effect(seconds):
            raise KeyboardInterrupt()

        call_count = {"schedule_called": False}

        def mock_schedule_daily(hour=9, minute=0):
            call_count["schedule_called"] = True
            return mock_scheduler

        monkeypatch.setattr(
            "evo_flywheel.scheduler.jobs.schedule_daily_collection", mock_schedule_daily
        )
        monkeypatch.setattr("sys.argv", ["evo-fetch", "--schedule"])
        monkeypatch.setattr("time.sleep", mock_sleep_side_effect)

        # Act & Assert
        # 不应该抛出异常，应该优雅关闭
        with contextlib.suppress(KeyboardInterrupt):
            main()

        # 验证调度器配置被调用
        assert call_count["schedule_called"]
        mock_scheduler.start.assert_called_once()
        mock_scheduler.shutdown.assert_called_once()
