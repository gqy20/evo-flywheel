# 进化生物学学术飞轮系统 MVP 产品需求文档 (PRD)

> **项目名称**: Evo-Flywheel (进化生物学学术飞轮)
> **版本**: v1.1
> **更新日期**: 2025-12-28
> **目标**: 2-3周完成MVP
> **更新内容**: 新增Chroma向量数据库 + 语义搜索功能

---

## 1. 产品概述

### 1.1 产品定位
一个面向进化生物学研究者的AI驱动文献分析系统，自动采集最新研究论文，智能提取关键信息，生成每日研究动态报告。

### 1.2 核心价值
- **效率**: 每天自动筛选数十篇论文，节省90%文献筛选时间
- **洞察**: AI提取关键发现、进化机制、研究方法
- **聚焦**: 专注进化生物学领域，精准度高
- **进化**: 用户反馈驱动系统持续优化

### 1.3 目标用户
- 进化生物学研究生/博士后
- 生态进化领域研究人员
- 需要跟踪前沿的科研工作者

### 1.4 MVP目标
**2-3周内完成可演示的核心功能，验证产品价值**

---

## 2. 功能需求

### 2.1 功能清单

| 功能 | 优先级 | 描述 |
|------|--------|------|
| F1: 文献自动采集 | P0 | 从多个RSS源 + API获取论文 |
| F2: 智能文献分析 | P0 | LLM提取关键信息 |
| F3: 每日报告生成 | P0 | 生成Markdown格式报告 |
| F4: 语义相似搜索 | P0 | 基于embedding的文献检索 |
| F5: Web界面 | P0 | Streamlit展示 |
| F6: 用户反馈 | P1 | 收集评分和建议 |

### 2.2 F1: 文献自动采集

**数据源配置**:
```yaml
sources:
  # 预印本 (API方式)
  biorxiv_api:
    type: api
    url: https://api.biorxiv.org/details/biorxiv/{start}/{end}
    params: {category: evolutionary_biology}
    priority: 1

  arxiv_pe:
    type: rss
    url: https://export.arxiv.org/rss/q-bio.PE
    priority: 2

  # 核心期刊
  plos_compbio:
    type: rss
    url: https://journals.plos.org/ploscompbiol/feed/atom
    priority: 3

  methods_eecol:
    type: rss
    url: https://besjournals.onlinelibrary.wiley.com/rss/journal/2041210X
    priority: 4

  mol_ecology:
    type: rss
    url: https://onlinelibrary.wiley.com/rss/journal/1365294X
    priority: 5

  evolution:
    type: rss
    url: https://academic.oup.com/evolut/rss
    priority: 6

  plos_biology:
    type: rss
    url: https://journals.plos.org/plosbiology/feed/atom
    priority: 7

  nature:
    type: rss
    url: https://www.nature.com/nature.rss
    priority: 8
```

**采集流程**:
```
定时任务(每天09:00)
  → 逐个源获取数据
  → 去重(基于DOI/标题)
  → 提取元数据
  → 存入数据库
```

**验收标准**:
- 支持8个以上数据源
- 去重准确率>99%
- 单次采集<2分钟

---

### 2.3 F2: 智能文献分析

**分析维度**:
```python
ANALYSIS_SCHEMA = {
    "基础信息": {
        "研究物种": "涉及的分类群",
        "进化尺度": "分子/个体/群体/物种",
        "研究方法": "系统发育/群体遗传/实验/比较"
    },

    "核心内容": {
        "关键发现": "3-5条主要结论",
        "进化机制": "自然选择/遗传漂变/基因流/突变",
        "创新性": "理论/方法/发现创新"
    },

    "价值评估": {
        "重要性评分": "0-100分",
        "推荐理由": "1-2句话说明价值"
    }
}
```

**Prompt模板**:
```python
EVOLUTION_ANALYSIS_PROMPT = """
你是进化生物学专家。请分析以下论文：

标题: {title}
摘要: {abstract}

请提取：
1. 研究物种/分类群:
2. 进化尺度: (分子/个体/群体/物种)
3. 研究方法: (系统发育分析/群体遗传/实验进化等)
4. 关键发现: (3-5条)
5. 进化机制: (自然选择/漂变/基因流等)
6. 重要性评分: (0-100，综合考虑创新性、影响力)
7. 推荐理由: (1-2句话)

请简洁专业。
"""
```

