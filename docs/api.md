# Evo-Flywheel API 文档

Evo-Flywheel REST API for evolutionary biology literature analysis.

**Base URL**: `http://localhost:8000`

**API Version**: v0.9.0

**Interactive Documentation**:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

---

## 目录

- [系统端点](#系统端点)
- [论文管理](#论文管理)
- [搜索](#搜索)
- [报告](#报告)
- [飞轮控制](#飞轮控制)
- [数据采集](#数据采集)
- [分析调度](#分析调度)
- [向量嵌入](#向量嵌入)
- [用户反馈](#用户反馈)
- [统计](#统计)
- [数据模型](#数据模型)

---

## 系统端点

### GET `/`
根端点，返回 API 基本信息。

**Response**:
```json
{
  "message": "Evo-Flywheel API",
  "docs": "/api/v1/docs"
}
```

### GET `/api/v1/health`
健康检查端点。

**Response**:
```json
{
  "status": "healthy"
}
```

---

## 论文管理

### GET `/api/v1/papers`
获取论文列表，支持分页和筛选。

**Query Parameters**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| skip | integer | 否 | 0 | 跳过的记录数（分页偏移） |
| limit | integer | 否 | 20 | 返回的记录数 (1-100) |
| taxa | string | 否 | - | 筛选分类群（如 "Mammalia", "Aves"） |
| min_score | integer | 否 | - | 最低重要性评分 (0-100) |

**Response**:
```json
{
  "total": 150,
  "papers": [
    {
      "id": 1,
      "title": "论文标题",
      "authors": ["作者 A", "作者 B"],
      "abstract": "摘要内容",
      "doi": "10.1101/2025.00001",
      "url": "https://biorxiv.org/content/10.1101/2025.00001",
      "publication_date": "2025-12-29",
      "source": "biorxiv_api",
      "taxa": "Mammalia",
      "evolutionary_scale": "Population",
      "research_method": "Population Genetic",
      "evolutionary_mechanism": "Natural selection",
      "importance_score": 85,
      "key_findings": "关键发现JSON字符串",
      "innovation_summary": "创新性总结",
      "embedded": true
    }
  ]
}
```

### GET `/api/v1/papers/{paper_id}`
获取单篇论文详情。

**Path Parameters**:
- `paper_id` (integer): 论文 ID

**Response**: 同上单篇论文对象

**Error Response** (404):
```json
{
  "detail": "论文不存在"
}
```

### POST `/api/v1/papers/{paper_id}/analyze`
使用 LLM 分析单篇论文的进化生物学特征。

**Path Parameters**:
- `paper_id` (integer): 论文 ID

**Response**:
```json
{
  "paper_id": 1,
  "taxa": "Mammalia",
  "importance_score": 85,
  "key_findings": ["发现1", "发现2", "发现3"]
}
```

**Error Responses**:
- 404: 论文不存在
- 400: 论文摘要为空
- 500: 分析失败

### POST `/api/v1/papers/analyze-batch`
批量分析未分析的论文。

**Query Parameters**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| limit | integer | 否 | 10 | 批量分析数量 (1-50) |

**Response**:
```json
{
  "analyzed": 8,
  "total": 10
}
```

---

## 搜索

### GET `/api/v1/search/semantic`
语义搜索论文，使用向量嵌入进行相似度搜索。

**Query Parameters**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| q | string | 是 | - | 搜索查询 |
| limit | integer | 否 | 10 | 返回结果数 (1-50) |

**Response**:
```json
{
  "results": [
    {
      "id": 1,
      "title": "匹配的论文标题",
      "abstract": "摘要",
      "taxa": "Mammalia",
      "importance_score": 85,
      "similarity": 0.92
    }
  ]
}
```

### POST `/api/v1/search/similar`
基于指定论文查找相似研究。

**Query Parameters**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| paper_id | integer | 是 | - | 参考论文 ID |
| limit | integer | 否 | 5 | 返回结果数 (1-20) |

**Response**:
```json
{
  "similar_papers": [
    {
      "id": 2,
      "title": "相似论文标题",
      "abstract": "摘要",
      "taxa": "Mammalia",
      "importance_score": 80,
      "similarity": 0.88
    }
  ]
}
```

### GET `/api/v1/search/hybrid`
混合搜索（语义相似度 + 元数据过滤）。

**Query Parameters**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| q | string | 是 | - | 搜索查询 |
| taxa | string | 否 | - | 物种过滤 |
| min_score | integer | 否 | - | 最低重要性评分 (0-100) |
| limit | integer | 否 | 10 | 返回结果数 (1-50) |

**Response**:
```json
{
  "results": [
    {
      "id": 1,
      "title": "匹配的论文",
      "abstract": "摘要",
      "taxa": "Mammalia",
      "importance_score": 90,
      "similarity": 0.95
    }
  ]
}
```

---

## 报告

### GET `/api/v1/reports/today`
获取今日报告，返回今天采集的论文统计和重点推荐。

**Response**:
```json
{
  "date": "2025-12-29",
  "count": 15,
  "papers": [
    {
      "id": 1,
      "title": "今日重点论文",
      "authors": ["作者 A"],
      "abstract": "摘要",
      "importance_score": 95
    }
  ]
}
```

### GET `/api/v1/reports/{report_date}`
获取指定日期的报告。

**Path Parameters**:
- `report_date` (date): 日期，格式 YYYY-MM-DD

**Response**: 同 `/reports/today`

### POST `/api/v1/reports/generate`
手动生成指定日期的报告。

**Query Parameters**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| date_str | string | 否 | - | 日期字符串 (YYYY-MM-DD)，默认今天 |

**Response**: 生成的报告内容

### GET `/api/v1/reports/deep`
获取深度报告列表（按创建时间倒序）。

由于飞轮每 4 小时运行一次，同一天可能有多份报告。

**Query Parameters**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| limit | integer | 否 | 10 | 返回数量限制 (1-100) |

**Response**:
```json
[
  {
    "id": 1,
    "report_date": "2025-12-29",
    "total_papers": 36,
    "high_value_papers": 5,
    "top_paper_ids": [1, 2, 3],
    "content": {
      "research_summary": "研究概要",
      "hot_topics": [
        {
          "topic": "热点话题名称",
          "description": "描述"
        }
      ],
      "recommended_papers": [
        {
          "title": "论文标题",
          "reason": "推荐理由"
        }
      ]
    },
    "created_at": "2025-12-29T12:00:00"
  }
]
```

### GET `/api/v1/reports/deep/{report_id}`
获取指定 ID 的深度报告详情。

**Path Parameters**:
- `report_id` (integer): 报告 ID

**Response**: 同上单个报告对象

**Error Response** (404):
```json
{
  "detail": "未找到 ID 为 1 的深度报告"
}
```

### GET `/api/v1/reports/deep/date/{report_date}`
获取指定日期的所有深度报告。

由于飞轮每 4 小时运行一次，同一天可能有多份报告。

**Path Parameters**:
- `report_date` (date): 日期，格式 YYYY-MM-DD

**Response**: 同 `/reports/deep`，返回按创建时间倒序的报告列表

### POST `/api/v1/reports/generate-deep`
生成深度报告，使用 LLM 生成包含研究概要、热点话题、趋势分析的深度报告。

**Query Parameters**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| date | string | 否 | - | 目标日期 (YYYY-MM-DD)，默认今天 |

**Response**:
```json
{
  "id": 1,
  "report_date": "2025-12-29",
  "total_papers": 36,
  "high_value_papers": 5
}
```

**Error Responses**:
- 400: 日期格式错误或没有论文
- 500: 生成失败

---

## 飞轮控制

### POST `/api/v1/flywheel/trigger`
手动触发一次飞轮运行，执行完整流程：采集论文 → 分析论文 → 生成报告。

**Response**:
```json
{
  "collected": 25,
  "analyzed": 20,
  "report_generated": true
}
```

**Error Response** (500):
```json
{
  "detail": "飞轮执行失败"
}
```

### GET `/api/v1/flywheel/status`
获取飞轮运行状态。

**Response**:
```json
{
  "running": true,
  "last_run": "2025-12-29T12:00:00",
  "next_run": "2025-12-29T16:00:00"
}
```

**字段说明**:
- `running`: 调度器是否运行中
- `last_run`: 上次运行时间 (ISO 格式)
- `next_run`: 下次运行时间 (ISO 格式)

### POST `/api/v1/flywheel/schedule`
控制飞轮调度器，启动或停止自动调度（每 4 小时运行一次）。

**Request Body**:
```json
{
  "action": "start"
}
```

**Fields**:

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| action | string | 是 | 操作: "start" 或 "stop" |

**Response** (启动):
```json
{
  "status": "started"
}
```

**Response** (停止):
```json
{
  "status": "stopped"
}
```

**Error Responses**:
- 400: 调度器已在运行中 / 调度器未运行 / 无效的操作
- 500: 启动/停止调度器失败

---

## 数据采集

### POST `/api/v1/collection/fetch`
手动触发从 RSS 和 API 采集论文。

**Query Parameters**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| days | integer | 否 | 7 | 采集最近几天的论文 (1-30) |
| sources | string | 否 | - | 指定数据源（逗号分隔，如 "biorxiv_api,arxiv"） |

**Response**:
```json
{
  "total": 25,
  "new": 18
}
```

### GET `/api/v1/collection/status`
获取采集状态和最近采集日志。

**Response**:
```json
{
  "status": "idle",
  "last_collection": {
    "status": "success",
    "total_papers": 25,
    "new_papers": 18,
    "sources": "biorxiv_api,arxiv",
    "error_message": null,
    "created_at": "2025-12-29T09:00:00"
  },
  "total_sources": 8
}
```

**status 值**:
- `idle`: 系统空闲
- `running`: 采集中
- `success`: 上次采集成功
- `failed`: 上次采集失败

---

## 分析调度

### POST `/api/v1/analysis/trigger`
触发论文分析，对未分析的论文进行批量分析。

**Query Parameters**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| limit | integer | 否 | 50 | 分析论文数量限制 (1-100) |
| min_score | integer | 否 | - | 最低重要性评分过滤 |

**Response**:
```json
{
  "analyzed": 30,
  "total": 30,
  "message": "已分析 30 篇论文"
}
```

### GET `/api/v1/analysis/status`
获取论文分析状态统计。

**Response**:
```json
{
  "total": 150,
  "analyzed": 120,
  "unanalyzed": 30,
  "progress": 80.0
}
```

---

## 向量嵌入

### POST `/api/v1/embeddings/rebuild`
重建向量索引，为论文重新生成并存储向量嵌入。

**Query Parameters**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| force | boolean | 否 | false | 强制重建所有论文的向量 |

**Response**:
```json
{
  "rebuilt": 45,
  "total": 50,
  "skipped": 5,
  "message": "成功向量化 45 篇论文，跳过 5 篇"
}
```

---

## 用户反馈

### POST `/api/v1/feedback`
创建用户反馈，提交对论文的评分和评论。

**Request Body**:
```json
{
  "paper_id": 1,
  "rating": 5,
  "is_helpful": true,
  "comment": "非常有用的研究"
}
```

**Fields**:

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| paper_id | integer | 是 | 论文 ID |
| rating | integer | 是 | 评分 1-5 |
| is_helpful | boolean | 否 | 是否有帮助 |
| comment | string | 否 | 评论 (最多1000字符) |

**Response**:
```json
{
  "id": 1,
  "paper_id": 1,
  "rating": 5,
  "is_helpful": true,
  "comment": "非常有用的研究"
}
```

### GET `/api/v1/feedback`
获取反馈列表，支持按论文筛选。

**Query Parameters**:

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| paper_id | integer | 否 | - | 论文 ID 筛选 |

**Response**:
```json
{
  "feedbacks": [
    {
      "id": 1,
      "paper_id": 1,
      "rating": 5,
      "is_helpful": true,
      "comment": "非常有用的研究"
    }
  ]
}
```

---

## 统计

### GET `/api/v1/stats/overview`
获取系统概览统计。

**Response**:
```json
{
  "total_papers": 150,
  "analyzed_papers": 120,
  "embedded_papers": 100,
  "today_new": 5,
  "analysis_rate": 80.0,
  "embedding_rate": 66.67
}
```

---

## 数据模型

### PaperResponse
论文响应模型。

| 字段 | 类型 | 描述 |
|------|------|------|
| id | integer | 论文 ID |
| title | string | 标题 |
| authors | string[] | 作者列表 |
| abstract | string \| null | 摘要 |
| doi | string \| null | DOI |
| url | string | 论文链接 |
| publication_date | string | 发布日期 (ISO 格式) |
| source | string | 数据源 |
| taxa | string \| null | 分类群 |
| evolutionary_scale | string \| null | 进化尺度 |
| research_method | string \| null | 研究方法 |
| evolutionary_mechanism | string \| null | 进化机制 |
| importance_score | integer \| null | 重要性评分 (0-100) |
| key_findings | string \| null | 关键发现 (JSON 字符串) |
| innovation_summary | string \| null | 创新性总结 |
| embedded | boolean | 是否已向量化 |

### FeedbackCreate
创建反馈请求模型。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| paper_id | integer | 是 | 论文 ID (≥1) |
| rating | integer | 是 | 评分 1-5 |
| is_helpful | boolean \| null | 否 | 是否有帮助 |
| comment | string \| null | 否 | 评论 (最多1000字符) |

### DeepReportResponse
深度报告响应模型（简化版）。

| 字段 | 类型 | 描述 |
|------|------|------|
| id | integer | 报告 ID |
| report_date | string | 报告日期 (YYYY-MM-DD) |
| total_papers | integer | 总论文数 |
| high_value_papers | integer | 高价值论文数 |

### DeepReportDetailResponse
深度报告详情响应模型（完整版）。

| 字段 | 类型 | 描述 |
|------|------|------|
| id | integer | 报告 ID |
| report_date | string | 报告日期 (YYYY-MM-DD) |
| total_papers | integer | 总论文数 |
| high_value_papers | integer | 高价值论文数 |
| top_paper_ids | integer[] | 顶级论文 ID 列表 |
| content | object | 报告内容（研究概要、热点话题、推荐论文等） |
| created_at | string | 创建时间 (ISO 格式) |

**content 字段结构**:
```json
{
  "research_summary": "研究概要",
  "hot_topics": [
    {
      "topic": "热点话题名称",
      "description": "话题描述"
    }
  ],
  "recommended_papers": [
    {
      "title": "论文标题",
      "reason": "推荐理由"
    }
  ]
}
```

### FlywheelTriggerResponse
飞轮触发响应模型。

| 字段 | 类型 | 描述 |
|------|------|------|
| collected | integer | 采集的论文数量 |
| analyzed | integer | 分析的论文数量 |
| report_generated | boolean | 是否生成了报告 |

### FlywheelStatusResponse
飞轮状态响应模型。

| 字段 | 类型 | 描述 |
|------|------|------|
| running | boolean | 调度器是否运行中 |
| last_run | string \| null | 上次运行时间 (ISO 格式) |
| next_run | string \| null | 下次运行时间 (ISO 格式) |

### ScheduleControlRequest
调度控制请求模型。

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| action | string | 是 | 操作: "start" 或 "stop" |

### ScheduleControlResponse
调度控制响应模型。

| 字段 | 类型 | 描述 |
|------|------|------|
| status | string | 操作后的状态: "started" 或 "stopped" |

---

## 错误响应

所有错误响应遵循统一格式：

```json
{
  "detail": "错误描述信息"
}
```

**常见 HTTP 状态码**:

| 状态码 | 描述 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 数据源列表

支持以下数据源（可在 `sources` 参数中使用）：

| 名称 | 类型 | 描述 |
|------|------|------|
| biorxiv_api | API | bioRxiv API |
| arxiv | RSS | arXiv q-bio.PE |
| plos | RSS | PLOS 系列期刊 |
| nature | RSS | Nature 期刊 |
| science | RSS | Science 期刊 |
| cell | RSS | Cell 期刊 |
| elife | RSS | eLife 期刊 |
| oxford | RSS | Oxford 期刊 |

---

## 开发指南

### 启动服务器

```bash
# 安装依赖
uv pip install -e ".[dev]"

# 方式1: 同时启动前后端 (推荐)
./start.sh

# 方式2: 单独启动 API 服务器
uvicorn evo_flywheel.api.main:app --reload

# 方式3: 单独启动 Web 界面
streamlit run src/evo_flywheel/web/app.py
```

### 运行测试

```bash
# 运行所有 API 测试
pytest tests/api/ -v

# 运行特定模块测试
pytest tests/api/test_papers.py -v
```

### 访问 API 文档

启动服务器后访问：
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc
