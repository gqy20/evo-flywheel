# 开源项目调研报告：AI飞轮与多智能体系统

> **项目**: Evo-Flywheel 学术飞轮系统
> **文档类型**: 开源项目调研与架构设计参考
> **版本**: v1.0
> **创建日期**: 2025-12-28
> **状态**: 调研完成

---

## 摘要

本文档系统调研了与学术飞轮系统相关的开源项目，重点关注多智能体框架、评估反馈循环、研究自动化、知识图谱等方向的实现模式。通过对CrewAI、OpenAI Evaluation Flywheel、GPT Researcher、Graphiti、continuous-eval等项目的深入分析，我们提炼出了适用于学术影响力预测系统的架构模式和最佳实践。

**关键词**: 多智能体系统、评估飞轮、知识图谱、学术推荐、引用预测、持续改进

---

## 目录

1. [多智能体编排框架](#1-多智能体编排框架)
2. [评估反馈循环系统](#2-评估反馈循环系统)
3. [研究自动化工具](#3-研究自动化工具)
4. [知识图谱实现](#4-知识图谱实现)
5. [学术分析工具](#5-学术分析工具)
6. [飞轮模式提取](#6-飞轮模式提取)
7. [架构设计建议](#7-架构设计建议)
8. [技术选型建议](#8-技术选型建议)

---

## 1. 多智能体编排框架

### 1.1 CrewAI - 双模式架构

**项目地址**: https://github.com/crewAIInc/crewAI

**核心特性**:

CrewAI提供了两个互补的概念来构建复杂的AI系统：

#### 1.1.1 Crews（团队）- 自主协作

```python
# Crew架构模式
Crew = {
    "agents": [
        ConservativeAgent(role="历史数据分析"),
        RadicalAgent(role="创新信号识别"),
        TheoryAgent(role="理论严谨性"),
        ApplicationAgent(role="应用价值")
    ],
    "tasks": ["预测论文影响力", "评估研究质量"],
    "process": "hierarchical"  # 或 "sequential"
}
```

**关键设计**：
- **Role-based**: 每个Agent有明确的角色、目标、背景故事
- **Autonomous Collaboration**: Agent之间自主协作完成任务
- **Hierarchical Process**: 支持层级式任务流程（Manager → Workers）

#### 1.1.2 Flows（流程）- 事件驱动控制

```python
# Flow架构模式
Flow = {
    "events": [
        "NewPaperArrived",
        "CitationDataUpdated",
        "AltmetricChanged"
    ],
    "transitions": {
        "NewPaperArrived": ["AnalyzePaper", "GeneratePrediction"],
        "CitationDataUpdated": ["ValidatePrediction", "UpdateReputation"]
    }
}
```

**关键设计**：
- **Event-Driven**: 基于事件触发工作流
- **Control Flow**: 精确控制执行顺序、分支和循环
- **State Management**: 维护跨Agent的共享状态

**对学术飞轮的启示**：

```python
# 应用到学术飞轮
AcademicFlywheelCrew = {
    "agents": {
        "collector": "收集新论文（RSS/API）",
        "analyzer": "提取进化生物学特征",
        "predictor_conservative": "基于历史数据预测",
        "predictor_radical": "基于创新信号预测",
        "validator": "验证预测准确性",
        "reputation_manager": "更新智能体声誉"
    },
    "flows": {
        "daily_collection": "Collector → Analyzer → Predictors → Ensemble",
        "monthly_validation": "获取真实数据 → Validator → UpdateReputation"
    }
}
```

**可借鉴的代码模式**:

```python
from crewai import Agent, Task, Crew, Process

# 定义保守派智能体
conservative_agent = Agent(
    role="保守派预测专家",
    goal="基于历史引用数据预测论文影响力",
    backstory="""你是一位经验丰富的科学计量学专家，
    相信历史模式是预测未来的最佳指标。""",
    verbose=True,
    allow_delegation=False
)

# 定义激进派智能体
radical_agent = Agent(
    role="激进派预测专家",
    goal="识别可能突破传统引用模式的创新论文",
    backstory="""你是一位科学史研究者，专注于识别那些
    被低估但可能产生重大影响的突破性研究。""",
    verbose=True,
    allow_delegation=False
)

# 定义任务
prediction_task = Task(
    description="""分析论文 {paper_id} 的元数据、摘要和早期引用，
    预测其5年后的引用数范围，并给出置信度评分。""",
    expected_output="预测结果和置信度评分",
    agent=conservative_agent  # 主Agent
)

# 创建团队
prediction_crew = Crew(
    agents=[conservative_agent, radical_agent],
    tasks=[prediction_task],
    process=Process.hierarchical,
    manager_llm="gpt-4"  # 管理者使用更强大的模型
)
```

---

## 2. 评估反馈循环系统

### 2.1 OpenAI Evaluation Flywheel

**项目地址**: https://github.com/openai/openai-cookbook/tree/main/examples/evaluation

**核心方法论 - 三阶段循环**:

```
┌─────────────────────────────────────────────────────────┐
│                   EVALUATION FLYWHEEL                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐             │
│   │ ANALYZE │ →  │ MEASURE │ →  │ IMPROVE │             │
│   └─────────┘    └─────────┘    └─────────┘             │
│        ↑              ↑               ↑                  │
│        └──────────────┴───────────────┘                  │
│                    Continuous Loop                       │
└─────────────────────────────────────────────────────────┘
```

#### 2.1.1 Phase 1: Analyze（分析）

**目的**: 定性理解系统行为

**步骤**:
1. **Open Coding**: 开放式编码，记录所有观察到的模式
2. **Axial Coding**: 轴心编码，识别类别之间的关系
3. **Pattern Recognition**: 识别系统性问题

**应用到学术飞轮**:

```python
# 分析阶段示例
def analyze_prediction_patterns():
    """分析预测模式的定性分析"""
    patterns = {
        "高估论文类型": [
            "来自知名期刊",
            "作者h-index高",
            "已有早期引用"
        ],
        "低估论文类型": [
            "跨学科研究",
            "方法论创新",
            "小型机构发表"
        ],
        "系统性偏差": {
            "领域偏见": "生物医学预测偏高",
            "时间偏见": "近期论文预测不准",
            "语言偏见": "非英语论文被低估"
        }
    }
    return patterns
```

#### 2.1.2 Phase 2: Measure（测量）

**目的**: 创建量化指标

**关键组件**:

1. **Golden Dataset**: 创建标准测试集
   ```python
   golden_dataset = {
       "papers": [
           {
               "id": "doi:10.1234/example",
               "metadata": {...},
               "true_citations_5yr": 150,  # 真实值
               "prediction_conservative": 120,
               "prediction_radical": 180,
               "altmetric_score": 85
           }
       ],
       "split": {
           "train": "2015-2019",
           "test": "2020-2021",
           "validation": "2022"
       }
   }
   ```

2. **Automated Graders**: 自动化评分器
   ```python
   def citation_prediction_grader(prediction, ground_truth):
       """引用预测评分器"""
       error = abs(prediction - ground_truth)
       if error < 10:
           return "excellent"
       elif error < 30:
           return "good"
       elif error < 50:
           return "fair"
       else:
           return "poor"

   def classification_grader(predicted_class, true_class):
       """分类任务评分器"""
       return {
           "accuracy": predicted_class == true_class,
           "confusion_matrix": build_confusion_matrix(...)
       }
   ```

3. **Metrics Suite**: 指标套件
   ```python
   metrics = {
       "回归指标": ["R²", "RMSE", "MAE", "Spearmanρ"],
       "分类指标": ["Precision", "Recall", "F1", "AUC-ROC"],
       "排序指标": ["NDCG", "MRR", "Precision@k"],
       "校准指标": ["Calibration Error", "Brier Score"]
   }
   ```

#### 2.1.3 Phase 3: Improve（改进）

**目的**: 针对性改进

**策略**:

1. **Targeted Prompt Improvements**: 针对性提示词改进
   ```python
   # 改进前
   prompt_v1 = "预测这篇论文的引用数"

   # 改进后 - 添加具体指导
   prompt_v2 = """
   预测这篇论文5年后的引用数。考虑以下因素：
   1. 论文的进化生物学相关性和创新性
   2. 作者的历史引用记录
   3. 期刊的影响力和受众
   4. 早期Altmetric评分
   5. 跨学科引用潜力

   给出预测值和70%置信区间。
   """
   ```

2. **Feature Engineering**: 特征工程优化
   ```python
   features_v1 = ["authors_hindex", "journal_if", "early_citations"]

   features_v2 = [
       "authors_hindex",
       "journal_if",
       "early_citations",
       "altmetric_score",          # 新增
       "cross_disciplinary_indicator",  # 新增
       "method_novelty_score",     # 新增
       "network_centrality"        # 新增
   ]
   ```

3. **A/B Testing**: A/B测试
   ```python
   # 运行对比实验
   results = {
       "baseline": evaluate(model_v1, test_set),
       "with_altmetric": evaluate(model_v2, test_set),
       "with_network": evaluate(model_v3, test_set)
   }

   # 选择最佳模型
   best_model = max(results.items(), key=lambda x: x[1]["r2"])
   ```

**对学术飞轮的启示**:

```python
class AcademicFlywheelEvaluation:
    """学术飞轮评估系统"""

    def __init__(self):
        self.phase = "analyze"
        self.patterns = []
        self.metrics_history = []

    def run_flywheel_cycle(self, month):
        """运行完整的飞轮循环"""

        # Phase 1: Analyze
        if self.phase == "analyze":
            patterns = self.qualitative_analysis()
            self.patterns.extend(patterns)
            self.phase = "measure"

        # Phase 2: Measure
        elif self.phase == "measure":
            metrics = self.quantitative_evaluation()
            self.metrics_history.append(metrics)

            # 如果性能达标，继续改进
            if metrics["r2"] < 0.75:
                self.phase = "improve"
            else:
                print("目标已达成！")
                self.phase = "analyze"  # 重新开始

        # Phase 3: Improve
        elif self.phase == "improve":
            improvements = self.targeted_improvements()
            self.apply_improvements(improvements)
            self.phase = "measure"  # 重新测量

    def qualitative_analysis(self):
        """定性分析"""
        # 分析预测失败案例
        failures = self.get_worst_predictions(n=50)

        patterns = {
            "sleeping_beauties": [
                p for p in failures
                if p["early_citations"] < 5 and p["late_citations"] > 100
            ],
            "overhyped_papers": [
                p for p in failures
                if p["altmetric_score"] > 90 and p["citations"] < 20
            ],
            "cross_disciplinary_hits": [
                p for p in failures
                if p["discipline_count"] > 3
            ]
        }
        return patterns

    def quantitative_evaluation(self):
        """定量评估"""
        predictions = self.get_all_predictions()
        ground_truth = self.get_ground_truth()

        metrics = {
            "r2": r2_score(ground_truth, predictions),
            "rmse": mean_squared_error(ground_truth, predictions),
            "mae": mean_absolute_error(ground_truth, predictions),
            "spearman": spearmanr(ground_truth, predictions)[0],
            "by_quartile": {
                "q1_top": evaluate_top_quartile(predictions),
                "q4_bottom": evaluate_bottom_quartile(predictions)
            }
        }
        return metrics

    def targeted_improvements(self):
        """针对性改进"""
        # 基于分析结果生成改进建议
        improvements = []

        if "sleeping_beauties" in self.patterns:
            improvements.append({
                "type": "feature",
                "action": "add_method_novelty_detector",
                "rationale": "识别方法创新论文"
            })

        if "cross_disciplinary_hits" in self.patterns:
            improvements.append({
                "type": "feature",
                "action": "add_cross_discipline_indicator",
                "rationale": "检测跨学科研究"
            })

        return improvements
```

---

### 2.2 continuous-eval - 模块化评估框架

**项目地址**: https://github.com/relari-ai/continuous-eval

**核心特性**:

#### 2.2.1 Pipeline-Level Metrics（流水线级指标）

```python
from continuous_eval import EvaluationPipeline

# 定义评估流水线
pipeline = EvaluationPipeline(
    metrics=[
        "CitationAccuracy",
        "AltmetricCorrelation",
        "RankingQuality",
        "CalibrationScore"
    ]
)

# 评估整个预测流水线
results = pipeline.evaluate(
    predictor=academic_flywheel.predictor,
    dataset=test_dataset,
    aggregations=["mean", "std", "by_quartile"]
)
```

#### 2.2.2 Custom LLM-as-a-Judge（自定义LLM评判）

```python
from continuous_eval import LLMJudge

# 定义自定义评判标准
importance_judge = LLMJudge(
    name="importance_assessment",
    criteria={
        "scientific_rigor": "研究方法的严谨性",
        "innovation": "理论或方法的创新程度",
        "reproducibility": "结果的可复现性",
        "clarity": "表达的清晰度"
    },
    prompt_template="""
    评估以下进化生物学论文的重要性：

    标题：{title}
    摘要：{abstract}

    请按以下标准评分（1-10分）：
    - 科学严谨性：{scientific_rigor}
    - 创新性：{innovation}
    - 可复现性：{reproducibility}
    - 清晰度：{clarity}

    总分和理由：
    """
)

# 评判论文
assessment = importance_judge.evaluate(paper_data)
```

#### 2.2.3 Probabilistic Evaluation（概率化评估）

```python
from continuous_eval import ProbabilisticMetrics

# 使用概率化指标评估预测不确定性
prob_metrics = ProbabilisticMetrics(
    metrics=[
        "ExpectedCalibrationError",
        "BrierScore",
        "ConfidenceIntervalCoverage"
    ]
)

# 评估预测的置信区间质量
calibration_results = prob_metrics.evaluate(
    predictions=predictions_with_intervals,
    ground_truth=true_citations
)
```

**对学术飞轮的启示**:

```python
class AcademicFlywheelMetrics:
    """学术飞轮评估指标"""

    def __init__(self):
        self.metrics_suite = {
            # 基础预测指标
            "prediction_metrics": [
                "R²",
                "RMSE",
                "MAE",
                "Spearmanρ",
                "NDCG@10"
            ],

            # 分类指标（高被引/低被引）
            "classification_metrics": [
                "Precision",
                "Recall",
                "F1",
                "AUC-ROC",
                "ConfusionMatrix"
            ],

            # 排序指标
            "ranking_metrics": [
                "MRR",
                "NDCG@5",
                "NDCG@10",
                "Precision@k"
            ],

            # 校准指标
            "calibration_metrics": [
                "ExpectedCalibrationError",
                "BrierScore",
                "ConfidenceIntervalCoverage"
            ],

            # 公平性指标
            "fairness_metrics": [
                "DemographicParity",  # 不同领域的公平性
                "EqualizedOpportunities",
                "CalibrationBySubgroup"
            ],

            # 发现能力指标
            "discovery_metrics": [
                "NoveltyScore",  # 推荐论文的新颖度
                "DiversityScore",  # 推荐的多样性
                "SerendipityScore"  # 意外发现率
            ]
        }

    def evaluate_comprehensive(self, predictions, ground_truth):
        """综合评估"""
        results = {}

        for category, metrics in self.metrics_suite.items():
            results[category] = {}
            for metric in metrics:
                results[category][metric] = self.compute_metric(
                    metric, predictions, ground_truth
                )

        return results

    def compute_metric(self, metric_name, predictions, ground_truth):
        """计算单个指标"""
        if metric_name == "R²":
            return r2_score(ground_truth, predictions)
        elif metric_name == "NDCG@10":
            return ndcg_score(ground_truth, predictions, k=10)
        # ... 其他指标
```

---

## 3. 研究自动化工具

### 3.1 GPT Researcher - Plan-and-Execute架构

**项目地址**: https://github.com/assafelovic/gpt-researcher

**核心架构**:

```
┌──────────────────────────────────────────────────────────┐
│                    GPT RESEARCHER                         │
├──────────────────────────────────────────────────────────┤
│                                                           │
│   ┌──────────┐    ┌──────────────┐    ┌──────────────┐  │
│   │ PLANNER  │ →  │ EXECUTION    │ →  │ PUBLISHER    │  │
│   │          │    │ AGENTS       │    │              │  │
│   └──────────┘    └──────────────┘    └──────────────┘  │
│                          ↓                                 │
│                   ┌──────────────┐                        │
│                   │ 20+ SOURCES  │                        │
│                   │ - Google     │                        │
│                   │ - ArXiv      │                        │
│                   │ - PubMed     │                        │
│                   │ - Semantic   │                        │
│                   │   Scholar    │                        │
│                   └──────────────┘                        │
└──────────────────────────────────────────────────────────┘
```

#### 3.1.1 Planner（规划器）

```python
# Planner生成研究问题
research_questions = planner.generate(
    topic="进化生物学中的性选择理论最新进展",
    context="2023-2024年的研究",
    max_questions=10
)

# 输出示例
questions = [
    "性选择理论在果蝇研究中有哪些新发现？",
    "性冲突如何影响物种形成？",
    "配偶选择的行为生态学机制是什么？",
    # ...
]
```

#### 3.1.2 Execution Agents（执行智能体）

```python
# 并行执行多个研究任务
async def run_research_agents():
    tasks = [
        researcher_agent.search("ArXiv", questions[0]),
        researcher_agent.search("PubMed", questions[1]),
        researcher_agent.search("Semantic Scholar", questions[2]),
        # ... 更多并行任务
    ]

    results = await asyncio.gather(*tasks)
    return aggregate_results(results)
```

#### 3.1.3 Publisher（发布器）

```python
# 生成综合报告
report = publisher.generate(
    research_results=aggregated_results,
    format="markdown",
    sections=[
        "Executive Summary",
        "Key Findings",
        "Detailed Analysis",
        "Methodology",
        "References"
    ]
)
```

**关键特性**:

1. **多源聚合**: 从20+个来源收集信息
2. **并行执行**: 多个Agent并行工作
3. **深度报告**: 生成2000+字的详细报告

**对学术飞轮的启示**:

```python
class AcademicPaperResearcher:
    """学术论文研究智能体"""

    def __init__(self):
        self.planner = ResearchPlanner()
        self.agents = {
            "metadata_collector": MetadataCollectorAgent(),
            "citation_analyzer": CitationAnalyzerAgent(),
            "content_summarizer": ContentSummarizerAgent(),
            "impact_assessor": ImpactAssessorAgent()
        }
        self.publisher = ReportPublisher()

    async def research_paper(self, doi: str):
        """研究单篇论文"""

        # Phase 1: Planning
        research_plan = self.planner.plan(
            target=f"分析论文 {doi}",
            aspects=[
                "基础元数据",
                "引用网络分析",
                "内容语义理解",
                "影响力评估"
            ]
        )

        # Phase 2: Parallel Execution
        tasks = [
            self.agents["metadata_collector"].collect(doi),
            self.agents["citation_analyzer"].analyze(doi),
            self.agents["content_summarizer"].summarize(doi),
            self.agents["impact_assessor"].assess(doi)
        ]

        results = await asyncio.gather(*tasks)

        # Phase 3: Publishing
        report = self.publisher.compile({
            "metadata": results[0],
            "citations": results[1],
            "summary": results[2],
            "impact": results[3]
        })

        return report
```

---

### 3.2 AutoAgent - 零代码智能体构建

**项目地址**: https://github.com/HKUDS/AutoAgent

**核心特性**:

#### 3.2.1 Natural Language Agent Building

```python
# 用自然语言描述构建Agent
agent_description = """
你是一个进化生物学论文分析专家。你的任务是：
1. 从论文摘要中提取关键发现
2. 识别研究方法和进化尺度
3. 评估论文的重要性（0-100分）
"""

# AutoAgent自动构建
agent = AutoAgent.from_description(agent_description)
```

#### 3.2.2 Self-Managing Workflow

```python
# Agent自动管理工作流
result = agent.run(
    task="分析这篇论文",
    input_data={
        "title": "...",
        "abstract": "..."
    }
)

# Agent自动：
# 1. 分解任务为子任务
# 2. 选择合适的工具
# 3. 执行并验证结果
# 4. 聚合最终答案
```

**对学术飞轮的启示**:

```python
# 可以快速构建原型Agent
conservative_predictor = AutoAgent.from_description("""
你是一位保守派的学术影响力预测专家。你的预测基于：
1. 历史引用模式
2. 作者的h-index
3. 期刊的影响因子
4. 早期引用数量

请给出5年后引用数的预测值和70%置信区间。
""")

radical_predictor = AutoAgent.from_description("""
你是一位激进派的学术影响力预测专家。你关注：
1. 方法的创新性
2. 理论的突破性
3. 跨学科潜力
4. Sleeping Beauty特征

请给出5年后引用数的预测值，并标注"高潜力"论文。
""")
```

---

## 4. 知识图谱实现

### 4.1 Graphiti - 时序知识图谱

**项目地址**: https://github.com/getzep/graphiti

**核心特性**:

#### 4.1.1 Temporal Awareness（时序感知）

```python
# Graphiti跟踪知识的时间维度
graph_events = [
    {
        "timestamp": "2024-01-15",
        "event": "Paper Published",
        "entity": "doi:10.1234/example",
        "attributes": {
            "title": "...",
            "authors": ["..."],
            "journal": "Nature"
        }
    },
    {
        "timestamp": "2024-02-01",
        "event": "First Citation",
        "relationship": "cites",
        "from": "doi:10.5678/newpaper",
        "to": "doi:10.1234/example"
    },
    {
        "timestamp": "2024-06-01",
        "event": "Altmetric Spike",
        "entity": "doi:10.1234/example",
        "attributes": {
            "altmetric_score": 150,
            "twitter_mentions": 89,
            "news_mentions": 5
        }
    }
]

# 插入图谱
for event in graph_events:
    graphiti.add_event(event)
```

#### 4.1.2 Bi-Temporal Model（双时序模型）

```python
# 双时序：事件时间 + 摄入时间
graph_node = {
    "entity_id": "paper:123",
    "event_time": "2024-01-15T10:00:00Z",  # 事件发生时间
    "ingestion_time": "2024-01-15T11:30:00Z",  # 系统摄入时间
    "valid_from": "2024-01-15T11:30:00Z",  # 有效期开始
    "valid_to": None  # 仍然有效
}
```

#### 4.1.3 Incremental Updates（增量更新）

```python
# 增量更新 vs 批量处理
def update_paper_citations(new_citation_data):
    """增量更新引用数据"""

    # 不需要重建整个图谱
    for citation in new_citation_data:
        graphiti.add_edge(
            from_entity=citation["citing_paper"],
            to_entity=citation["cited_paper"],
            edge_type="cites",
            timestamp=citation["date"],
            properties={
                "context": citation.get("context"),
                "section": citation.get("section")  # intro, methods, etc.
            }
        )

    # 图谱自动更新：索引、向量嵌入、统计信息
```

**对学术飞轮的启示**:

```python
class AcademicKnowledgeGraph:
    """学术知识图谱"""

    def __init__(self):
        self.graphiti = Graphiti(
            store="Neo4j",  # 或其他图数据库
            embedding_model="text-embedding-3-small"
        )

    def add_paper(self, paper_data):
        """添加论文到图谱"""

        # 添加论文节点
        self.graphiti.add_node(
            entity_id=f"paper:{paper_data['doi']}",
            entity_type="Paper",
            attributes={
                "title": paper_data["title"],
                "abstract": paper_data["abstract"],
                "publication_date": paper_data["date"],
                "journal": paper_data["journal"]
            }
        )

        # 添加作者节点和关系
        for author in paper_data["authors"]:
            self.graphiti.add_node(
                entity_id=f"author:{author['name']}",
                entity_type="Author",
                attributes={
                    "name": author["name"],
                    "affiliation": author.get("affiliation")
                }
            )

            self.graphiti.add_edge(
                from_entity=f"author:{author['name']}",
                to_entity=f"paper:{paper_data['doi']}",
                edge_type="authored",
                timestamp=paper_data["date"]
            )

    def add_citation(self, citing_doi, cited_doi, citation_context=None):
        """添加引用关系"""

        self.graphiti.add_edge(
            from_entity=f"paper:{citing_doi}",
            to_entity=f"paper:{cited_doi}",
            edge_type="cites",
            attributes={
                "context": citation_context
            }
        )

    def query_sleeping_beauties(self):
        """查询潜在的Sleeping Beauty论文"""

        # Cypher查询示例
        query = """
        MATCH (p:Paper)
        WHERE p.publication_date > datetime('2019-01-01')
        WITH p, size((p)<-[:cites]-()) as citations
        WHERE citations < 5  // 早期引用少
        MATCH (p)-[:cites]->(method_paper:Paper)
        WHERE method_paper.keywords CONTAINS "methodology"
        WITH p, count(method_paper) as method_citations
        WHERE method_citations > 0  // 引用了方法论文
        RETURN p, citations, method_citations
        ORDER BY method_citations DESC
        LIMIT 20
        """

        return self.graphiti.execute_query(query)

    def get_paper_centrality(self, paper_doi):
        """计算论文的中心性"""

        # PageRank
        pagerank = self.graphiti.compute_pagerank(
            entity_id=f"paper:{paper_doi}"
        )

        # Betweenness Centrality
        betweenness = self.graphiti.compute_betweenness(
            entity_id=f"paper:{paper_doi}"
        )

        # Citation Count
        citation_count = self.graphiti.get_in_degree(
            entity_id=f"paper:{paper_doi}",
            edge_type="cites"
        )

        return {
            "pagerank": pagerank,
            "betweenness": betweenness,
            "citation_count": citation_count
        }

    def find_similar_papers(self, paper_doi, top_k=10):
        """基于图谱结构和内容找相似论文"""

        # 1. 语义相似（基于摘要嵌入）
        semantic_similar = self.graphiti.similarity_search(
            entity_id=f"paper:{paper_doi}",
            attribute="abstract",
            top_k=top_k
        )

        # 2. 结构相似（基于引用模式）
        structural_similar = self.graphiti.structural_similarity(
            entity_id=f"paper:{paper_doi}",
            top_k=top_k
        )

        # 3. 融合排序
        combined = merge_and_rerank(
            semantic_similar,
            structural_similar,
            weights=[0.6, 0.4]
        )

        return combined[:top_k]
```

---

## 5. 学术分析工具

### 5.1 pyBibX - 文献计量分析库

**项目地址**: https://github.com/Valdecy/pyBibX

**核心功能**:

#### 5.1.1 数据导入与处理

```python
from pybibx import BibDatabase

# 导入数据
db = BibDatabase()

# 支持多个数据源
db.add_bibtex("scopus_export.bib")  # Scopus
db.add_bibtex("wos_export.bib")     # Web of Science
db.add_pubmed("pubmed_export.txt")  # PubMed

# 去重
db.remove_duplicates(field="doi")
db.remove_duplicates(field="title")

# 合并相同实体的不同条目
db.merge_authors()
db.merge_institutions()
db.merge_sources()
```

#### 5.1.2 探索性数据分析（EDA）

```python
# 生成EDA报告
eda_report = db.eda_report()

print(f"""
出版物时间跨度: {eda_report['timespan']}
国家数: {eda_report['n_countries']}
机构数: {eda_report['n_institutions']}
期刊数: {eda_report['n_sources']}
总引用数: {eda_report['total_citations']}
平均每篇引用: {eda_report['avg_citations_per_document']}
最大h-index: {eda_report['max_h_index']}
""")
```

#### 5.1.3 引用分析

```python
# 引用轨迹图
db.citation_trajectory_plot(
    papers=["paper1", "paper2", "paper3"]
)

# 引用矩阵
citation_matrix = db.citation_matrix(
    papers=["paper1", "paper2", "paper3"]
)

# RPYS（Reference Publication Year Spectroscopy）
db.rpys_plot()  # 识别影响文献发表年份的峰值

# Sleeping Beauty识别
sleeping_beauties = db.find_sleeping_beauties(
    sleeping_threshold=5,  # 5年无引用
    awakening_threshold=50  # 突然获得50+引用
)

# Prince识别（唤醒Sleeping Beauty的论文）
princes = db.find_princes(sleeping_beauties)
```

#### 5.1.4 网络分析

```python
# 合作网络
db.collaboration_plot(
    by="authors",  # 或 "countries", "institutions"
    top_n=20
)

# Hubs & Authorities
hubs_auth = db.hubs_and_authorities(
    by_decade=True,
    top_k=10
)

# 引用共现网络
db.co_citation_network(
    target_paper="paper1",
    top_n=20
)
```

#### 5.1.5 AI功能

```python
# 主题建模
topics = db.topic_modeling(
    text_field="abstract",
    model="BERTopic",
    n_topics=10
)

# 可视化主题分布
db.visualize_topics(topics)

# 查看最具代表性的文档
representative_docs = db.get_representative_documents(
    topics,
    n_per_topic=5
)

# 文本摘要
summary = db.summarize(
    papers=paper_list,
    method="PEGASUS"  # 或 "chatGPT", "Gemini", "BERT"
)

# 向量嵌入
embeddings = db.create_sentence_embeddings(
    text_field="abstract",
    model="all-MiniLM-L6-v2"
)

# 基于嵌入找相似论文
similar_papers = db.find_similar_by_embedding(
    query_paper="paper1",
    top_k=10
)
```

**对学术飞轮的启示**:

```python
from pybibx import BibDatabase
import sqlite3

class EvolutionaryBiologyAnalyzer:
    """进化生物学文献分析器"""

    def __init__(self, db_path="evo_flywheel.db"):
        self.bib_db = BibDatabase()
        self.sqlite_conn = sqlite3.connect(db_path)

    def export_to_bibtex(self, papers_df, output_path):
        """从SQLite导出为BibTeX格式"""

        bibtex_entries = []
        for _, row in papers_df.iterrows():
            entry = self._create_bibtex_entry(row)
            bibtex_entries.append(entry)

        with open(output_path, 'w') as f:
            f.write('\n'.join(bibtex_entries))

    def analyze_collection(self, start_date, end_date):
        """分析指定时间范围的论文集合"""

        # 从SQLite获取数据
        papers = self._get_papers_by_date(start_date, end_date)

        # 导出为BibTeX
        self.export_to_bibtex(papers, "temp_collection.bib")

        # 导入pyBibX
        self.bib_db.add_bibtex("temp_collection.bib")

        # 生成报告
        report = {
            "eda": self.bib_db.eda_report(),
            "sleeping_beauties": self.bib_db.find_sleeping_beauties(),
            "hubs_authorities": self.bib_db.hubs_and_authorities(),
            "topics": self.bib_db.topic_modeling()
        }

        return report

    def identify_undercited_gems(self):
        """识别被低估的论文"""

        # 使用pyBibX的Sleeping Beauty检测
        sleeping_beauties = self.bib_db.find_sleeping_beauties(
            sleeping_threshold=3,
            awakening_threshold=30
        )

        # 结合我们的预测
        gems = []
        for sb in sleeping_beauties:
            paper_id = sb["id"]

            # 查询我们的预测
            prediction = self._get_prediction(paper_id)

            # 如果我们的预测高于当前引用
            if prediction["predicted_citations"] > sb["current_citations"] * 2:
                gems.append({
                    "paper": sb,
                    "prediction": prediction,
                    "reason": "高潜力但当前被低估"
                })

        return gems

    def update_knowledge_graph(self, papers):
        """更新知识图谱"""

        for paper in papers:
            # 1. 添加论文节点
            self._add_paper_to_graph(paper)

            # 2. 添加引用关系
            for ref in paper.get("references", []):
                self._add_citation_to_graph(paper["id"], ref)

            # 3. 计算中心性指标
            centrality = self._compute_centrality(paper["id"])

            # 4. 更新SQLite
            self._update_paper_metrics(
                paper["id"],
                {
                    "pagerank": centrality["pagerank"],
                    "betweenness": centrality["betweenness"],
                    "hubs_score": centrality["hubs"]
                }
            )
```

---

## 6. 飞轮模式提取

### 6.1 评估飞轮模式（OpenAI）

```python
class EvaluationFlywheel:
    """评估飞轮 - 持续改进循环"""

    def run_cycle(self, iteration):
        """运行一个完整的飞轮周期"""

        # Phase 1: Analyze
        if self.should_analyze(iteration):
            patterns = self.analyze_failures()
            self.hypotheses = self.generate_hypotheses(patterns)

        # Phase 2: Measure
        metrics = self.measure_performance(
            test_set=self.get_golden_dataset()
        )
        self.metrics_history.append(metrics)

        # Phase 3: Improve
        if self.should_improve(metrics):
            improvements = self.design_improvements(
                hypotheses=self.hypotheses,
                current_metrics=metrics
            )
            self.apply_improvements(improvements)

        return metrics

    def analyze_failures(self):
        """分析预测失败的模式"""
        # 收集最差预测
        worst_predictions = self.get_worst_predictions(n=100)

        # 识别模式
        patterns = {
            "domain_bias": self.detect_domain_bias(worst_predictions),
            "temporal_drift": self.detect_temporal_drift(worst_predictions),
            "missing_features": self.identify_missing_features(worst_predictions)
        }

        return patterns

    def generate_hypotheses(self, patterns):
        """基于模式生成改进假设"""
        hypotheses = []

        if patterns["domain_bias"] > 0.3:
            hypotheses.append({
                "type": "domain_normalization",
                "priority": "high",
                "description": "领域归一化可以减少偏见"
            })

        if patterns["temporal_drift"]:
            hypotheses.append({
                "type": "temporal_features",
                "priority": "medium",
                "description": "添加时间衰减因子"
            })

        return hypotheses

    def measure_performance(self, test_set):
        """量化评估性能"""
        predictions = self.predict(test_set)

        metrics = {
            "overall": {
                "r2": r2_score(test_set.targets, predictions),
                "rmse": mean_squared_error(test_set.targets, predictions),
                "mae": mean_absolute_error(test_set.targets, predictions)
            },
            "by_subgroup": {
                "by_journal": self.evaluate_by_subgroup(test_set, "journal"),
                "by_year": self.evaluate_by_subgroup(test_set, "year"),
                "by_quartile": self.evaluate_by_quartiles(test_set)
            },
            "calibration": self.evaluate_calibration(predictions, test_set.targets)
        }

        return metrics

    def design_improvements(self, hypotheses, current_metrics):
        """设计针对性改进"""
        improvements = []

        for h in hypotheses:
            if h["type"] == "domain_normalization":
                improvements.append({
                    "action": "add_domain_normalization",
                    "implementation": """
                    def normalize_by_domain(predictions, domain):
                        domain_mean = get_domain_mean(domain)
                        global_mean = get_global_mean()
                        return predictions * (global_mean / domain_mean)
                    """,
                    "expected_impact": "+0.05 R²"
                })

        return improvements

    def apply_improvements(self, improvements):
        """应用改进"""
        for imp in improvements:
            if imp["action"] == "add_domain_normalization":
                self.model.add_normalization_layer()
            elif imp["action"] == "add_temporal_features":
                self.model.add_temporal_features()
```

---

### 6.2 数据飞轮模式

```python
class DataFlywheel:
    """数据飞轮 - 用户反馈驱动改进"""

    def __init__(self):
        self.user_feedback = []
        self.model_versions = []

    def collect_feedback(self, prediction_id, user_rating, user_comment):
        """收集用户反馈"""
        self.user_feedback.append({
            "prediction_id": prediction_id,
            "rating": user_rating,  # 1-5星
            "comment": user_comment,
            "timestamp": datetime.now()
        })

    def analyze_feedback(self):
        """分析用户反馈"""
        # 识别系统性问题
        low_rated = [f for f in self.user_feedback if f["rating"] <= 2]

        issues = {
            "overconfident": self.check_overconfidence(low_rated),
            "underconfident": self.check_underconfidence(low_rated),
            "biased_domains": self.identify_biased_domains(low_rated)
        }

        return issues

    def generate_training_data(self):
        """从反馈生成训练数据"""
        training_samples = []

        for feedback in self.user_feedback:
            if feedback["rating"] >= 4:
                # 高评分 → 正样本
                training_samples.append({
                    "paper": self.get_paper(feedback["prediction_id"]),
                    "label": "high_impact",
                    "weight": 1.0
                })
            elif feedback["rating"] <= 2:
                # 低评分 → 负样本
                training_samples.append({
                    "paper": self.get_paper(feedback["prediction_id"]),
                    "label": "low_impact",
                    "weight": 1.0
                })

        return training_samples

    def retrain_with_feedback(self):
        """使用反馈数据重新训练"""
        new_data = self.generate_training_data()

        # 增量训练
        new_model = self.model.train_incremental(
            new_data=new_data,
            old_model=self.current_model
        )

        # 评估新模型
        old_performance = self.evaluate(self.current_model)
        new_performance = self.evaluate(new_model)

        # 如果有改进，部署
        if new_performance["f1"] > old_performance["f1"]:
            self.deploy_model(new_model)
            self.model_versions.append({
                "version": len(self.model_versions) + 1,
                "performance": new_performance,
                "trained_on": len(new_data),
                "timestamp": datetime.now()
            })
```

---

### 6.3 预测市场飞轮模式

```python
class PredictionMarketFlywheel:
    """预测市场飞轮 - 集体智慧驱动"""

    def __init__(self):
        self.agents = {}  # 智能体注册表
        self.markets = {}  # 预测市场
        self.reputation_scores = {}

    def register_agent(self, agent_id, agent_type):
        """注册预测智能体"""
        self.agents[agent_id] = {
            "type": agent_type,
            "reputation": 1000,  # 初始声誉
            "predictions": [],
            "accuracy_history": []
        }

    def create_market(self, paper_id, deadline):
        """为论文创建预测市场"""
        self.markets[paper_id] = {
            "paper_id": paper_id,
            "deadline": deadline,
            "predictions": {},  # agent_id → prediction
            "outcome": None,  # 真实结果（到期后揭晓）
            "participants": []
        }

    def submit_prediction(self, agent_id, paper_id, prediction, confidence):
        """智能体提交预测"""
        if paper_id not in self.markets:
            raise ValueError("Market not found")

        # 记录预测
        self.markets[paper_id]["predictions"][agent_id] = {
            "prediction": prediction,
            "confidence": confidence,
            "timestamp": datetime.now()
        }

        self.markets[paper_id]["participants"].append(agent_id)

    def resolve_market(self, paper_id, true_citations):
        """结算市场（获得真实数据后）"""
        market = self.markets[paper_id]
        market["outcome"] = true_citations

        # 计算每个智能体的准确度
        for agent_id, pred_data in market["predictions"].items():
            predicted = pred_data["prediction"]
            error = abs(predicted - true_citations)

            # 更新声誉
            accuracy = max(0, 1 - error / true_citations)
            self.update_reputation(agent_id, accuracy)

            # 记录历史
            self.agents[agent_id]["accuracy_history"].append(accuracy)

    def update_reputation(self, agent_id, accuracy):
        """更新智能体声誉"""
        agent = self.agents[agent_id]

        # 使用Elo评分系统
        k = 32  # K因子
        expected_score = agent["reputation"] / 1000
        actual_score = accuracy

        new_reputation = agent["reputation"] + k * (actual_score - expected_score)
        agent["reputation"] = max(100, min(2000, new_reputation))

    def ensemble_prediction(self, paper_id):
        """基于市场共识生成集成预测"""
        market = self.markets[paper_id]

        if not market["predictions"]:
            return None

        # 加权平均（权重 = 声誉）
        total_weight = sum(
            self.agents[aid]["reputation"]
            for aid in market["predictions"]
        )

        weighted_prediction = sum(
            pred_data["prediction"] * self.agents[aid]["reputation"]
            for aid, pred_data in market["predictions"].items()
        ) / total_weight

        # 计算置信区间（基于预测分歧度）
        predictions = [
            pred_data["prediction"]
            for pred_data in market["predictions"].values()
        ]
        std = np.std(predictions)

        return {
            "prediction": weighted_prediction,
            "confidence_interval": (
                weighted_prediction - 1.96 * std,
                weighted_prediction + 1.96 * std
            ),
            "disagreement": std,  # 分歧度
            "n_participants": len(market["predictions"])
        }

    def analyze_disagreement_value(self, paper_id):
        """分析分歧度与预测质量的关系"""
        market = self.markets[paper_id]

        if market["outcome"] is None:
            return None  # 市场尚未结算

        # 计算分歧度
        predictions = [
            pred_data["prediction"]
            for pred_data in market["predictions"].values()
        ]
        disagreement = np.std(predictions)

        # 计算共识预测的误差
        consensus = np.mean(predictions)
        error = abs(consensus - market["outcome"])

        return {
            "disagreement": disagreement,
            "error": error,
            "n_participants": len(predictions)
        }

    def get_disagreement_insights(self):
        """获取关于分歧度的洞察"""
        insights = []

        for paper_id, market in self.markets.items():
            if market["outcome"] is None:
                continue

            analysis = self.analyze_disagreement_value(paper_id)
            if analysis:
                insights.append(analysis)

        # 分析相关性
        disagreements = [i["disagreement"] for i in insights]
        errors = [i["error"] for i in insights]

        correlation = np.corrcoef(disagreements, errors)[0, 1]

        return {
            "correlation": correlation,
            "interpretation": (
                "正相关：高分歧度可能意味着高不确定性" if correlation > 0
                else "负相关：高分歧度可能意味着高价值信号"
            ),
            "data": insights
        }
```

---

## 7. 架构设计建议

### 7.1 整体架构

基于开源项目调研，建议采用以下架构：

```
┌────────────────────────────────────────────────────────────────┐
│                    EVO-FLYWHEEL ARCHITECTURE                    │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    DATA LAYER                            │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  SQLite (Metadata)  │  Chroma (Vectors)  │  Graphiti (KG) │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↑                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  MULTI-AGENT LAYER                       │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │ Collector│  │ Analyzer │  │Predictor │  │Validator │  │  │
│  │  │  Agent   │  │  Agent   │  │  Crew    │  │  Agent   │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↑                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                ORCHESTRATION LAYER                        │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  CrewAI Flows → Event-driven workflow coordination        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↑                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 EVALUATION FLYWHEEL                       │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  Analyze → Measure → Improve (Continuous Loop)            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↑                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   PRESENTATION LAYER                      │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  Streamlit UI  │  FastAPI  │  Daily Reports               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

### 7.2 核心模块设计

#### 7.2.1 多智能体预测系统

```python
from crewai import Agent, Task, Crew, Process
from typing import List, Dict

class AcademicPredictionSystem:
    """学术预测系统 - 多智能体架构"""

    def __init__(self):
        self.agents = self._create_agents()
        self.crews = self._create_crews()
        self.flows = self._create_flows()

    def _create_agents(self):
        """创建专业智能体"""
        return {
            # 数据收集智能体
            "collector": Agent(
                role="数据收集专家",
                goal="从RSS和API收集最新的进化生物学论文",
                backstory="你是一位经验丰富的学术数据收集专家...",
                tools=[RSSCollectorTool(), BioRxivAPITool()]
            ),

            # 分析智能体
            "analyzer": Agent(
                role="进化生物学分析专家",
                goal="提取论文的进化生物学特征",
                backstory="你是一位进化生物学研究员...",
                tools=[LLMAnalyzerTool()]
            ),

            # 预测智能体（多个策略）
            "conservative_predictor": Agent(
                role="保守派预测专家",
                goal="基于历史数据预测引用数",
                backstory="你相信历史模式是最佳预测指标...",
                verbose=True
            ),

            "radical_predictor": Agent(
                role="激进派预测专家",
                goal="识别可能突破模式的创新论文",
                backstory="你专注于识别被低估的突破性研究...",
                verbose=True
            ),

            "theory_predictor": Agent(
                role="理论派预测专家",
                goal="评估理论贡献和严谨性",
                backstory="你重视理论框架和方法论...",
                verbose=True
            ),

            "application_predictor": Agent(
                role="应用派预测专家",
                goal="评估实际应用价值",
                backstory="你关注研究的实际应用...",
                verbose=True
            ),

            # 验证智能体
            "validator": Agent(
                role="预测验证专家",
                goal="评估预测准确性并更新声誉",
                backstory="你是一位科学计量学专家...",
                tools=[ValidationTool()]
            )
        }

    def _create_crews(self):
        """创建团队"""
        return {
            "prediction_crew": Crew(
                agents=[
                    self.agents["conservative_predictor"],
                    self.agents["radical_predictor"],
                    self.agents["theory_predictor"],
                    self.agents["application_predictor"]
                ],
                process=Process.hierarchical,
                manager_llm="gpt-4"
            ),

            "daily_collection_crew": Crew(
                agents=[
                    self.agents["collector"],
                    self.agents["analyzer"]
                ],
                process=Process.sequential
            )
        }

    def predict_paper(self, paper_id: str) -> Dict:
        """预测单篇论文的影响力"""

        # 创建任务
        prediction_task = Task(
            description=f"""
            分析论文 {paper_id} 并预测其5年后的引用数。

            请考虑：
            1. 论文的进化生物学相关性
            2. 作者的历史表现
            3. 期刊的影响力
            4. 早期引用和Altmetric
            5. 方法的创新性

            给出：
            - 预测的引用数
            - 70%置信区间
            - 预测理由
            """,
            expected_output="预测结果和理由",
            agent=self.agents["conservative_predictor"]
        )

        # 执行预测
        result = self.crews["prediction_crew"].kickoff(
            tasks=[prediction_task]
        )

        return result

    def ensemble_predictions(self, paper_id: str) -> Dict:
        """集成多个预测智能体的结果"""

        individual_predictions = []

        for agent_name in ["conservative", "radical", "theory", "application"]:
            agent = self.agents[f"{agent_name}_predictor"]
            prediction = self._run_single_prediction(agent, paper_id)
            individual_predictions.append({
                "agent": agent_name,
                "prediction": prediction
            })

        # 集成（加权平均）
        weights = self._compute_agent_weights()
        ensemble_prediction = self._weighted_average(
            individual_predictions,
            weights
        )

        # 计算分歧度
        disagreement = self._compute_disagreement(individual_predictions)

        return {
            "ensemble": ensemble_prediction,
            "individual": individual_predictions,
            "disagreement": disagreement,
            "confidence": self._compute_confidence(disagreement)
        }

    def _compute_agent_weights(self) -> Dict[str, float]:
        """基于历史准确率计算权重"""
        # 从数据库获取每个智能体的历史准确率
        accuracies = self._get_agent_accuracies()

        # 转换为权重
        total = sum(accuracies.values())
        weights = {
            agent: acc / total
            for agent, acc in accuracies.items()
        }

        return weights

    def _compute_disagreement(self, predictions: List[Dict]) -> float:
        """计算预测分歧度"""
        values = [p["prediction"]["value"] for p in predictions]
        return np.std(values)

    def _compute_confidence(self, disagreement: float) -> float:
        """基于分歧度计算置信度"""
        # 分歧度越高，置信度越低
        return max(0, 1 - disagreement / 100)
```

---

#### 7.2.2 评估飞轮系统

```python
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class FlywheelPhase(Enum):
    ANALYZE = "analyze"
    MEASURE = "measure"
    IMPROVE = "improve"

@dataclass
class EvaluationMetrics:
    r2: float
    rmse: float
    mae: float
    spearman: float
    by_quartile: Dict[str, float]
    calibration_error: float

class AcademicFlywheel:
    """学术飞轮 - 持续改进系统"""

    def __init__(self):
        self.phase = FlywheelPhase.ANALYZE
        self.metrics_history: List[EvaluationMetrics] = []
        self.patterns: List[Dict] = []
        self.improvements: List[Dict] = []

    def run_cycle(self, iteration: int) -> EvaluationMetrics:
        """运行一个完整的飞轮周期"""

        print(f"\n{'='*60}")
        print(f"Flywheel Cycle {iteration} - Phase: {self.phase.value}")
        print(f"{'='*60}\n")

        if self.phase == FlywheelPhase.ANALYZE:
            return self._analyze(iteration)
        elif self.phase == FlywheelPhase.MEASURE:
            return self._measure(iteration)
        elif self.phase == FlywheelPhase.IMPROVE:
            return self._improve(iteration)

    def _analyze(self, iteration: int) -> EvaluationMetrics:
        """Phase 1: Analyze - 定性分析"""

        print("🔍 Phase 1: Analyzing prediction patterns...")

        # 1. 获取预测最差的案例
        worst_predictions = self._get_worst_predictions(n=100)

        # 2. 识别模式
        patterns = self._identify_patterns(worst_predictions)
        self.patterns.extend(patterns)

        print(f"  ✓ Identified {len(patterns)} patterns:")
        for p in patterns:
            print(f"    - {p['name']}: {p['description']}")

        # 3. 生成假设
        hypotheses = self._generate_hypotheses(patterns)
        print(f"  ✓ Generated {len(hypotheses)} hypotheses")

        # 转到测量阶段
        self.phase = FlywheelPhase.MEASURE

        # 返回空指标（将在下一阶段计算）
        return None

    def _measure(self, iteration: int) -> EvaluationMetrics:
        """Phase 2: Measure - 定量评估"""

        print("📊 Phase 2: Measuring performance...")

        # 1. 获取测试集
        test_set = self._get_golden_dataset()

        # 2. 运行预测
        predictions = self._predict_all(test_set)

        # 3. 计算指标
        metrics = self._compute_metrics(predictions, test_set)
        self.metrics_history.append(metrics)

        print(f"  ✓ R² = {metrics.r2:.4f}")
        print(f"  ✓ RMSE = {metrics.rmse:.2f}")
        print(f"  ✓ Spearman ρ = {metrics.spearman:.4f}")

        # 4. 决定是否需要改进
        if metrics.r2 < 0.75:
            print(f"  → Performance below target (0.75), entering IMPROVE phase")
            self.phase = FlywheelPhase.IMPROVE
        else:
            print(f"  ✓ Target achieved! Starting new ANALYZE phase")
            self.phase = FlywheelPhase.ANALYZE

        return metrics

    def _improve(self, iteration: int) -> EvaluationMetrics:
        """Phase 3: Improve - 针对性改进"""

        print("🔧 Phase 3: Designing and applying improvements...")

        # 1. 基于分析设计改进
        improvements = self._design_improvements(self.patterns)
        print(f"  ✓ Designed {len(improvements)} improvements")

        # 2. 应用改进
        for imp in improvements:
            self._apply_improvement(imp)
            print(f"    - Applied: {imp['name']}")
            self.improvements.append(imp)

        # 3. 转回测量阶段
        self.phase = FlywheelPhase.MEASURE

        return None

    def _identify_patterns(self, predictions: List[Dict]) -> List[Dict]:
        """识别预测失败的模式"""
        patterns = []

        # 检测Sleeping Beauty
        sleeping_beauties = [
            p for p in predictions
            if p["early_citations"] < 5 and p["true_citations"] > 100
        ]
        if len(sleeping_beauties) > 10:
            patterns.append({
                "name": "Sleeping Beauty Detection",
                "description": f"{len(sleeping_beauties)} papers were delayed recognition",
                "priority": "high",
                "hypothesis": "Add method novelty detector"
            })

        # 检测跨学科偏见
        cross_disciplinary = [
            p for p in predictions
            if p["discipline_count"] > 3 and p["error"] > 50
        ]
        if len(cross_disciplinary) > 10:
            patterns.append({
                "name": "Cross-Disciplinary Bias",
                "description": f"{len(cross_disciplinary)} cross-disciplinary papers poorly predicted",
                "priority": "high",
                "hypothesis": "Add cross-discipline indicator feature"
            })

        # 检测领域偏见
        domain_errors = self._compute_domain_errors(predictions)
        biased_domains = [
            domain for domain, error in domain_errors.items()
            if error > np.mean(list(domain_errors.values())) + 20
        ]
        if biased_domains:
            patterns.append({
                "name": "Domain Bias",
                "description": f"Bias detected in domains: {', '.join(biased_domains)}",
                "priority": "medium",
                "hypothesis": "Implement domain normalization"
            })

        return patterns

    def _design_improvements(self, patterns: List[Dict]) -> List[Dict]:
        """基于模式设计改进"""
        improvements = []

        for pattern in patterns:
            if pattern["name"] == "Sleeping Beauty Detection":
                improvements.append({
                    "name": "Add Method Novelty Detector",
                    "type": "feature",
                    "priority": pattern["priority"],
                    "implementation": """
                    def detect_method_novelty(paper):
                        # 检测方法论文的关键词
                        method_keywords = [
                            "novel method", "new approach",
                            "methodology", "framework"
                        ]
                        abstract_lower = paper["abstract"].lower()
                        return any(kw in abstract_lower for kw in method_keywords)
                    """,
                    "expected_impact": "+0.05 R²"
                })

            elif pattern["name"] == "Cross-Disciplinary Bias":
                improvements.append({
                    "name": "Add Cross-Discipline Indicator",
                    "type": "feature",
                    "priority": pattern["priority"],
                    "implementation": """
                    def compute_cross_discipline_score(paper):
                        # 基于引用的期刊分布计算跨学科程度
                        cited_journals = get_cited_journals(paper)
                        categories = [get_journal_category(j) for j in cited_journals]
                        return len(set(categories))
                    """,
                    "expected_impact": "+0.03 R²"
                })

            elif pattern["name"] == "Domain Bias":
                improvements.append({
                    "name": "Implement Domain Normalization",
                    "type": "normalization",
                    "priority": pattern["priority"],
                    "implementation": """
                    def normalize_by_domain(prediction, domain):
                        domain_mean = get_domain_historical_mean(domain)
                        global_mean = get_global_historical_mean()
                        normalization_factor = global_mean / domain_mean
                        return prediction * normalization_factor
                    """,
                    "expected_impact": "+0.04 R²"
                })

        return improvements

    def _apply_improvement(self, improvement: Dict):
        """应用改进"""
        if improvement["type"] == "feature":
            # 添加新特征
            exec(improvement["implementation"])
        elif improvement["type"] == "normalization":
            # 添加归一化层
            self.model.add_normalization(
                exec(improvement["implementation"])
            )

    def _compute_metrics(
        self,
        predictions: List[float],
        test_set: Dataset
    ) -> EvaluationMetrics:
        """计算评估指标"""
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
        from scipy.stats import spearmanr

        true_values = [p.true_citations for p in test_set]

        return EvaluationMetrics(
            r2=r2_score(true_values, predictions),
            rmse=np.sqrt(mean_squared_error(true_values, predictions)),
            mae=mean_absolute_error(true_values, predictions),
            spearman=spearmanr(true_values, predictions)[0],
            by_quartile=self._compute_metrics_by_quartile(predictions, test_set),
            calibration_error=self._compute_calibration_error(predictions, test_set)
        )

    def _compute_metrics_by_quartile(
        self,
        predictions: List[float],
        test_set: Dataset
    ) -> Dict[str, float]:
        """按四分位数计算指标"""
        # 按真实引用数排序
        sorted_papers = sorted(test_set, key=lambda p: p.true_citations)
        n = len(sorted_papers)

        quartiles = {
            "q1_bottom": sorted_papers[:n//4],
            "q2": sorted_papers[n//4:n//2],
            "q3": sorted_papers[n//2:3*n//4],
            "q4_top": sorted_papers[3*n//4:]
        }

        metrics_by_quartile = {}
        for q_name, q_papers in quartiles.items():
            q_true = [p.true_citations for p in q_papers]
            q_pred = [predictions[i] for i, p in enumerate(q_papers)]
            metrics_by_quartile[q_name] = r2_score(q_true, q_pred)

        return metrics_by_quartile
```

---

## 8. 技术选型建议

### 8.1 推荐技术栈

基于开源项目调研，建议采用以下技术组合：

| 模块 | 技术选择 | 理由 | 参考 |
|------|----------|------|------|
| **多智能体编排** | CrewAI | 独立框架，Crews + Flows双模式，企业级特性 | crewAIInc/crewAI |
| **评估框架** | continuous-eval + OpenAI Flywheel方法论 | 模块化评估，LLM-as-a-Judge支持 | relari-ai/continuous-eval |
| **知识图谱** | Graphiti (Zep) | 时序感知，增量更新，专为Agent设计 | getzep/graphiti |
| **研究自动化** | GPT Researcher模式 | Plan-and-Execute架构，多源聚合 | assafelovic/gpt-researcher |
| **文献计量** | pyBibX | 功能全面，AI增强，Sleeping Beauty检测 | Valdecy/pyBibX |
| **向量数据库** | Chroma | 已集成，支持元数据过滤 | 现有技术栈 |
| **结构化数据** | SQLite | 已集成，零配置 | 现有技术栈 |

---

### 8.2 分阶段实施路线

#### Phase 1: 多智能体框架搭建（1-2周）

```python
# 1. 安装CrewAI
pip install crewai

# 2. 定义基础智能体
- Collector Agent: RSS/API数据收集
- Analyzer Agent: LLM特征提取
- Predictor Agent (保守派): 历史数据预测
- Validator Agent: 预测验证

# 3. 创建第一个Crew
collection_crew = Crew(
    agents=[collector, analyzer],
    process=Process.sequential
)

# 4. 测试端到端流程
result = collection_crew.kickoff()
```

#### Phase 2: 评估飞轮实现（1-2周）

```python
# 1. 实现三阶段循环
class EvaluationFlywheel:
    def run_cycle(self):
        # Analyze → Measure → Improve
        pass

# 2. 创建Golden Dataset
golden_dataset = create_golden_dataset(
    train_years="2015-2019",
    test_years="2020-2021"
)

# 3. 实现自动化评估器
citation_grader = AutomatedGrader(
    metric="citation_prediction",
    threshold=30  # ±30 citations
)

# 4. 集成到训练流程
flywheel = EvaluationFlywheel()
for iteration in range(10):
    metrics = flywheel.run_cycle(iteration)
    if metrics.r2 >= 0.75:
        break
```

#### Phase 3: 知识图谱集成（2-3周）

```python
# 1. 安装Graphiti
pip install graphiti-core

# 2. 初始化图谱
graph = Graphiti(
    store="Neo4j",
    embedding_model="text-embedding-3-small"
)

# 3. 数据迁移
for paper in papers:
    graph.add_node(
        entity_id=f"paper:{paper['doi']}",
        entity_type="Paper",
        attributes=paper
    )

# 4. 实现时序查询
sleeping_beauties = graph.query("""
    MATCH (p:Paper)
    WHERE p.publication_date > datetime('2020-01-01')
    WITH p, size((p)<-[:cites]-()) as citations
    WHERE citations < 5
    RETURN p
    ORDER BY p.method_novelty DESC
    LIMIT 20
""")
```

#### Phase 4: 文献计量分析集成（1周）

```python
# 1. 安装pyBibX
pip install pybibx

# 2. 数据导出
export_to_bibtex(papers_df, "evolutionary_biology.bib")

# 3. 使用pyBibX分析
from pybibx import BibDatabase
db = BibDatabase()
db.add_bibtex("evolutionary_biology.bib")

# 4. 检测Sleeping Beauty
sleeping_beauties = db.find_sleeping_beauties()

# 5. 网络分析
hubs_auth = db.hubs_and_authorities()
```

---

### 8.3 可选增强功能

#### 8.3.1 预测市场（长期愿景）

```python
class PredictionMarket:
    """预测市场 - 集体智慧"""

    def create_market(self, paper_id: str):
        """为论文创建预测市场"""
        pass

    def submit_prediction(self, agent_id: str, prediction: Dict):
        """智能体提交预测"""
        pass

    def resolve_market(self, paper_id: str, true_value: int):
        """结算市场"""
        pass

    def ensemble_prediction(self, paper_id: str) -> Dict:
        """基于市场共识集成"""
        pass
```

#### 8.3.2 用户反馈循环

```python
class FeedbackLoop:
    """用户反馈循环"""

    def collect_feedback(self, prediction_id: str, rating: int):
        """收集用户评分"""
        pass

    def retrain_with_feedback(self):
        """使用反馈数据增量训练"""
        pass
```

---

## 9. 总结与下一步行动

### 9.1 关键发现

1. **多智能体模式成熟**: CrewAI提供了完整的多智能体编排框架，可以直接应用于学术预测

2. **评估飞轮方法论**: OpenAI的三阶段循环（Analyze → Measure → Improve）提供了系统化的改进方法

3. **时序知识图谱**: Graphiti的增量更新和时序感知非常适合动态学术数据

4. **文献计量工具**: pyBibX提供了Sleeping Beauty检测等专业功能

5. **集成预测优势**: 多智能体集成预测优于单一模型

### 9.2 建议的优先级

| 优先级 | 功能 | 预期收益 | 实施难度 |
|--------|------|----------|----------|
| **P0** | 多智能体预测系统 | 高 | 中 |
| **P0** | 评估飞轮基础 | 高 | 低 |
| **P1** | 时序知识图谱 | 中 | 高 |
| **P1** | pyBibX集成 | 中 | 低 |
| **P2** | 预测市场 | 高 | 高 |
| **P2** | 用户反馈循环 | 中 | 中 |

### 9.3 下一步行动

1. **立即开始**:
   - 实现基础的多智能体预测系统（CrewAI）
   - 创建评估飞轮框架
   - 建立Golden Dataset

2. **短期目标（1-2月）**:
   - 完成4个预测智能体（保守派、激进派、理论派、应用派）
   - 实现自动化评估器
   - 运行第一个完整的飞轮周期

3. **中期目标（3-6月）**:
   - 集成Graphiti知识图谱
   - 集成pyBibX进行深度分析
   - 实现预测市场原型

4. **长期目标（6月+）**:
   - 完整的预测市场系统
   - 用户反馈和持续改进
   - 跨领域扩展

---

## 参考文献

### 开源项目

1. **CrewAI**: https://github.com/crewAIInc/crewAI
2. **OpenAI Evaluation Flywheel**: https://github.com/openai/openai-cookbook/tree/main/examples/evaluation
3. **continuous-eval**: https://github.com/relari-ai/continuous-eval
4. **GPT Researcher**: https://github.com/assafelovic/gpt-researcher
5. **AutoAgent**: https://github.com/HKUDS/AutoAgent
6. **Graphiti**: https://github.com/getzep/graphiti
7. **pyBibX**: https://github.com/Valdecy/pyBibX

### 技术文档

8. CrewAI Documentation: https://docs.crewai.com/
9. Zep Documentation: https://help.getzep.com/
10. BERTopic: https://maartengr.github.io/BERTopic/

---

**文档版本**: v1.0
**最后更新**: 2025-12-28
**维护者**: Evo-Flywheel 项目团队

---

## 附录：快速开始指南

### A. 安装依赖

```bash
# 多智能体框架
pip install crewai

# 评估框架
pip install continuous-eval

# 知识图谱
pip install graphiti-core neo4j

# 文献计量
pip install pybibx

# 现有依赖
pip install -e ".[dev]"
```

### B. 运行示例

```python
# 1. 多智能体预测
from evo_flywheel.agents import PredictionSystem

system = PredictionSystem()
result = system.predict_paper("doi:10.1234/example")

# 2. 评估飞轮
from evo_flywheel.evaluation import EvaluationFlywheel

flywheel = EvaluationFlywheel()
metrics = flywheel.run_cycle(iteration=1)

# 3. 知识图谱查询
from evo_flywheel.knowledge_graph import AcademicGraph

graph = AcademicGraph()
sleeping_beauties = graph.find_sleeping_beauties()
```

---

**反馈与贡献**: 如有问题或建议，请通过 GitHub Issues 提交。
