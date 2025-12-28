# Evo-Flywheel 开发路线图

> 项目周期: 2-3周
> 目标: 完成可演示的 MVP
> 更新日期: 2025-12-28

---

## 阶段概览

| 阶段 | 名称 | 工期 | 代码量 | 优先级 |
|------|------|------|--------|--------|
| Phase 0 | 项目初始化 | 0.5天 | ~200 行 | P0 |
| Phase 1 | 数据层构建 | 2天 | ~800 行 | P0 |
| Phase 2 | 采集层开发 | 2天 | ~700 行 | P0 |
| Phase 3 | 分析层实现 | 2天 | ~600 行 | P0 |
| Phase 4 | 搜索层集成 | 1.5天 | ~500 行 | P0 |
| Phase 5 | 展示层开发 | 3天 | ~900 行 | P0 |
| Phase 6 | 测试与优化 | 2天 | ~600 行 | P1 |
| **总计** | **MVP** | **13天** | **~4300 行** | - |

**代码分布**:
- 业务代码: ~3000 行 (70%)
- 测试代码: ~1300 行 (30%)
- 配置文件: ~200 行
- 文档: 已有 ~2000 行

---

## Phase 0: 项目初始化 (0.5天)

### 目标
搭建项目基础结构，配置开发环境

### 代码量预估
- **总代码量**: ~200 行
- **主要文件**: 8 个
  - `pyproject.toml`: ~80 行
  - `ruff.toml`: ~30 行
  - `.env.example`: ~10 行
  - `config/sources.yaml`: ~50 行
  - `src/evo_flywheel/__init__.py`: ~10 行
  - `tests/__init__.py`, `tests/conftest.py`: ~20 行

### 任务清单

| 任务 | 说明 | 代码量 |
|------|------|--------|
| 目录结构创建 | 创建 src/, tests/, docs/, config/ 等目录 | - |
| 依赖管理 | pyproject.toml，定义所有依赖包 | ~80 行 |
| 配置文件 | ruff.toml，config/sources.yaml | ~80 行 |
| 环境变量 | .env.example 模板 | ~10 行 |
| 日志配置 | 统一的日志格式和输出 | ~30 行 |

### 验收标准

- [ ] 项目目录结构完整
- [ ] `uv pip install -e ".[dev]"` 成功无报错
- [ ] 配置文件可正常加载
- [ ] 日志系统可正常输出

---

## Phase 1: 数据层构建 (2天)

### 目标
搭建双数据库架构（SQLite + Chroma）

### 代码量预估
- **总代码量**: ~800 行
- **主要文件**: 12 个
  - `src/evo_flywheel/db/models.py`: ~150 行 (SQLAlchemy 模型)
  - `src/evo_flywheel/db/crud.py`: ~250 行 (CRUD 操作)
  - `src/evo_flywheel/db/__init__.py`: ~30 行
  - `src/evo_flywheel/vector/client.py`: ~120 行 (Chroma 封装)
  - `src/evo_flywheel/vector/__init__.py`: ~20 行
  - `tests/unit/test_db.py`: ~150 行
  - `tests/unit/test_vector.py`: ~80 行

### 任务清单

| 任务 | 说明 | 代码量 |
|------|------|--------|
| SQLite Schema 设计 | 实现数据库表结构和索引 | ~150 行 |
| 数据库初始化脚本 | 创建表、索引、初始数据 | ~50 行 |
| Chroma 集成 | 配置向量数据库连接 | ~140 行 |
| 数据模型定义 | 定义 Python 数据模型类 | ~150 行 |
| CRUD 基础操作 | 实现增删改查基础函数 | ~250 行 |
| 单元测试 | 数据库和向量测试 | ~230 行 |

### 验收标准

- [ ] 数据库表创建成功，结构符合 PRD
- [ ] 可以成功插入和查询论文数据
- [ ] Chroma collection 创建成功
- [ ] 单元测试覆盖率 > 60%

---

## Phase 2: 采集层开发 (2天)

### 目标
实现多源文献自动采集

### 代码量预估
- **总代码量**: ~700 行
- **主要文件**: 10 个
  - `src/evo_flywheel/collectors/rss.py`: ~200 行 (RSS 解析)
  - `src/evo_flywheel/collectors/biorxiv.py`: ~150 行 (API 调用)
  - `src/evo_flywheel/collectors/dedup.py`: ~80 行 (去重逻辑)
  - `src/evo_flywheel/scheduler/jobs.py`: ~100 行 (定时任务)
  - `config/sources.yaml`: ~50 行 (RSS 源配置)
  - `tests/unit/test_collectors.py`: ~120 行

