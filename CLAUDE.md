# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Evo-Flywheel (进化生物学学术飞轮)** is an AI-driven academic literature analysis system for evolutionary biology researchers. The system automatically collects the latest research papers from multiple sources, intelligently extracts key findings using LLMs, generates daily research reports, and provides semantic search capabilities.

### Current Status

**里程碑 1-9 (v0.1.0 - v0.1.8) 已完成** ✅
- ✅ 项目初始化 (uv + ruff + pre-commit)
- ✅ 数据库模型 (SQLite + Chroma)
- ✅ CRUD 操作模块
- ✅ 单元测试框架
- ✅ RSS 采集器 (feedparser)
- ✅ bioRxiv API 采集器
- ✅ 数据去重模块 (DOI + title)
- ✅ 采集编排器 (orchestrator)
- ✅ 定时调度器 (APScheduler)
- ✅ CLI 工具 (evo-fetch, evo-init, evo-analyze)
- ✅ LLM 分析模块 (GLM-4.7)
- ✅ 向量嵌入和语义搜索
- ✅ FastAPI REST API
- ✅ Streamlit Web 界面
- ✅ 飞轮自动化 (4小时间隔)
- ✅ 深度报告生成

**当前版本**: v0.1.8

---

## Architecture Overview

### Dual Database Architecture

The system uses two complementary databases:

1. **SQLite** (`evo_flywheel.db`) - Structured data
   - Paper metadata (title, authors, abstract, DOI, journal, source)
   - AI analysis results (importance score, key findings, evolutionary mechanisms)
   - Daily reports, user feedback
   - RSS source configurations

2. **Chroma** (`chroma_db/`) - Vector embeddings
   - Semantic search for paper abstracts
   - Similar paper recommendations
   - Query embeddings for natural language search

Both databases are linked via `paper_id`. Chroma uses the same ID as SQLite for consistency.

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | FastAPI | REST API with auto-documentation |
| Frontend | Streamlit | Quick web interface without frontend expertise |
| Structured Data | SQLite | Zero-config single-file database |
| Vector Data | Chroma | Embedded vector database (PersistentClient) |
| Embeddings | 远程 API | 使用远程 embedding 服务 (非本地模型) |
| LLM | 智谱 GLM-4.7 | Paper analysis (¥0.5/1M input, ¥2/1M output) |
| Scheduler | APScheduler | Daily automated tasks |
| RSS Parsing | feedparser | RSS feed parsing |
| Linting | ruff | Fast Python linter & formatter |
| Package Manager | uv | Fast Python package installer |
| Testing | pytest | Unit testing framework |

### Project Structure (src layout)

```
evo-flywheel/
├── src/
│   └── evo_flywheel/         # 主包目录
│       ├── __init__.py
│       ├── config.py         # 配置管理 (pydantic-settings)
│       ├── logging.py        # 日志配置
│       ├── api/              # FastAPI endpoints ✅
│       │   ├── deps.py       # 依赖注入
│       │   ├── schemas.py    # Pydantic 模型
│       │   ├── main.py       # API 入口
│       │   └── v1/           # API v1 路由
│       ├── db/               # SQLite models and operations ✅
│       │   ├── models.py      # SQLAlchemy models
│       │   ├── crud.py        # CRUD operations
│       │   └── init.py        # 数据库初始化脚本
│       ├── vector/           # Chroma integration ✅
│       │   ├── client.py      # Chroma PersistentClient
│       │   ├── embeddings.py  # Embedding 服务
│       │   ├── storage.py     # 向量存储
│       │   ├── search.py      # 语义搜索
│       │   └── hybrid.py      # 混合搜索
│       ├── collectors/       # RSS/API data collection ✅
│       │   ├── rss.py         # RSS feed parser
│       │   ├── biorxiv.py     # bioRxiv API client
│       │   ├── dedup.py       # Deduplication logic
│       │   └── orchestrator.py # Multi-source coordinator
│       ├── scheduler/        # APScheduler tasks ✅
│       │   ├── jobs.py        # Daily collection jobs
│       │   └── analysis.py    # Analysis scheduling
│       ├── analyzers/        # LLM paper analysis ✅
│       │   ├── prompts.py     # Prompt 模板
│       │   ├── llm.py         # GLM-4.7 封装
│       │   └── batch.py       # 批量处理
│       ├── reporters/        # Daily report generation ✅
│       │   └── generator.py   # 报告生成器
│       └── web/              # Streamlit UI ✅
│           ├── app.py         # Streamlit 应用入口
│           ├── api_client.py  # API 客户端
│           └── views/         # 页面视图
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # pytest fixtures ✅
│   ├── unit/                 # 单元测试 ✅
│   │   ├── test_config.py
│   │   ├── test_db_models.py
│   │   ├── test_db_crud.py
│   │   └── test_vector_client.py
│   └── integration/          # 集成测试 (待开发)
├── config/
│   └── sources.yaml          # RSS source configurations ✅
├── data/                     # Generated data files
├── reports/                  # Daily markdown reports
├── chroma_db/                # Vector database storage
├── pyproject.toml            # 项目配置 (uv) ✅
├── .env.example              # 环境变量模板 ✅
├── .gitignore
├── .pre-commit-config.yaml    # Pre-commit hooks ✅
├── README.md
└── CLAUDE.md
```

