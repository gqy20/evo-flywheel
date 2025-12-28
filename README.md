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
前端:     Streamlit
后端:     FastAPI
数据库:   SQLite + Chroma (向量)
嵌入:     sentence-transformers (all-MiniLM-L6-v2)
分析:     智谱 GLM-4.7
调度:     APScheduler
检查:     ruff (lint + format)
包管理:    uv
```

## 开发状态

> 🚧 项目处于规划阶段，尚未开始编码

当前版本: v0.0-planning

预计 2-3 周完成 MVP

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/gqy20/evo-flywheel.git
cd evo-flywheel

# 使用 uv 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 ZHIPU_API_KEY (智谱AI API密钥)

# 初始化数据库
python -m src.evo_flywheel.db.init

# 启动 Web 界面
streamlit run src/evo_flywheel/web/app.py
```

## 项目结构 (src layout)

```
evo-flywheel/
├── src/evo_flywheel/    # 源代码包
│   ├── api/             # FastAPI endpoints
│   ├── db/              # SQLite models & CRUD
│   ├── vector/          # Chroma integration
│   ├── collectors/      # RSS/API collection
│   ├── analyzers/       # GLM-4.7 LLM analysis
│   ├── reporters/       # Report generation
│   ├── scheduler/       # APScheduler jobs
│   └── web/             # Streamlit UI
├── tests/               # 测试 (unit/integration)
├── config/              # 配置文件
│   └── sources.yaml     # RSS sources
├── docs/                # 设计文档
├── data/                # 数据文件
├── reports/             # 每日报告
├── chroma_db/           # 向量数据库
├── pyproject.toml       # 项目配置
└── .env.example         # 环境变量模板
```

## 文档

- [产品需求文档 (PRD)](docs/PRD.md) - 完整的功能规格和技术设计
- [开发路线图](docs/ROADMAP.md) - 6 阶段开发计划
- [RSS 期刊源配置](docs/rss.md) - 30+ 进化生物学期刊列表

## 成本估算

月度运营成本约 **¥15-20** (约 $2-3)：
- LLM 分析: ~¥5/月 (30 篇/天 × ¥0.005/篇)
- 服务器: ¥10-15/月 ($2-3/月)
- 其他: 免费 (本地嵌入和数据库)

## 许可证

MIT License

---

**文档更新**: 2025-12-28
