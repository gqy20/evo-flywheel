# Evo-Flywheel

> 进化生物学学术飞轮 - AI 驱动的文献分析与报告系统

自动采集最新进化生物学研究论文，智能提取关键发现，生成每日研究动态报告，并提供语义搜索功能。

## 核心功能

- **自动采集** - 从 30+ 期刊 RSS 源和 bioRxiv API 自动获取最新论文
- **智能分析** - 使用 LLM 提取研究物种、进化机制、关键发现和重要性评分
- **每日报告** - 生成格式化的 Markdown 研究动态
- **语义搜索** - 基于向量嵌入的自然语言文献检索
- **Web 界面** - Streamlit 构建的简洁交互界面

## 技术栈

```
前端:       Streamlit
后端:       FastAPI
数据库:     SQLite + Chroma (向量)
嵌入服务:   远程 Embedding API (OpenAI 兼容)
分析:       智谱 GLM-4.7
调度:       APScheduler
代码检查:   ruff (lint + format) + mypy (类型)
包管理:     uv
测试:       pytest + pytest-playwright
```

## 开发状态

> 已完成 Milestone 1-2，正在开发 Milestone 3

| 里程碑 | 版本 | 状态 | 内容 |
|--------|------|------|------|
| M1 | v0.1.0 | ✅ | 基础设施 (数据库、向量库、CRUD、测试) |
| M2 | v0.2.0 | ✅ | 数据采集层 (RSS、bioRxiv API、去重、编排器、调度器) |
| M3 | v0.3.0 | 🔄 | LLM 分析层 (论文分析、批量处理) |
| M4 | v0.4.0 | ⏳ | 搜索层 (嵌入、语义搜索、混合搜索) |
| M5 | v0.5.0 | ⏳ | Web 界面 (Streamlit) |
| M6 | v0.6.0 | ⏳ | 测试优化与部署 |

当前版本: v0.2.0

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/gqy20/evo-flywheel.git
cd evo-flywheel

# 使用 uv 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# 安装 pre-commit hooks (TDD 必备)
pre-commit install

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入以下配置:
# - OPENAI_API_KEY: 智谱AI或其他兼容API密钥
# - OPENAI_BASE_URL: API Base URL
# - EMBEDDING_API_KEY: Embedding API 密钥 (可选)
# - EMBEDDING_API_URL: Embedding API URL (可选)

# 初始化数据库 (使用 CLI 工具)
evo-init

# 数据采集 (单次执行)
evo-fetch

# 启动定时调度器 (每日 9:00 自动采集)
evo-fetch --schedule

# 启动 Web 界面
streamlit run src/evo_flywheel/web/app.py
```

## CLI 工具

```bash
# 数据库初始化
evo-init                    # 创建 SQLite 数据库和表结构

# 数据采集
evo-fetch                   # 执行一次采集 (默认最近7天)
evo-fetch --days 3          # 采集最近3天的论文
evo-fetch --schedule        # 启动定时调度器
evo-fetch --sources arxiv   # 只采集指定源
```

## 项目结构 (src layout)

```
evo-flywheel/
├── src/
│   └── evo_flywheel/         # 主包目录
│       ├── __init__.py
│       ├── config.py         # 配置管理 (pydantic-settings)
│       ├── logging.py        # 日志配置 (轮转 + JSON)
│       ├── api/              # FastAPI endpoints (待开发)
│       ├── db/               # SQLite models and operations ✅
│       │   ├── models.py      # SQLAlchemy models
│       │   ├── crud.py        # CRUD operations
│       │   └── init.py        # 数据库初始化脚本
│       ├── vector/           # Chroma integration ✅
│       │   └── client.py      # Chroma PersistentClient
│       ├── collectors/       # RSS/API data collection ✅
│       │   ├── rss.py         # RSS feed parser
│       │   ├── biorxiv.py     # bioRxiv API client
│       │   ├── dedup.py       # Deduplication logic
│       │   └── orchestrator.py # Multi-source coordinator
│       ├── scheduler/        # APScheduler tasks ✅
│       │   └── jobs.py        # Daily collection jobs
│       ├── analyzers/        # LLM paper analysis 🔄
│       ├── reporters/        # Daily report generation (待开发)
│       └── web/              # Streamlit UI ✅
│           ├── app.py         # Streamlit 应用入口
│           └── pages/         # 页面模块
│               ├── home.py
│               ├── list.py
│               ├── search.py
│               └── report.py
├── tests/
│   ├── conftest.py           # pytest fixtures ✅
│   ├── unit/                 # 单元测试 ✅
│   └── e2e/                  # E2E 测试 ✅
├── config/
│   └── sources.yaml          # RSS source configurations ✅
├── data/                     # Generated data files
├── reports/                  # Daily markdown reports
├── logs/                     # Log files with rotation
├── chroma_db/                # Vector database storage
├── pyproject.toml            # 项目配置 (uv) ✅
├── .env.example              # 环境变量模板 ✅
├── .gitignore
├── .pre-commit-config.yaml    # Pre-commit hooks ✅
├── README.md
├── CLAUDE.md                 # Claude Code 开发指南
└── docs/                     # 设计文档
    ├── PRD.md                # 产品需求文档
    ├── ROADMAP.md            # 开发路线图
    └── rss.md                # RSS 期刊源配置
```

## 开发命令

```bash
# 代码检查和格式化 (ruff)
ruff check .                    # 检查代码
ruff check . --fix              # 检查并自动修复
ruff format .                   # 格式化代码

# 类型检查
mypy src/evo_flywheel           # 类型检查

# 手动运行 pre-commit
pre-commit run --all-files      # 检查所有文件

# 运行测试
pytest                          # 运行所有测试
pytest tests/unit/              # 只运行单元测试
pytest tests/e2e/               # 只运行 E2E 测试
pytest -v                       # 详细输出
pytest --cov=src/evo_flywheel   # 测试覆盖率
```

## 文档

- [产品需求文档 (PRD)](docs/PRD.md) - 完整的功能规格和技术设计
- [开发路线图](docs/ROADMAP.md) - 6 阶段开发计划
- [RSS 期刊源配置](docs/rss.md) - 30+ 进化生物学期刊列表
- [Claude Code 开发指南](CLAUDE.md) - AI 辅助开发说明

## 成本估算

月度运营成本约 **¥15-20** (约 $2-3)：
- LLM 分析: ~¥5/月 (30 篇/天 × ¥0.005/篇)
- Embedding: ~¥2/月 (远程 API 调用)
- 服务器: ¥10-15/月 ($2-3/月)
- 数据库: 免费 (SQLite + Chroma 本地)

## 许可证

MIT License

---

**文档更新**: 2025-12-28