**为什么使用 src layout:**
- ✅ 避免测试时的隐式导入问题
- ✅ 更清晰的包边界
- ✅ 更容易打包和发布
- ✅ Python 官方推荐结构

### Development Commands (src layout + ruff + uv)

```bash
# 使用 uv 管理环境
uv venv                          # 创建虚拟环境 (Python 3.13)
source .venv/bin/activate         # 激活环境 (Windows: .venv\Scripts\activate)
uv pip install -e ".[dev]"       # 安装项目（开发模式，含所有依赖）

# 安装 pre-commit hooks (首次运行)
pre-commit install                # 安装 Git hooks

# 初始化数据库
evo-init                        # 使用 CLI 工具
# 或
uv run python -m src.evo_flywheel.db.init

# 数据采集
evo-fetch                       # 执行一次采集 (默认最近7天)
evo-fetch --schedule            # 启动定时调度器 (每日 9:00)

# 论文分析
evo-analyze                     # 分析未分析的论文 (默认 10 篇)
evo-analyze --limit 50          # 分析 50 篇论文

# 启动服务器
./start.sh                      # 同时启动 API 和 Web 界面
# 或分别启动:
uvicorn evo_flywheel.api.main:app --reload  # FastAPI (端口 8000)
streamlit run src/evo_flywheel/web/app.py   # Streamlit (端口 8501)

# 代码检查和格式化 (ruff)
ruff check .                    # 检查代码
ruff check . --fix              # 检查并自动修复
ruff format .                   # 格式化代码

# 手动运行 pre-commit
pre-commit run --all-files      # 检查所有文件

# 运行测试
pytest                          # 运行所有测试
pytest tests/unit/              # 只运行单元测试
pytest tests/api/               # 只运行 API 测试
pytest -v                       # 详细输出
pytest --cov=src/evo_flywheel   # 测试覆盖率
pytest -k "test_papers"         # 运行匹配名称的测试
pytest tests/api/test_papers.py::test_get_papers -v  # 运行单个测试
```

**为什么使用 uv:**
- ✅ 比 pip 快 10-100 倍
- ✅ 统一的依赖解析
- ✅ 更好的锁文件支持
- ✅ 现代化的 Python 工具链

**Pre-commit Hooks:**
- 自动运行 ruff lint 和 format
- 检查 YAML/TOML 语法
- 安全检查 (bandit)
- 跳过 hook: `git commit --no-verify`

---

## Data Flow

```
1. Collection (Daily 09:00)
   RSS feeds + bioRxiv API
   → Deduplication (DOI/title)
   → Metadata extraction
   → Store in SQLite

2. Analysis
   New papers from SQLite
   → LLM (GLM-4.7) analysis
   → Extract: taxa, scale, method, findings, mechanism, score
   → Update SQLite

3. Vectorization
   New papers
   → Generate embeddings (远程 API)
   → Store in Chroma with metadata

4. Search (On-demand)
   User query
   → Query embedding (远程 API)
   → Chroma similarity search
   → Hybrid: SQLite filters + Chroma ranking

5. Reporting
   Daily aggregation
   → Top papers by score
   → Markdown report template
   → Save to reports/
```