**验收标准**:
- 单篇分析<10秒
- 关键发现准确率>70%
- API成本<$0.1/篇

---

### 2.4 F4: 语义相似搜索

**搜索能力**:
```python
# 支持的搜索类型
SEMANTIC_SEARCH = {
    "摘要语义搜索": "基于论文摘要的向量相似度",
    "关键词扩展": "找到相似概念的相关论文",
    "相关研究推荐": "给定一篇论文，推荐相似研究",
    "跨语言检索": "支持中英文查询"
}
```

**Embedding模型选择**:
```python
# 方案1: OpenAI Embeddings (推荐，性价比最高)
OPENAI_EMBEDDING = {
    "model": "text-embedding-3-small",  # $0.00002/1K tokens
    "dimension": 1536,
    "cost": "~$0.0001/篇论文"
}

# 方案2: 开源模型 (零成本)
SENTENCE_TRANSFORMERS = {
    "model": "sentence-transformers/all-MiniLM-L6-v2",  # 384维
    "dimension": 384,
    "cost": "免费",
    "tradeoff": "精度略低，但足够用"
}

# 方案3: 学术专用模型 (最佳精度)
SPECTER_MDL = {
    "model": "allenai/specter_md",  # 学术论文专用
    "dimension": 768,
    "cost": "免费（本地运行）"
}
```

**Chroma集成**:
```python
import chromadb
from chromadb.config import Settings

# 初始化Chroma (嵌入式，零配置)
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_db"  # 持久化存储
))

# 创建collection
papers_collection = client.get_or_create_collection(
    name="evolutionary_papers",
    metadata={"description": "进化生物学论文向量库"}
)

# 添加论文向量
def add_paper_to_chroma(paper_id, abstract, metadata):
    """将论文添加到向量库"""
    # 生成embedding
    embedding = generate_embedding(abstract)

    # 存入Chroma
    papers_collection.add(
        ids=[str(paper_id)],
        embeddings=[embedding],
        metadatas=[{
            "title": metadata["title"],
            "authors": metadata["authors"],
            "journal": metadata["journal"],
            "taxa": metadata.get("taxa", ""),
            "score": metadata.get("importance_score", 0)
        }],
        documents=[abstract]
    )

# 语义搜索
def search_similar_papers(query, n_results=5, filters=None):
    """搜索相似论文"""
    query_embedding = generate_embedding(query)

    results = papers_collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=filters  # 按物种、期刊、评分过滤
    )

    return results
```

**混合搜索策略**:
```python
# SQLite精确过滤 + Chroma语义搜索
def hybrid_search(
    query: str,
    taxa: str = None,      # 按物种过滤
    min_score: int = 0,    # 最低评分
    journal: str = None,   # 指定期刊
    top_k: int = 10
):
    """
    1. 先用SQLite按元数据过滤
    2. 再用Chroma做语义相似度排序
    3. 返回最相关的结果
    """
    # Step 1: SQLite过滤
    candidate_ids = sqlite_filter(taxa, min_score, journal)

    # Step 2: Chroma语义搜索
    similar_ids = chroma_search(query, top_k * 2)

    # Step 3: 取交集并按相似度排序
    results = merge_and_rank(candidate_ids, similar_ids)

    return results[:top_k]
```

**验收标准**:
- 语义搜索响应<1秒
- 支持中英文查询
- 相关度Top5准确率>80%

---

### 2.5 F5: 每日报告生成

**报告模板**:
```markdown
# 🧬 进化生物学日报 | {date}

## 📊 今日概览
- 新增文献: **{total}** 篇
- 高价值论文: **{high_value}** 篇 (评分>70)
- 主要来源: bioRxiv {n} | arXiv {n} | 期刊 {n}

## 🌟 重点推荐 (Top 5)

### 1. [{title}]({link})
**评分**: {score}/100 | **来源**: {source}

**作者**: {authors}
**物种**: {taxa}
**尺度**: {scale}

**关键发现**:
- {finding_1}
- {finding_2}
- {finding_3}

**进化机制**: {mechanism}
**推荐理由**: {reason}

---

## 🔍 研究热点

### 今日热门
1. **{topic}** ({count}篇)
   - 代表: {paper}

### 方法趋势
- 热门方法: {method}
- 新兴技术: {technique}

## 📚 完整列表

| 评分 | 标题 | 期刊/来源 |
|------|------|-----------|
| {score} | {title} | {source} |

---

**生成时间**: {timestamp}
**反馈**: 觉得有用吗？[点击评分]({feedback_link})
```

