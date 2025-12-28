"""数据库初始化脚本

创建数据库表和索引
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from sqlalchemy import Index, create_engine

from evo_flywheel.config import get_settings
from evo_flywheel.db.models import Base, Paper


def init_database(drop_all: bool = False) -> None:
    """初始化数据库

    Args:
        drop_all: 是否删除所有表后重新创建（谨慎使用）
    """
    settings = get_settings()

    # 从 DATABASE_URL 中提取文件路径
    # 格式: sqlite:///path/to/db.db
    db_url = settings.database_url
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        # 确保数据目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    # 创建引擎
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
        echo=False,
    )

    # 删除所有表（可选）
    if drop_all:
        print("⚠️  删除所有表...")
        Base.metadata.drop_all(engine)

    # 创建所有表
    print("📦 创建数据库表...")
    Base.metadata.create_all(engine)

    # 创建额外的索引
    print("📇 创建索引...")
    create_indexes(engine)

    print(f"✅ 数据库初始化完成: {db_url}")


def create_indexes(engine) -> None:
    """创建额外的索引

    Args:
        engine: SQLAlchemy 引擎
    """
    # papers 表索引
    Index("idx_papers_date", Paper.publication_date).create(engine, checkfirst=True)
    Index("idx_papers_score", Paper.importance_score).create(engine, checkfirst=True)
    Index("idx_papers_source", Paper.source).create(engine, checkfirst=True)

    print("  - papers: publication_date, importance_score, source")


def main() -> None:
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="初始化 Evo-Flywheel 数据库")
    parser.add_argument("--drop", action="store_true", help="删除所有表后重新创建（谨慎使用）")
    args = parser.parse_args()

    if args.drop:
        confirm = input("⚠️  确认要删除所有表吗？这将清空所有数据！[yes/N]: ")
        if confirm.lower() != "yes":
            print("❌ 取消操作")
            return

    init_database(drop_all=args.drop)


if __name__ == "__main__":
    main()