### 任务清单

| 任务 | 说明 | 代码量 |
|------|------|--------|
| RSS 采集器 | 实现 feedparser 解析逻辑 | ~200 行 |
| bioRxiv API 集成 | 实现官方 API 调用 | ~150 行 |
| 数据去重 | 基于 DOI/标题的去重逻辑 | ~80 行 |
| 元数据提取 | 统一各源数据格式 | ~70 行 |
| 定时任务配置 | APScheduler 配置每日采集 | ~100 行 |
| 错误处理 | 单源失败不影响其他源 | ~50 行 |
| 单元测试 | 采集器测试 | ~120 行 |

### 验收标准

- [ ] 8个数据源全部正常采集
- [ ] 去重准确率 > 99%
- [ ] 单次采集耗时 < 2分钟
- [ ] 采集失败有完整日志

---

## Phase 3: 分析层实现 (2天)

### 目标
实现 GLM-4.7 智能分析服务

### 代码量预估
- **总代码量**: ~600 行
- **主要文件**: 8 个
  - `src/evo_flywheel/analyzers/prompts.py`: ~100 行 (Prompt 模板)
  - `src/evo_flywheel/analyzers/llm.py`: ~200 行 (GLM-4.7 封装)
  - `src/evo_flywheel/analyzers/batch.py`: ~80 行 (批量处理)
  - `src/evo_flywheel/analyzers/schemas.py`: ~60 行 (数据结构)
  - `tests/unit/test_llm.py`: ~100 行
  - `tests/integration/test_analysis.py`: ~60 行

### 任务清单

| 任务 | 说明 | 代码量 |
|------|------|--------|
| Prompt 模板 | 定义进化生物学分析 Prompt | ~100 行 |
| LLM 服务封装 | 封装智谱 GLM-4.7 API 调用 | ~200 行 |
| 结构化解析 | 解析 LLM 返回的 JSON | ~60 行 |
| 批量处理 | 支持批量分析，控制并发 | ~80 行 |
| 成本控制 | 添加 Token 统计和成本估算 | ~40 行 |
| 缓存机制 | 避免重复分析同一论文 | ~50 行 |
| 单元测试 | LLM 服务测试 | ~100 行 |

### 验收标准

- [ ] 单篇分析耗时 < 10秒
- [ ] LLM 返回结果可正确解析
- [ ] 关键发现提取准确率 > 70%
- [ ] 单篇分析成本 < ¥0.05
- [ ] 批量分析 30 篇耗时 < 5分钟

---

## Phase 4: 搜索层集成 (1.5天)

### 目标
实现语义搜索和向量检索

### 代码量预估
- **总代码量**: ~500 行
- **主要文件**: 8 个
  - `src/evo_flywheel/vector/embeddings.py`: ~100 行 (Embedding 服务)
  - `src/evo_flywheel/api/search.py`: ~150 行 (搜索 API)
  - `src/evo_flywheel/vector/hybrid.py`: ~80 行 (混合搜索)
  - `tests/unit/test_embeddings.py`: ~80 行
  - `tests/unit/test_search.py`: ~90 行

### 任务清单

| 任务 | 说明 | 代码量 |
|------|------|--------|
| Embedding 服务 | 集成 sentence-transformers | ~100 行 |
| 向量生成 | 为论文摘要生成向量 | ~50 行 |
| Chroma 存储 | 将向量存入 Chroma | ~40 行 |
| 语义搜索 API | 实现相似度查询接口 | ~150 行 |
| 混合搜索 | SQLite 过滤 + Chroma 排序 | ~80 行 |
| 向量重建 | 支持重建向量索引 | ~30 行 |
| 单元测试 | Embedding 和搜索测试 | ~170 行 |

### 验收标准

- [ ] Embedding 生成成功，384维向量
- [ ] 语义搜索响应 < 1秒
- [ ] 支持中英文查询
- [ ] Top5 结果相关度 > 80%
- [ ] 混合搜索功能正常

---

## Phase 5: 展示层开发 (3天)

### 目标
实现 Streamlit Web 界面