**验收标准**:
- 报告生成<30秒
- 格式规范专业
- 至少5篇高价值论文

---

### 2.6 F6: Web界面 (Streamlit)

**页面结构**:
```
┌─────────────────────────────────────┐
│        进化生物学学术飞轮           │
├─────────────────────────────────────┤
│  [今日报告] [文献列表] [历史] [设置] │
├─────────────────────────────────────┤
│                                     │
│  📊 今日概览                        │
│  ┌─────────────────────────────┐   │
│  │ 新增: XX篇 | 高价值: X篇     │   │
│  └─────────────────────────────┘   │
│                                     │
│  🌟 重点推荐                         │
│  ┌─────────────────────────────┐   │
│  │ 1. [论文标题]              │   │
│  │    评分:XX | 作者:XXX      │   │
│  │    [查看详情] [评分]         │   │
│  │                             │   │
│  │ 2. [论文标题]              │   │
│  └─────────────────────────────┘   │
│                                     │
│  [查看完整列表 →]                  │
└─────────────────────────────────────┘
```

**核心功能**:
- 今日报告概览
- 重点推荐卡片
- 文献列表（可筛选、搜索）
- **语义搜索框** - 支持自然语言查询
- **相似论文推荐** - 每篇论文显示相关研究
- 文献详情弹窗
- 用户反馈组件

**语义搜索UI**:
```
┌─────────────────────────────────────┐
│  🔍 语义搜索                         │
│  ┌─────────────────────────────┐   │
│  │ "研究果蝇气候适应的论文"      │   │
│  └─────────────────────────────┘   │
│  [搜索]                             │
│                                     │
│  📂 精细化过滤                       │
│  物种: [Drosophila ▼]               │
│  评分: [70+ ▼]                      │
│  期刊: [全部 ▼]                     │
│                                     │
│  📊 搜索结果                         │
│  ┌─────────────────────────────┐   │
│  │ 1. [相似度: 95%]             │   │
│  │    Rapid adaptation to...   │   │
│  │    [查看] [更多相似]         │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**验收标准**:
- 页面加载<3秒
- 响应式设计
- 交互流畅

---

## 3. 技术架构

### 3.1 技术栈（极简版）

```
┌─────────────────────────────────────────────┐
│              技术架构                        │
├─────────────────────────────────────────────┤
│                                             │
│  前端: Streamlit (Python)                   │
│  后端: FastAPI (Python)                     │
│  结构化数据: SQLite (零配置)                │
│  向量数据: Chroma (嵌入式向量库)            │
│  Embedding: sentence-transformers (免费)    │
│  调度: APScheduler                          │
│  RSS解析: feedparser                        │
│  LLM: 智谱 GLM-4.7                          │
│  代码检查: ruff (lint + format)             │
│  包管理: uv (快速安装)                      │
│                                             │
└─────────────────────────────────────────────┘
```

**项目结构 (src layout)**:
```
evo-flywheel/
├── src/
│   └── evo_flywheel/           # 主包
│       ├── api/                # FastAPI
│       ├── db/                 # SQLite
│       ├── vector/             # Chroma
│       ├── collectors/         # RSS/API
│       ├── analyzers/          # GLM-4.7
│       ├── reporters/          # 报告
│       ├── scheduler/          # 定时任务
│       └── web/                # Streamlit
├── tests/
│   ├── unit/                   # 单元测试
│   └── integration/            # 集成测试
├── config/sources.yaml         # RSS配置
├── pyproject.toml              # 项目配置
└── .env.example                # 环境变量
```

**双数据库架构**:
- ✅ SQLite - 存储结构化数据（元数据、评分、反馈）
- ✅ Chroma - 存储向量数据（语义搜索、相似论文推荐）
- ✅ 两者通过paper_id关联，各司其职

**Embedding模型选择**:
- ✅ sentence-transformers (免费) - MVP首选
- 🔄 可选升级到 OpenAI embeddings 或 SPECTER

---

### 3.2 数据模型（SQLite）

```sql
-- 论文表
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    authors TEXT,           -- 存储为分号分隔的字符串
    abstract TEXT,
    doi TEXT UNIQUE,
    url TEXT,
    publication_date TEXT,
    journal TEXT,
    source TEXT,

    -- 进化生物学字段
    taxa TEXT,
    evolutionary_scale TEXT,
    research_method TEXT,
    evolutionary_mechanism TEXT,  -- 存储为分号分隔

    -- AI分析结果
    importance_score INTEGER,
    key_findings TEXT,        -- 存储为JSON字符串
    innovation_summary TEXT,
    tags TEXT,                -- 存储为分号分隔

    -- 向量搜索
    embedding_id TEXT,        -- Chroma中的ID (与id相同)
    embedded INTEGER DEFAULT 0,  -- 是否已生成向量

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 每日报告表
CREATE TABLE IF NOT EXISTS daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date TEXT UNIQUE,
    total_papers INTEGER,
    high_value_papers INTEGER,
    top_paper_ids TEXT,       -- 存储为逗号分隔的ID
    report_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 反馈表
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    is_helpful INTEGER,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);

