"""配置管理单元测试"""

import os

from evo_flywheel.config import Settings, ensure_directories, get_project_root, get_settings


class TestSettings:
    """Settings 配置类测试"""

    def test_settings_default_values_no_env(self):
        """测试配置默认值（不读取 .env 文件）"""
        # Arrange & Act - 使用 _env_file=None 禁用 .env 文件读取
        settings = Settings(_env_file=None)

        # Assert
        assert settings.database_url == "sqlite:///evo_flywheel.db"
        assert settings.chroma_persist_dir == "./chroma_db"
        assert settings.log_level == "INFO"
        assert settings.reports_dir == "reports"

    def test_settings_from_env(self, monkeypatch):
        """测试从环境变量加载配置"""
        # Arrange
        monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("ZHIPU_API_KEY", "test-key-123")

        # Act
        settings = Settings(_env_file=None)

        # Assert
        assert settings.database_url == "sqlite:///test.db"
        assert settings.log_level == "DEBUG"
        assert settings.zhipu_api_key == "test-key-123"

    def test_settings_from_env_file(self, tmp_path):
        """测试从 .env 文件加载配置"""
        # Arrange
        env_file = tmp_path / ".env"
        env_file.write_text("DATABASE_URL=sqlite:///env_test.db\nLOG_LEVEL=WARNING\n")

        # Act
        settings = Settings(_env_file=str(env_file))

        # Assert
        assert settings.database_url == "sqlite:///env_test.db"
        assert settings.log_level == "WARNING"


class TestGetSettings:
    """get_settings 函数测试"""

    def test_get_settings_returns_singleton(self, monkeypatch):
        """测试 get_settings 返回单例"""
        # Arrange - 需要清除已缓存的实例
        import evo_flywheel.config as config_module

        config_module._settings = None

        monkeypatch.setenv("DATABASE_URL", "sqlite:///singleton.db")

        # Act
        settings1 = get_settings()
        settings2 = get_settings()

        # Assert
        assert settings1 is settings2
        assert settings1.database_url == "sqlite:///singleton.db"

        # Cleanup
        config_module._settings = None

    def test_get_settings_caches_instance(self, monkeypatch):
        """测试 get_settings 缓存配置实例"""
        # Arrange - 清除缓存
        import evo_flywheel.config as config_module

        config_module._settings = None

        monkeypatch.setenv("LOG_LEVEL", "ERROR")
        settings = get_settings()

        # 改变环境变量
        monkeypatch.setenv("LOG_LEVEL", "CRITICAL")

        # Act
        get_settings()

        # Assert - 应该返回缓存的实例
        assert settings.log_level == "ERROR"

        # Cleanup
        config_module._settings = None


class TestGetProjectRoot:
    """get_project_root 函数测试"""

    def test_get_project_root_returns_path(self):
        """测试返回项目根目录路径"""
        # Act
        root = get_project_root()

        # Assert
        assert isinstance(root, os.PathLike | str)
        assert str(root).endswith("evo-flywheel")

    def test_get_project_root_contains_src(self):
        """测试项目根目录包含 src 目录"""
        # Act
        root = get_project_root()

        # Assert
        src_dir = root / "src"
        assert src_dir.exists()


class TestEnsureDirectories:
    """ensure_directories 函数测试"""

    def test_ensure_directories_creates_missing_dirs(self, tmp_path, monkeypatch):
        """测试创建缺失的目录"""
        # Arrange
        reports_dir = tmp_path / "reports"
        chroma_dir = tmp_path / "chroma_db"
        config_dir = tmp_path / "config"

        # 清除配置缓存
        import evo_flywheel.config as config_module

        config_module._settings = None

        monkeypatch.setenv("REPORTS_DIR", str(reports_dir))
        monkeypatch.setenv("CHROMA_PERSIST_DIR", str(chroma_dir))
        monkeypatch.setenv("RSS_SOURCES_PATH", str(config_dir / "sources.yaml"))

        # Act
        ensure_directories()

        # Assert
        assert reports_dir.exists()
        assert chroma_dir.exists()
        assert config_dir.exists()

        # Cleanup
        config_module._settings = None

    def test_ensure_directories_idempotent(self, tmp_path, monkeypatch):
        """测试多次调用不会出错"""
        # Arrange
        reports_dir = tmp_path / "reports"

        # 清除配置缓存
        import evo_flywheel.config as config_module

        config_module._settings = None

        monkeypatch.setenv("REPORTS_DIR", str(reports_dir))

        # Act & Assert - 两次调用不应出错
        ensure_directories()
        ensure_directories()
        assert reports_dir.exists()

        # Cleanup
        config_module._settings = None