---

## Key Configuration Files

### RSS Sources (`config/sources.yaml`)

The system supports 30+ evolutionary biology journals. See `docs/rss.md` for the complete list. The MVP minimum is 7 sources:

**MVP Configuration:**
- arXiv q-bio.PE (Populations & Evolution)
- bioRxiv API (evolutionary_biology category)
- PLOS Computational Biology
- Methods in Ecology & Evolution
- Molecular Ecology
- Nature
- PLOS Biology

### Environment Variables (`.env`)

```bash
# LLM API (OpenAI 兼容，用于智谱/通义等)
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4  # 智谱 GLM

# Embedding API (用于语义搜索)
EMBEDDING_API_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=your-embedding-api-key
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# Database
DATABASE_URL=sqlite:///data/evo_flywheel.db
CHROMA_PERSIST_DIR=./chroma_db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/evo_flywheel.log
```

---

## LLM Analysis Schema

The system uses a structured prompt to extract evolutionary biology insights:

```python
ANALYSIS_SCHEMA = {
    "基础信息": {
        "研究物种": "Involved taxa/classification",
        "进化尺度": "Molecular/Individual/Population/Species",
        "研究方法": "Phylogenetic/Population Genetic/Experimental/Comparative"
    },
    "核心内容": {
        "关键发现": "3-5 key findings",
        "进化机制": "Natural selection/Genetic drift/Gene flow/Mutation",
        "创新性": "Theoretical/Methodological/Discovery innovation"
    },
    "价值评估": {
        "重要性评分": "0-100 score",
        "推荐理由": "1-2 sentences explaining value"
    }
}
```

---

## API Endpoints

The FastAPI runs on `http://localhost:8000` with interactive docs at `/api/v1/docs`.

**Key Routes** (all under `/api/v1/`):
- `GET /papers` - List papers with pagination and filters
- `GET /papers/{id}` - Get paper details
- `POST /papers/{id}/analyze` - Analyze a paper with LLM
- `GET /search/semantic` - Semantic search by query
- `POST /search/similar` - Find similar papers
- `GET /search/hybrid` - Hybrid search (semantic + filters)
- `GET /reports/today` - Get today's report
- `POST /collection/fetch` - Trigger data collection
- `POST /analysis/trigger` - Trigger batch analysis
- `POST /embeddings/rebuild` - Rebuild vector index
- `GET /stats/overview` - System statistics

See `docs/api.md` for complete API documentation.

---

## Development Phases

See `docs/ROADMAP.md` for detailed 6-phase development plan (2-3 weeks MVP):

1. **Phase 0**: Project initialization (0.5d) ✅ 完成
2. **Phase 1**: Data layer - SQLite + Chroma setup (2d) ✅ 完成
3. **Phase 2**: Collection layer - RSS + bioRxiv API (2d) ✅ 完成
4. **Phase 3**: Analysis layer - LLM integration (2d) ✅ 完成
5. **Phase 4**: Search layer - Embeddings + semantic search (1.5d) ✅ 完成
6. **Phase 5**: Presentation layer - Streamlit UI (3d) ✅ 完成
7. **Phase 6**: Testing & optimization (2d) 🔄 进行中

### Completed Milestones

**v0.1.0 - 基础设施** ✅
- 项目初始化 (uv + ruff + pre-commit)
- 数据库Schema设计 (SQLite + Chroma)
- 单元测试框架

**v0.1.1 - 数据采集层** ✅
- RSS feed parser with advanced DOI extraction
- bioRxiv API client (avoiding Cloudflare)
- Cross-source deduplication (DOI + title normalization)
- Multi-source orchestrator with graceful error handling
- APScheduler with CLI entry points (`evo-fetch`, `evo-init`)