-- RSS源配置表
CREATE TABLE IF NOT EXISTS rss_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    url TEXT,
    source_type TEXT,
    priority INTEGER,
    enabled INTEGER DEFAULT 1,
    last_fetch TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_papers_date ON papers(publication_date DESC);
CREATE INDEX IF NOT EXISTS idx_papers_score ON papers(importance_score DESC);
CREATE INDEX IF NOT EXISTS idx_papers_source ON papers(source);
```

---

### 3.3 API接口

```
# 论文相关
GET    /api/papers                    - 获取文献列表
GET    /api/papers/{id}               - 获取文献详情
POST   /api/papers/analyze            - 分析单篇文献

# 语义搜索 (NEW!)
GET    /api/search/semantic           - 语义搜索
POST   /api/search/similar            - 查找相似论文
GET    /api/search/hybrid             - 混合搜索（语义+过滤）

# 报告相关
GET    /api/reports/today              - 获取今日报告
GET    /api/reports/{date}             - 获取指定日期报告
POST   /api/reports/generate          - 手动生成报告

# 反馈相关
POST   /api/feedback                  - 提交反馈

# 系统相关
GET    /api/stats/overview             - 系统统计
POST   /api/rss/fetch                  - 手动触发采集
POST   /api/embeddings/rebuild         - 重建向量索引
```

**语义搜索API示例**:
```python
# GET /api/search/semantic?q=adaptation+climate+change&limit=10
{
    "query": "adaptation climate change",
    "results": [
        {
            "id": 123,
            "title": "Rapid adaptation to climate change in Drosophila",
            "similarity": 0.92,
            "authors": ["Smith et al."],
            "abstract": "...",
            "taxa": "Drosophila",
            "score": 85
        },
        ...
    ]
}
```

---

## 4. bioRxiv API集成

### 4.1 为什么使用API而非RSS

```
✅ API优势:
- 绕过Cloudflare保护
- 返回结构化JSON
- 支持按日期范围查询
- 支持按分类过滤
- 官方支持，稳定可靠

