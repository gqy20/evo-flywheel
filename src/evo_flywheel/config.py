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
    database_path: str = Field(
        default="./data/evo_flywheel.db",
        description="SQLite 数据库路径（兼容配置）",
    )

    # Chroma 配置
    chroma_persist_dir: str = Field(
        default="./chroma_db",
        description="Chroma 向量数据库持久化目录",
    )

    # LLM API 配置 (OpenAI 兼容)
    openai_api_key: str = Field(
        default="",
        description="OpenAI 兼容 API 密钥（智谱/通义等）",
    )
    openai_base_url: str = Field(
        default="",
        description="OpenAI 兼容 API Base URL",
    )

    # 日志配置
    log_level: str = Field(
        default="INFO",
        description="日志级别",
    )
    log_file: str = Field(
        default="logs/evo_flywheel.log",
        description="日志文件路径",
    )
    log_max_bytes: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="日志文件最大大小（字节）",
    )
    log_backup_count: int = Field(
        default=5,
        description="保留的日志备份文件数量",
    )
    log_json_format: bool = Field(
        default=False,
        description="是否使用 JSON 格式日志",
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

    # Embedding API 配置
    embedding_api_url: str = Field(
        default="https://api.openai.com/v1",
        description="Embedding API Base URL（不含 /embeddings 路径）",
    )
    embedding_api_key: str = Field(
        default="",
        description="Embedding API 密钥",
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding 模型名称",
    )
    embedding_dimension: int = Field(
        default=1536,
        description="Embedding 向量维度",
    )

    @property
    def effective_database_url(self) -> str:
        """获取有效的数据库 URL

        优先使用 database_path（如果配置了且文件存在），否则使用 database_url

        Returns:
            str: 数据库连接 URL
        """
        from pathlib import Path

        # 优先使用 database_path
        if self.database_path:
            path = self.database_path
            # 如果不是 sqlite:/// 格式，需要转换
            if not path.startswith("sqlite:///") and not path.startswith("sqlite://"):
                if (
                    Path(path).exists()
                    or path.startswith("./")
                    or path.startswith("/")
                    or path.startswith("..")
                ):
                    # 文件路径或相对路径
                    return f"sqlite:///{path.lstrip('/')}"
                # 其他情况当作原始 URL
                return path
            return path
        return self.database_url

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
        Path(settings.log_file).parent,  # logs 目录
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
