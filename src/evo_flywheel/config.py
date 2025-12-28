"""配置管理模块

从环境变量和配置文件加载设置
"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置

    从环境变量和 .env 文件加载配置
    """

    # 数据库配置
    database_url: str = Field(
        default="sqlite:///evo_flywheel.db",
        description="SQLite 数据库路径",
    )

    # Chroma 配置
    chroma_persist_dir: str = Field(
        default="./chroma_db",
        description="Chroma 向量数据库持久化目录",
    )

    # LLM API 配置
    zhipu_api_key: str = Field(
        default="",
        description="智谱 AI API 密钥",
    )

    # 日志配置
    log_level: str = Field(
        default="INFO",
        description="日志级别",
    )

    # RSS 配置
    rss_sources_path: str = Field(
        default="config/sources.yaml",
        description="RSS 源配置文件路径",
    )

    # 报告配置
    reports_dir: str = Field(
        default="reports",
        description="报告输出目录",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# 全局配置实例
_settings: Settings | None = None


def get_settings() -> Settings:
    """获取配置单例实例

    Returns:
        Settings: 配置实例
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_project_root() -> Path:
    """获取项目根目录

    Returns:
        Path: 项目根目录路径
    """
    return Path(__file__).parent.parent.parent


def ensure_directories() -> None:
    """确保必要的目录存在"""
    settings = get_settings()
    directories = [
        Path(settings.reports_dir),
        Path(settings.chroma_persist_dir),
        Path(settings.rss_sources_path).parent,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