❌ RSS问题:
- Cloudflare保护
- 需要JavaScript渲染
- 不稳定
```

### 4.2 API使用方式

```python
def fetch_biorxiv_papers(days=7, category="evolutionary_biology"):
    """获取bioRxiv论文"""
    from datetime import datetime, timedelta

    end = datetime.now()
    start = end - timedelta(days=days)

    url = f"https://api.biorxiv.org/details/biorxiv/{start.strftime('%Y-%m-%d')}/{end.strftime('%Y-%m-%d')}"
    params = {
        "category": category,
        "format": "json"
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data.get("collection", [])
```

### 4.3 数据映射

```python
def parse_biorxiv_paper(item):
    """解析bioRxiv API返回的论文数据"""
    return {
        "title": item.get("title"),
        "authors": item.get("authors", "").split(";"),
        "abstract": item.get("abstract"),
        "doi": item.get("doi"),
        "url": f"https://www.biorxiv.org/content/{item.get('doi')}",
        "publication_date": item.get("date"),
        "journal": "bioRxiv",
        "source": "biorxiv_api",
        "license": item.get("license"),
        "version": item.get("version"),
        "category": item.get("category")
    }
```

---

## 5. 开发计划

### 5.1 时间线（2-3周）

```
Week 1: 核心功能
├─ Day 1-2: 环境搭建 + 数据库设计
├─ Day 3-4: RSS采集 + bioRxiv API集成
├─ Day 5: LLM分析服务
└─ Day 6-7: 报告生成模块

Week 2: 界面与集成
├─ Day 8-10: Streamlit界面开发
├─ Day 11: 反馈收集
└─ Day 12-13: 集成测试

Week 3: 优化（可选）
├─ Day 14-15: 性能优化
└─ Day 16-17: 文档与部署
```

### 5.2 任务分解

| 任务 | 工作量 | 交付物 |
|------|--------|--------|
| 项目初始化 | 0.5d | 项目结构、依赖 |
| 数据库Schema | 0.5d | SQL脚本 |
| RSS采集器 | 2d | 采集服务 |
| bioRxiv API | 1d | API集成 |
| LLM分析 | 2d | 分析服务 |
| 报告生成 | 1.5d | 报告模块 |
| Streamlit界面 | 3d | Web界面 |
| 测试 | 2d | 测试报告 |

---

## 6. 成功指标

### 6.1 验收标准

**功能完整性**:
- [ ] 8个数据源正常采集
- [ ] LLM分析功能可用
- [ ] 每日报告按时生成
- [ ] Web界面可访问

**质量标准**:
- [ ] 单元测试覆盖率>50%
- [ ] 无P0级Bug
- [ ] API文档完整

**性能标准**:
- [ ] 采集耗时<2分钟
- [ ] 报告生成<30秒
- [ ] 页面加载<3秒

### 6.2 验证指标

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| 日新增论文 | >30篇 | 系统统计 |
| 分析准确率 | >70% | 人工抽检 |
| 系统稳定性 | >95% | 运行时间 |

---

## 7. 成本估算

```
月度成本:
- LLM API: ¥5-10/月
  - 30篇/天 × ¥0.005/篇 × 30天 = ~¥5
  - GLM-4.7 定价: ¥0.5/1M tokens (输入), ¥2/1M tokens (输出)

- Embedding: 免费
  - sentence-transformers 本地运行，零成本

- 数据库: 免费
  - SQLite + Chroma 本地文件存储

- 部署: $5-10/月 (小型云服务器)

总计: ~¥15-20/月 ($2-3/月)
```

**可选升级**:
- OpenAI embeddings: +$2-5/月（更高精度）
- SPECTER学术模型: 免费（需更多资源）

---

## 8. 风险与应对

| 风险 | 可能性 | 应对措施 |
|------|--------|----------|
| RSS源不稳定 | 中 | 多源备份、容错处理 |
| GLM API限流 | 低 | 添加重试机制、并发控制 |
| 分析质量不达预期 | 高 | Prompt调优、人工校准 |
| 进化生物学领域知识不足 | 中 | Prompt优化、专家咨询 |

---

## 9. 附录

### 9.1 完整期刊列表

参见文档: `进化生物学期刊RSS源总表.md`

### 9.2 技术选型理由

| 组件 | 选型 | 理由 |
|------|------|------|
| 后端 | FastAPI | 快速、异步、自动文档 |
| 前端 | Streamlit | 无需前端知识、快速迭代 |
| 结构化数据 | SQLite | 零配置、单文件 |
| 向量数据 | Chroma | 嵌入式、与SQLite完美配合 |
| Embedding | sentence-transformers | 免费开源、支持中文 |
| LLM | GLM-4.7 | 国产模型、性价比高、中文友好 |
| 调度 | APScheduler | 轻量级、易用 |

### 9.3 Embedding模型对比

| 模型 | 维度 | 成本 | 优势 | 推荐场景 |
|------|------|------|------|----------|
| all-MiniLM-L6-v2 | 384 | 免费 | 速度快、体积小 | MVP首选 |
| text-embedding-3-small | 1536 | $0.02/1M tokens | 精度高 | 生产环境 |
| SPECTER | 768 | 免费 | 学术论文专用 | 纯学术场景 |

### 9.4 参考资源

- [bioRxiv API文档](https://api.biorxiv.org/)
- [arXiv API](https://arxiv.org/help/api/)
- [Chroma文档](https://docs.trychroma.com/)
- [sentence-transformers](https://www.sbert.net/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Streamlit文档](https://docs.streamlit.io/)

---

**文档版本**: v1.2
**维护者**: [Your Name]
**状态**: 待开发
**更新记录**:
- v1.2 (2025-12-28): 更换LLM为GLM-4.7，更新成本估算
- v1.1 (2025-12-28): 新增Chroma向量数据库、语义搜索、Embedding模型集成
- v1.0 (2025-12-28): 初始版本
