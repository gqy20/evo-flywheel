"""LLM 分析 Prompt 模板

定义进化生物学论文分析的 Prompt 结构
"""

from typing import Any

# 进化尺度选项
EVOLUTIONARY_SCALES = ["分子", "个体", "种群", "物种"]

# 研究方法选项
RESEARCH_METHODS = ["系统发育", "群体遗传", "实验", "比较"]

# 进化机制选项
EVOLUTIONARY_MECHANISMS = [
    "自然选择",
    "遗传漂变",
    "基因流",
    "突变",
    "性选择",
    "人工选择",
]


def get_analysis_schema() -> dict:
    """获取分析结果的数据结构 Schema

    Returns:
        dict: 分析结果的默认结构示例
    """
    return {
        "taxa": "",  # 研究物种/分类群
        "evolutionary_scale": "",  # 分子/个体/种群/物种
        "research_method": "",  # 系统发育/群体遗传/实验/比较
        "key_findings": [],  # 3-5个关键发现
        "evolutionary_mechanism": "",  # 主要进化机制
        "importance_score": 0,  # 重要性评分 0-100
        "innovation_summary": "",  # 创新性总结（1-2句话）
    }


def build_analysis_prompt(title: str, abstract: str) -> str:
    """构建论文分析 Prompt

    Args:
        title: 论文标题
        abstract: 论文摘要

    Returns:
        str: 分析 Prompt
    """
    # 构建进化机制说明
    mechanisms_text = "、".join(EVOLUTIONARY_MECHANISMS[:4])

    # 构建 Prompt
    prompt = f"""请分析以下进化生物学论文，提取关键信息并评估其重要性。

## 论文信息

**标题**: {title}

**摘要**: {abstract}

---

## 分析要求

### 一、基础信息

1. **研究物种** (taxa)
   - 涉及的物种、类群或分类群

2. **进化尺度** (evolutionary_scale)
   - 请从以下选项中选择：分子、个体、种群、物种

3. **研究方法** (research_method)
   - 请从以下选项中选择：系统发育、群体遗传、实验、比较

### 二、核心内容

4. **关键发现** (key_findings)
   - 提取 3-5 个最重要的研究发现
   - 每个发现用一句话概括

5. **进化机制** (evolutionary_mechanism)
   - 主要涉及的进化机制：{mechanisms_text}等
   - 请选择最相关的一个

6. **创新性** (innovation_summary)
   - 理论创新、方法创新或发现创新
   - 用 1-2 句话概括

### 三、价值评估

7. **重要性评分** (importance_score)
   - 0-100 分
   - 考虑因素：科学价值、方法创新、发现重要性
   - 参考标准：
     * 90-100：突破性发现，改变领域认知
     * 70-89：重要进展，有显著创新
     * 50-69：有价值的研究
     * 30-49：一般性研究
     * 0-29：价值有限

8. **推荐理由** (与 innovation_summary 结合)
   - 简要说明为何值得研究者关注

---

## 输出格式

请以 JSON 格式返回结果（**只输出 JSON 代码块，不要包含其他任何文字**）：

```json
{{
    "taxa": "研究物种",
    "evolutionary_scale": "进化尺度",
    "research_method": "研究方法",
    "key_findings": [
        "发现1",
        "发现2",
        "发现3"
    ],
    "evolutionary_mechanism": "进化机制",
    "importance_score": 85,
    "innovation_summary": "创新性总结"
}}
```

**重要提示**：
1. **只输出 JSON**，开头用 ```json，结尾用 ```，中间不要有任何其他文字
2. **使用英文标点符号**：冒号(:)、逗号(,)、双引号(")
3. key_findings 必须是数组，包含 3-5 个字符串
4. importance_score 必须是 0-100 之间的整数
5. 数组最后一个元素后面**不要加逗号**
"""

    return prompt


def build_report_prompt(
    papers: list[dict[str, Any]],
    clusters: dict[str, list[dict]],
    stats: dict[str, Any],
) -> str:
    """构建深度报告生成的 LLM Prompt

    Args:
        papers: 论文列表
        clusters: 按主题分组的论文
        stats: 统计信息

    Returns:
        str: LLM prompt
    """
    # 构建论文摘要（限制数量避免超token）
    paper_summaries = []
    for p in papers[:50]:
        findings_text = "; ".join(p.get("key_findings", [])[:3])
        paper_summaries.append(f"""
- 【{p.get("importance_score", 0)}分】{p.get("title", "")}
  物种: {p.get("taxa", "Unknown")} | 尺度: {p.get("evolutionary_scale", "Unknown")} | 方法: {p.get("research_method", "Unknown")}
  机制: {p.get("evolutionary_mechanism", "Unknown")}
  关键发现: {findings_text}
  创新性: {p.get("innovation_summary", "")}
""")

    # 构建聚类信息
    cluster_info = []
    for topic, cluster_papers in clusters.items():
        cluster_info.append(f"""
【{topic.replace("_", "/")}】({len(cluster_papers)}篇)
  代表论文: {cluster_papers[0].get("title", "")[:50]}...
""")

    prompt = f"""你是一位资深的进化生物学研究专家，请基于以下今天采集的论文数据，生成一份深度分析报告。

## 日期
{stats.get("date", "")}

## 统计概览
- 总论文数: {stats.get("total", 0)}
- 高价值论文(≥80分): {stats.get("high_value", 0)}
- 涉及物种数: {stats.get("taxa_count", 0)}
- 涉及方法数: {stats.get("methods_count", 0)}

## 论文数据
{"".join(paper_summaries)}

## 主题聚类
{"".join(cluster_info)}

## 请生成以下内容（以 JSON 格式返回）：

{{
  "research_summary": "用3-5句话概括今天的研究亮点，突出突破性进展和值得关注的趋势",

  "hot_topics": [
    {{"topic": "热点名称", "description": "为什么成为热点，涉及哪些突破", "paper_count": 5, "key_papers": [1, 2, 3]}}
  ],

  "trend_analysis": {{
    "emerging_taxa": "新兴研究对象（如果今天出现新的物种研究）",
    "methodology_trends": "方法学发展趋势（如单细胞测序应用的扩展）",
    "cross_disciplinary_insights": "跨学科洞察（如与AI、物理的结合）"
  }},

  "recommended_papers": [
    {{"paper_id": 1, "title": "论文标题", "reason": "推荐理由：为什么这篇论文特别值得读（1-2句话）", "priority": "must_read"}}
  ],

  "forward_look": "基于今天的研究，预测未来1-2个月可能出现的方向（2-3句话）"
}}

**重要提示**：
1. 只返回 JSON，不要包含其他文字
2. hot_topics 识别3-5个热点
3. recommended_papers 包含5-10篇，priority 分为 must_read/highly_recommended/interesting
4. 趋势分析要有洞察力，不是简单的数据罗列
"""

    return prompt