**v0.1.2 - LLM 分析层** ✅
- LLM paper analysis (GLM-4.7 via OpenAI-compatible API)
- Structured prompts for evolutionary biology insights
- Batch analysis with progress tracking

**v0.1.3 - 搜索层** ✅
- Vector embeddings (remote API)
- Semantic search with Chroma
- Hybrid search (metadata filters + semantic ranking)

**v0.1.4 - Web 界面** ✅
- Streamlit web interface with multiple views
- Home page with statistics and recommendations
- Paper list, search, and detail views

**v0.1.5 - 测试优化与部署** ✅
- Enhanced testing coverage
- Performance optimization
- Bug fixes and refinements

**v0.1.6 - FastAPI 后端** ✅
- REST API with comprehensive endpoints
- OpenAPI documentation (Swagger/ReDoc)
- Unified error handling

**v0.1.7 - Web UI 后端集成** ✅
- APIClient for backend communication
- Paper detail page with feedback
- Integrated search and reporting

**v0.1.8 - 飞轮控制** ✅
- Automated flywheel (4-hour interval)
- Deep report generation with LLM
- Multiple reports per day support

---

## Performance Targets

| Operation | Target |
|-----------|--------|
| RSS collection | < 2 minutes |
| Single paper analysis | < 10 seconds |
| Batch analysis (30 papers) | < 5 minutes |
| Semantic search | < 1 second |
| Report generation | < 30 seconds |
| UI page load | < 3 seconds |

---

## Important Implementation Details

### Configuration Access Pattern

Always use `get_settings()` to access configuration, never instantiate `Settings` directly:

```python
from evo_flywheel.config import get_settings

settings = get_settings()
api_key = settings.openai_api_key
```

The `database_url` vs `database_path` logic is handled by `settings.effective_database_url` property.

### Database Session Pattern

Use the `get_db()` dependency for FastAPI endpoints. For scripts, use `SessionLocal()` context manager:

```python
from evo_flywheel.db import SessionLocal

with SessionLocal() as db:
    papers = get_papers(db, limit=10)
```

### DOI Extraction and Normalization

The RSS collector uses advanced regex patterns in `collectors/rss.py` to extract DOIs from various formats. DOIs are normalized (lowercased, whitespace stripped) before storage. The deduplication logic in `collectors/dedup.py` checks both DOI and title similarity.

### LLM API Integration

The project uses OpenAI-compatible API (not just OpenAI). Configure via `OPENAI_BASE_URL` for providers like Zhipu (智谱 GLM). The `analyzers/llm.py` module wraps the OpenAI client with retry logic and structured JSON response parsing.

### Vector Storage Linking

Chroma collection uses the same `paper_id` as SQLite for consistency. When storing embeddings, always include metadata (title, source, taxa) for hybrid search filtering.

### Error Handling in Collectors

Each collector (RSS, bioRxiv API) should handle errors gracefully. The orchestrator continues even if one source fails. Check logs for individual source errors.

---

## Chroma PersistentClient (新版 API)

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("evolutionary_papers")
```

**注意**: 不再使用旧的 `Settings(chroma_db_impl="duckdb+parquet")` API。

### Remote Embedding API

使用远程 embedding 服务（非本地模型），需在环境变量中配置：
- `EMBEDDING_API_URL`: Embedding API 端点
- `EMBEDDING_API_KEY`: API 密钥
- `EMBEDDING_MODEL`: 模型名称

### bioRxiv API vs RSS

Use the **bioRxiv API** instead of RSS:
- RSS is protected by Cloudflare (requires JavaScript rendering)
- API returns structured JSON, supports date range and category filtering
- Endpoint: `https://api.biorxiv.org/details/biorxiv/{start}/{end}?category=evolutionary_biology`

### Hybrid Search Pattern

1. Use SQLite to filter by metadata (taxa, min_score, journal)
2. Use Chroma to rank by semantic similarity
3. Merge and return top-k results

---

## Reference Documentation

- `docs/PRD.md` - Complete product requirements (v1.2)
- `docs/ROADMAP.md` - Development roadmap with task breakdown
- `docs/rss.md` - 30+ evolutionary biology journal RSS sources