### 代码量预估
- **总代码量**: ~900 行
- **主要文件**: 10 个
  - `src/evo_flywheel/web/app.py`: ~150 行 (主应用)
  - `src/evo_flywheel/web/pages/home.py`: ~120 行 (首页)
  - `src/evo_flywheel/web/pages/list.py`: ~150 行 (文献列表)
  - `src/evo_flywheel/web/pages/search.py`: ~130 行 (语义搜索)
  - `src/evo_flywheel/web/pages/detail.py`: ~100 行 (论文详情)
  - `src/evo_flywheel/reporters/generator.py`: ~120 行 (报告生成)
  - `src/evo_flywheel/api/main.py`: ~80 行 (FastAPI)
  - `tests/unit/test_pages.py`: ~50 行

### 任务清单

| 任务 | 说明 | 代码量 |
|------|------|--------|
| 首页 | 今日报告概览、重点推荐 | ~120 行 |
| 文献列表页 | 可筛选、搜索、分页 | ~150 行 |
| 论文详情页 | 完整信息展示 | ~100 行 |
| 语义搜索页 | 自然语言搜索界面 | ~130 行 |
| 相似论文推荐 | 每篇论文显示相关研究 | ~70 行 |
| 反馈组件 | 评分、评论功能 | ~80 行 |
| 报告生成页 | 手动生成历史报告 | ~120 行 |
| FastAPI 后端 | REST API 接口 | ~130 行 |

### 验收标准

- [ ] 页面加载时间 < 3秒
- [ ] 所有核心功能可访问
- [ ] 响应式设计，适配移动端
- [ ] 用户交互流畅无卡顿
- [ ] 反馈数据正常保存

---

## Phase 6: 测试与优化 (2天)

### 目标
保证系统质量，优化性能

### 代码量预估
- **总代码量**: ~600 行 (主要是测试代码)
- **主要文件**: 8 个
  - `tests/integration/test_pipeline.py`: ~150 行 (端到端测试)
  - `tests/integration/test_e2e.py`: ~120 行 (E2E 测试)
  - `tests/performance/test_load.py`: ~80 行 (压力测试)
  - `Dockerfile`: ~30 行
  - `docker-compose.yml`: ~40 行
  - `.github/workflows/ci.yml`: ~60 行 (CI 配置)
  - 各种 Bug 修复和优化: ~120 行

### 任务清单

| 任务 | 说明 | 代码量 |
|------|------|--------|
| 单元测试 | 核心逻辑测试覆盖 (补充) | ~100 行 |
| 集成测试 | 端到端流程测试 | ~150 行 |
| E2E 测试 | Playwright/Selenium | ~120 行 |
| 压力测试 | 模拟 100+ 论文场景 | ~80 行 |
| 性能优化 | 数据库查询、API 响应优化 | ~70 行 |
| 错误修复 | 修复所有 P0/P1 Bug | ~50 行 |
| CI/CD 配置 | GitHub Actions | ~60 行 |
| 部署准备 | Docker 化（可选） | ~70 行 |

### 验收标准

- [ ] 单元测试覆盖率 > 50%
- [ ] 无 P0 级 Bug
- [ ] P1 级 Bug < 3个
- [ ] 采集、分析、报告全流程打通
- [ ] API 文档完整

---

## 总体验收标准

### 功能完整性

- [ ] 8个数据源正常采集
- [ ] LLM 分析功能可用
- [ ] 语义搜索功能正常
- [ ] 每日报告按时生成
- [ ] Web 界面可访问

### 质量标准

- [ ] 单元测试覆盖率 > 50%
- [ ] 无 P0 级 Bug
- [ ] API 文档完整
- [ ] 代码注释完整

### 性能标准

- [ ] 采集耗时 < 2分钟
- [ ] 单篇分析 < 10秒
- [ ] 报告生成 < 30秒
- [ ] 语义搜索 < 1秒
- [ ] 页面加载 < 3秒

---

## 依赖关系

```
Phase 0 (初始化)
    ↓
Phase 1 (数据层) ←─────┐
    ↓                  │
Phase 2 (采集层)        │
    ↓                  │
Phase 3 (分析层)        │
    ↓                  │
Phase 4 (搜索层)        │
    ↓                  │
Phase 5 (展示层) ───────┘
    ↓
Phase 6 (测试与优化)
```

---

## 风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| RSS 源不稳定 | 中 | 多源备份、容错处理 |
| LLM 成本超预算 | 中 | 使用 mini 模型、缓存 |
| Chroma 性能问题 | 低 | 调整索引参数、分片 |
| 开发进度延期 | 中 | 砍掉非核心功能 |

---

**文档版本**: v1.1
**更新记录**:
- v1.1 (2025-12-28): 添加各阶段代码量预估
- v1.0 (2025-12-28): 初始版本
