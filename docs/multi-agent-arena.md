# 多智能体竞争框架设计文档

> **项目**: Evo-Flywheel 学术飞轮系统
> **文档类型**: 技术设计文档
> **版本**: v1.0
> **创建日期**: 2025-12-28
> **状态**: 设计阶段

---

## 1. 背景与动机

### 1.1 问题定义

**传统推荐系统的局限：**

当前学术文献推荐系统存在以下问题：

1. **封闭循环**：用户点击 → 优化推荐 → 更多点击，可能陷入局部最优
2. **单一价值**：以用户偏好为导向，而非真实学术价值
3. **缺乏验证**：无法预测论文的真实影响力
4. **过滤气泡**：过度迎合用户历史，限制发现范围

### 1.2 启发：AI-Trader 多模型交易实验

**AI-Trader (香港大学)**

| 项目 | 详情 |
|------|------|
| **主办方** | 香港大学数据科学学院 (黄超教授) |
| **GitHub** | https://github.com/HKUDS/AI-Trader |
| **直播平台** | https://ai4trade.ai |

**实验设计：**

- 5个AI模型（Qwen, DeepSeek, GPT, Claude, Gemini）各持$10,000
- 在NASDAQ 100市场独立交易，零人工干预
- 遵循"三不原则"：不干预、不加杠杆、不做空

**实验结果：**

| 排名 | 模型 | 收益率 | 特征 |
|------|------|--------|------|
| 🥇 | Qwen 3 Max | +22.32% | 稳健波段操作 |
| 🥈 | DeepSeek V3.1 | +4.89% | 精准抄底 |
| 3 | Grok 4 | 小幅亏损 | - |
| 4 | Claude Sonnet 4.5 | 亏损 | 过于保守 |
| 5 | Gemini 2.5 Pro | 大幅亏损 | 策略混乱 |
| 6 | **GPT-5** | **-62%** | 高频过度交易 |

**关键发现：**

1. **策略差异暴露**：不同模型有天然不同的交易风格
2. **真实市场验证**：实际收益作为客观评价标准
3. **竞争驱动进化**：可识别有效策略并调整权重
4. **透明可视化**：排行榜形成持续激励

---

## 2. 核心设计理念

### 2.1 从交易到学术的映射

| 金融市场 | 学术市场 |
|----------|----------|
| 股票价格 | 论文影响力 |
| 买入/卖出 | 关注/忽略 |
| 涨跌幅 | 引用增长 |
| 交易量 | 下载/浏览量 |
| 收益率 | 预测准确率 |
| 破产 | 被撤稿/证伪 |

### 2.2 多智能体竞争框架

**核心理念转变：**

```
传统模式:
单一推荐系统 → 优化用户点击 → 封闭循环

竞争模式:
多个智能体 → 预测真实影响 → 真实验证 → 策略进化 → 开放飞轮
```

**三层反馈结构：**

```
Layer 1: 智能体层 (AI vs AI)
  多个评估智能体竞争预测
  ↓
Layer 2: 用户层 (Human vs AI)
  用户参与预测，形成二级竞争
  ↓
Layer 3: 真实世界 (Nature vs All)
  学术市场作为终极仲裁者
  ↓
  反馈到 Layer 1 和 2
  ↓
  飞轮加速
```

---

## 3. 智能体角色体系

### 3.1 角色设计矩阵

```
        保守 ━━━━━━━━━━━━━━━━━━━━━ 激进
         ↑                          ↑
    理论  A型                   C型
    守护者              范式转移猎手
    (保守+理论)          (激进+理论)
         ↓                          ↓
    B型                   D型
    实用主义者             技术颠覆者
    (保守+应用)          (激进+应用)
         ↓                          ↓
        应用 ━━━━━━━━━━━━━━━━━━━━━ 理论
```

### 3.2 四个基础智能体

| 智能体 | 角色名 | 关注点 | 预测模式 | 高分场景 |
|--------|--------|--------|----------|----------|
| **A型** | 理论守护者 | 方法论严谨性、统计显著性 | 保守预测 | 标准化研究的突破 |
| **B型** | 实用主义者 | 实际应用价值、工程可行性 | 适中预测 | 应用优化论文 |
| **C型** | 范式转移猎手 | 颠覆性创新、理论突破 | 激进预测 | 开创新领域 |
| **D型** | 技术颠覆者 | 技术创新、工具价值 | 激进预测 | 新技术应用 |

### 3.3 智能体预测模式示例

**同一篇论文，不同智能体的预测：**

```python
论文: "CRISPR-Cas9在植物基因组编辑中的新方法"

智能体预测:
├── A型 (理论守护者)
│   ├── 预测引用: 15
│   ├── 理由: 方法标准但无理论突破
│   └── 评分: 6/10
│
├── B型 (实用主义者)
│   ├── 预测引用: 35
│   ├── 理由: 有实际应用价值
│   └── 评分: 7/10
│
├── C型 (范式转移猎手)
│   ├── 预测引用: 25
│   ├── 理由: 非范式转移，属渐进改进
│   └── 评分: 6/10
│
└── D型 (技术颠覆者)
    ├── 预测引用: 60
    ├── 理由: 新技术，可能被广泛采用
    └── 评分: 8/10

分歧度: 45 (高！值得关注)
共识: 33.75
```

---

## 4. 预测市场竞争机制

### 4.1 预测合约设计

```python
# 伪代码：预测合约系统
class PredictionContract:
    """论文影响力预测合约"""

    def __init__(self, paper):
        self.paper_id = paper["id"]
        self.opening_date = datetime.now()

        # 各智能体预测
        self.predictions = {}
        for agent in agents:
            self.predictions[agent.name] = {
                "citations_1year": agent.predict_impact(paper),
                "confidence": agent.get_confidence(),
                "reasoning": agent.explain_prediction(paper),
            }

        # 计算分歧度
        self.disagreement = self._calculate_disagreement()
        self.consensus = np.mean([p["citations_1year"]
                                  for p in self.predictions.values()])

    def _calculate_disagreement(self):
        """计算预测分歧度"""
        preds = [p["citations_1year"] for p in self.predictions.values()]
        return max(preds) - min(preds)

    def validate(self, actual_citations):
        """真实验证，更新智能体声誉"""
        for agent_name, prediction in self.predictions.items():
            error = abs(prediction["citations_1year"] - actual_citations)
            agents[agent_name].update_reputation(error)
```

### 4.2 分歧度的价值信号

| 分歧度范围 | 含义 | 用户行为 | 学术价值 |
|-----------|------|----------|----------|
| 高 (>50) | 智能体意见严重分歧 | 深入阅读、自行判断 | 可能有争议或突破 |
| 中 (20-50) | 正常观点差异 | 值得浏览 | 常规研究 |
| 低 (<20) | 智能体共识 | 可忽略 | 平庸或明显突破 |
| 低+高分 | 明确的突破论文 | 必读 | 领域重要成果 |

### 4.3 分层验证体系

| 时间点 | 验证指标 | 权重 | 反馈周期 |
|--------|----------|------|----------|
| **T+1周** | Altmetric评分、早期讨论 | 10% | 1周 |
| **T+1月** | 早期引用、下载量 | 20% | 1月 |
| **T+3月** | Q1引用、专利提及 | 30% | 3月 |
| **T+1年** | 正式引用数 | 40% | 1年 |
| **T+3年** | 稳定引用、衍生研究 | 长期 | 3年 |

---

## 5. 多维度评估指标体系

### 5.1 传统学术指标

| 指标 | 含义 | 获取周期 | 预测价值 |
|------|------|----------|----------|
| **总引用数** | 被其他论文引用次数 | 1-3年 | 核心指标 |
| **年均引用数** | 总引用/发表年数 | 1-3年 | 标准化 |
| **引用速度** | 首引时间、引用半衰期 | 3-12月 | 早期信号 |
| **PR值** | 引用网络中的重要性 | 1-2年 | 质量权重 |

### 5.2 替代计量学

| 维度 | 具体指标 | 数据源 | 反馈周期 |
|------|----------|--------|----------|
| **新闻媒体** | 报道数、媒体影响力 | Altmetric | 1-7天 |
| **社交媒体** | Twitter, Weibo 提及 | Altmetric API | 1小时-3天 |
| **博客/论坛** | 科学博客、Reddit | Altmetric | 1-3天 |
| **知识库** | Wikipedia, StackOverflow | API | 1-30天 |
| **参考管理** | Mendeley, Zotero | Altmetric | 1-7天 |

### 5.3 技术影响力

| 指标 | 数据源 | 适用领域 | 反馈周期 |
|------|--------|----------|----------|
| **代码影响** | GitHub stars/forks | 计算机科学 | 1周-1月 |
| **数据下载** | Zenodo, Figshare | 数据密集型 | 1周-1月 |
| **Docker使用** | Docker Hub pulls | 软件工具 | 1周-1月 |
| **专利引用** | Google Patents | 应用科学 | 1-3年 |
| **临床采用** | 临床指南 | 医学 | 2-5年 |

### 5.4 内容质量指标

| 维度 | 评估方法 | 预测目标 |
|------|----------|----------|
| **方法学严谨性** | 智能体分析 | 长期引用稳定性 |
| **统计功效** | 提取样本量/效应量 | 可重复性 |
| **可重复性** | 代码/数据可用性 | 后续研究基础 |
| **创新性** | 与已有文献距离 | 突破性引用 |
| **可读性** | NLP语言模型 | 社会传播力 |

### 5.5 长期衍生影响

| 指标 | 时间窗口 | 评估方法 |
|------|----------|----------|
| **开启新领域** | 5-10年 | 专家标注 |
| **改变教科书** | 5-15年 | 文本分析 |
| **后续高被引** | 3-10年 | 网络分析 |
| **反驳论文数** | 1-5年 | 情感分析 |
| **综述收录** | 2-5年 | 文本挖掘 |

---

## 6. 综合影响力指数

### 6.1 分领域加权

```python
def calculate_impact_score(paper, field="evolutionary_biology"):
    """计算综合影响力指数"""

    # 标准化各维度指标 (0-100)
    normalized_metrics = {
        "citations": normalize(paper.citations, field_benchmark),
        "altmetric": normalize(paper.altmetric_score),
        "technical": normalize(paper.github_stars, dataset_downloads),
        "quality": paper.methodology_score * 10,
        "long_term": paper.innovation_score * 10,
    }

    # 分领域权重
    weights = {
        "basic_research": {  # 基础研究
            "citations": 0.40,
            "altmetric": 0.20,
            "technical": 0.10,
            "quality": 0.20,
            "long_term": 0.10,
        },
        "applied_research": {  # 应用研究
            "citations": 0.25,
            "altmetric": 0.15,
            "technical": 0.35,  # 更重视应用
            "quality": 0.15,
            "long_term": 0.10,
        },
    }

    w = weights.get(field, weights["basic_research"])
    return sum(normalized_metrics[k] * w[k] for k in normalized_metrics)
```

### 6.2 预测目标分层

**短期 (1-3个月) - 快速反馈：**
- ✅ Altmetric评分
- ✅ 代码仓库 stars
- ✅ 下载量
- ✅ 社交媒体讨论

**中期 (1年) - 学术验证：**
- ✅ 早期引用数
- ✅ 专利引用
- ✅ 综述收录

**长期 (3-5年) - 真实影响：**
- ✅ 稳定引用数
- ✅ 知识衍生（高被引的引用者）
- ✅ 教材/指南收录

---

## 7. 技术实现方案

### 7.1 新增模块结构

```
src/evo_flywheel/
├── analyzers/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py              # 智能体基类
│   │   ├── conservative.py       # 保守派智能体
│   │   ├── radical.py            # 激进派智能体
│   │   └── prompts.py            # 角色特定Prompt
│   ├── arena.py                  # 竞争场协调器
│   └── predictions.py            # 预测管理
├── db/
│   ├── models.py                 # 新增预测/验证表
│   └── predictions_crud.py       # 预测数据操作
└── validation/
    ├── altmetric.py              # Altmetric数据获取
    ├── crossref.py               # 引用数据获取
    └── scheduler.py              # 验证调度任务
```

### 7.2 核心代码框架

**智能体基类：**

```python
# src/evo_flywheel/analyzers/agents/base.py
from abc import ABC, abstractmethod
from typing import Any

class PaperAgent(ABC):
    """论文评估智能体基类"""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role  # "conservative_theory", "radical_app", etc.
        self.accuracy_history = []
        self.reputation_score = 0.5  # 0-1

    @abstractmethod
    def predict_impact(self, paper: dict[str, Any]) -> int:
        """预测论文1年后的引用数"""
        pass

    @abstractmethod
    def analyze_paper(self, paper: dict[str, Any]) -> dict[str, Any]:
        """从特定角度分析论文"""
        pass

    def get_confidence(self) -> float:
        """返回预测置信度"""
        if not self.accuracy_history:
            return 0.5
        # 基于历史准确率计算
        recent_accuracy = np.mean(self.accuracy_history[-10:])
        return recent_accuracy

    def update_reputation(self, error: float) -> None:
        """基于预测误差更新声誉"""
        # 转换误差为分数 (0-1, 1为完美)
        score = 1 / (1 + error / 10)
        self.accuracy_history.append(score)
        self.reputation_score = np.mean(self.accuracy_history[-50:])
```

**保守派智能体实现：**

```python
# src/evo_flywheel/analyzers/agents/conservative.py
from evo_flywheel.analyzers.agents.base import PaperAgent
from evo_flywheel.analyzers.llm import analyze_paper
from evo_flywheel.analyzers.agents.prompts import CONSERVATIVE_THEORY_PROMPT

class ConservativeTheoryAgent(PaperAgent):
    """保守派理论智能体 - 理论守护者"""

    def __init__(self):
        super().__init__(
            name="Conservative_Theory",
            role="保守派理论"
        )

    def predict_impact(self, paper: dict[str, Any]) -> int:
        """保守预测引用数"""
        # 获取基础分析
        analysis = analyze_paper(paper["title"], paper["abstract"])

        # 保守评分标准
        base_score = 10  # 基础引用

        # 方法严谨性加成
        if analysis.research_method == "phylogenetic":
            base_score += 5
        elif analysis.research_method == "experimental":
            base_score += 8

        # 统计显著性加成
        if "p < 0.001" in paper["abstract"]:
            base_score += 3

        # 保守折扣：不激进预测
        if analysis.importance_score > 80:
            base_score *= 0.7  # 怀疑过高的评分

        return int(base_score)

    def analyze_paper(self, paper: dict[str, Any]) -> dict[str, Any]:
        """从保守理论角度分析"""
        prompt = CONSERVATIVE_THEORY_PROMPT.format(
            title=paper["title"],
            abstract=paper["abstract"]
        )

        # 调用LLM获取分析
        result = analyze_paper(
            paper["title"],
            paper["abstract"],
            custom_prompt=prompt
        )

        return {
            "methodology_score": self._assess_methodology(paper),
            "statistical_rigor": self._assess_statistics(paper),
            "reproducibility": self._check_reproducibility(paper),
            "conservative_rating": self._calculate_conservative_score(result),
        }

    def _assess_methodology(self, paper: dict[str, Any]) -> int:
        """评估方法学严谨性"""
        abstract = paper["abstract"].lower()
        score = 5

        # 方法学关键词
        if "randomized" in abstract or "randomised" in abstract:
            score += 2
        if "replicate" in abstract or "reproducible" in abstract:
            score += 2
        if "sample size" in abstract or "n=" in abstract:
            score += 1

        return min(score, 10)

    def _assess_statistics(self, paper: dict[str, Any]) -> int:
        """评估统计严谨性"""
        abstract = paper["abstract"]
        score = 5

        # 统计指标
        if "p < 0.05" in abstract or "p<0.05" in abstract:
            score += 1
        if "p < 0.01" in abstract or "p<0.01" in abstract:
            score += 1
        if "confidence interval" in abstract.lower():
            score += 2
        if "effect size" in abstract.lower():
            score += 1

        return min(score, 10)

    def _check_reproducibility(self, paper: dict[str, Any]) -> bool:
        """检查可重复性"""
        # 检查是否有代码/数据链接
        has_code = "github" in paper.get("url", "").lower()
        has_data = "supplementary" in paper.get("abstract", "").lower()
        return has_code or has_data

    def _calculate_conservative_score(self, result) -> int:
        """计算保守评分"""
        # 对重要性评分进行保守调整
        original_score = result.importance_score
        if original_score > 70:
            return int(original_score * 0.8)
        return original_score
```

**竞争场协调器：**

```python
# src/evo_flywheel/analyzers/arena.py
from typing import Any
import numpy as np

from evo_flywheel.analyzers.agents.conservative import (
    ConservativeTheoryAgent,
    ConservativeAppAgent
)
from evo_flywheel.analyzers.agents.radical import (
    RadicalTheoryAgent,
    RadicalAppAgent
)
from evo_flywheel.db.predictions_crud import (
    save_prediction,
    get_paper_predictions
)

class MultiAgentArena:
    """多智能体竞争场"""

    def __init__(self):
        self.agents = [
            ConservativeTheoryAgent(),
            ConservativeAppAgent(),
            RadicalTheoryAgent(),
            RadicalAppAgent(),
        ]

    def evaluate_paper(self, paper: dict[str, Any]) -> dict[str, Any]:
        """让所有智能体评估同一篇论文"""

        predictions = {}
        analyses = {}
        confidences = {}

        for agent in self.agents:
            # 预测影响
            pred = agent.predict_impact(paper)
            predictions[agent.name] = pred

            # 分析论文
            analysis = agent.analyze_paper(paper)
            analyses[agent.name] = analysis

            # 获取置信度
            conf = agent.get_confidence()
            confidences[agent.name] = conf

        # 计算分歧度
        pred_values = list(predictions.values())
        disagreement = max(pred_values) - min(pred_values)
        consensus = np.mean(pred_values)
        std = np.std(pred_values)

        # 加权预测（基于智能体声誉）
        weighted_pred = self._calculate_weighted_prediction(
            predictions, confidences
        )

        result = {
            "paper_id": paper["id"],
            "paper_title": paper["title"],
            "predictions": predictions,
            "analyses": analyses,
            "confidences": confidences,
            "disagreement": disagreement,
            "consensus": consensus,
            "std": std,
            "weighted_prediction": weighted_pred,
            "recommendation": self._get_recommendation(predictions, analyses),
        }

        # 保存预测
        save_prediction(result)

        return result

    def _calculate_weighted_prediction(
        self,
        predictions: dict[str, int],
        confidences: dict[str, float]
    ) -> float:
        """基于智能体声誉计算加权预测"""
        total_weight = sum(confidences.values())
        if total_weight == 0:
            return np.mean(list(predictions.values()))

        weighted_sum = sum(
            predictions[name] * conf
            for name, conf in confidences.items()
        )
        return weighted_sum / total_weight

    def _get_recommendation(
        self,
        predictions: dict[str, int],
        analyses: dict[str, Any]
    ) -> str:
        """生成推荐意见"""
        # 找出最高和最低预测
        max_agent = max(predictions, key=predictions.get)
        min_agent = min(predictions, key=predictions.get)

        if predictions[max_agent] - predictions[min_agent] > 50:
            return f"高争议：{max_agent}看好，{min_agent}看淡"
        elif predictions[max_agent] > 50:
            return f"共识看好：平均预测{np.mean(list(predictions.values())):.0f}引用"
        else:
            return "关注度一般"

    def validate_predictions(self, paper_id: int, actual_citations: int):
        """验证预测，更新智能体声誉"""
        predictions = get_paper_predictions(paper_id)

        for pred in predictions:
            agent_name = pred["agent_name"]
            predicted = pred["predicted_citations"]
            error = abs(predicted - actual_citations)

            # 更新对应智能体的声誉
            for agent in self.agents:
                if agent.name == agent_name:
                    agent.update_reputation(error)
                    break

    def get_leaderboard(self) -> list[dict[str, Any]]:
        """获取智能体排行榜"""
        leaderboard = []
        for agent in self.agents:
            leaderboard.append({
                "name": agent.name,
                "role": agent.role,
                "reputation": agent.reputation_score,
                "recent_accuracy": np.mean(agent.accuracy_history[-10:]) if agent.accuracy_history else 0,
                "total_predictions": len(agent.accuracy_history),
            })

        # 按声誉排序
        leaderboard.sort(key=lambda x: x["reputation"], reverse=True)
        return leaderboard
```

### 7.3 数据库扩展

**新增表结构：**

```python
# src/evo_flywheel/db/models.py 新增

class AgentPrediction(Base):
    """智能体预测记录"""
    __tablename__ = "agent_predictions"

    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey("papers.id"))
    agent_name = Column(String(100))  # 智能体名称
    agent_role = Column(String(50))   # 智能体角色

    # 预测内容
    predicted_citations = Column(Integer)  # 预测引用数
    predicted_altmetric = Column(Integer)   # 预测Altmetric
    confidence = Column(Float)              # 置信度

    # 分析结果
    reasoning = Column(Text)      # 预测理由
    analysis = Column(JSON)       # 详细分析

    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    validated = Column(Boolean, default=False)

    paper = relationship("Paper", back_populates="predictions")


class PaperValidation(Base):
    """论文真实验证记录"""
    __tablename__ = "paper_validations"

    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey("papers.id"))

    # 验证指标
    actual_citations = Column(Integer)
    actual_altmetric = Column(Integer)
    validation_date = Column(DateTime)

    # 早期指标
    early_citations_1month = Column(Integer)
    early_citations_3month = Column(Integer)

    # 技术影响
    github_stars = Column(Integer)
    dataset_downloads = Column(Integer)

    # 长期指标
    landmark_status = Column(Boolean)  # 是否成为经典
    textbook_citations = Column(Integer)

    validated_at = Column(DateTime, default=datetime.utcnow)


class AgentReputation(Base):
    """智能体声誉记录"""
    __tablename__ = "agent_reputation"

    id = Column(Integer, primary_key=True)
    agent_name = Column(String(100), unique=True)
    reputation_score = Column(Float, default=0.5)

    # 统计
    total_predictions = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0)

    # 时间序列
    recent_accuracy = Column(JSON)  # 最近10次的准确率
    reputation_history = Column(JSON)  # 声誉历史

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 扩展 Paper 模型
Paper.predictions = relationship("AgentPrediction", back_populates="paper")
```

---

## 8. API 接口设计

### 8.1 竞争场端点

```
# 智能体排行榜
GET /api/arena/leaderboard
Response:
{
  "leaderboard": [
    {
      "rank": 1,
      "name": "Conservative_Theory",
      "role": "保守派理论",
      "reputation": 0.78,
      "recent_accuracy": 0.82,
      "total_predictions": 1250
    },
    ...
  ]
}

# 论文预测对决
GET /api/arena/papers/{id}/battle
Response:
{
  "paper_id": 12345,
  "title": "论文标题",
  "predictions": {
    "Conservative_Theory": 15,
    "Radical_Theory": 60,
    "Conservative_App": 25,
    "Radical_App": 45
  },
  "disagreement": 45,
  "consensus": 36.25,
  "recommendation": "高争议：Radical_Theory看好，Conservative_Theory看淡",
  "analyses": {
    "Conservative_Theory": {
      "reasoning": "方法标准但无突破...",
      "methodology_score": 8,
      ...
    },
    ...
  }
}

# 高争议论文列表
GET /api/arena/controversies?min_disagreement=30&limit=20
Response:
{
  "papers": [
    {
      "paper_id": 12345,
      "title": "论文标题",
      "disagreement": 65,
      "consensus": 40,
      "highest_prediction": 80,
      "lowest_prediction": 15
    },
    ...
  ]
}

# 用户参与预测
POST /api/arena/predict
Request:
{
  "paper_id": 12345,
  "user_prediction": {
    "citations_1year": 35,
    "confidence": 0.7,
    "reasoning": "我认为..."
  }
}
```

### 8.2 验证端点

```
# 触发验证任务
POST /api/validation/validate/{paper_id}
Request:
{
  "actual_citations": 42,
  "actual_altmetric": 156
}

# 获取验证历史
GET /api/validation/history/{paper_id}
Response:
{
  "predictions": [
    {
      "agent_name": "Conservative_Theory",
      "predicted": 15,
      "actual": 42,
      "error": 27
    },
    ...
  ]
}
```

---

## 9. Streamlit 界面设计

### 9.1 主页面布局

```python
# streamlit/pages/arena.py
import streamlit as st

st.set_page_config(page_title="学术竞技场", layout="wide")

# 侧边栏：智能体排行榜
with st.sidebar:
    st.header("🏆 智能体排行榜")
    leaderboard = get_leaderboard()
    for i, agent in enumerate(leaderboard, 1):
        st.metric(
            f"{i}. {agent['name']}",
            f"{agent['reputation']:.1%}",
            help=f"准确率: {agent['recent_accuracy']:.1%}"
        )

# 主内容区
tab1, tab2, tab3 = st.tabs(["今日争议", "预测对决", "验证历史"])

with tab1:
    st.header("🔥 高争议论文")
    controversies = get_controversies(limit=20)

    for paper in controversies:
        with st.expander(f"📄 {paper['title']}"):
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("预测分布")
                # 绘制预测分布图
                fig = plot_prediction_distribution(paper['predictions'])
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("分歧度: " + str(paper['disagreement']))
                st.write(f"共识: {paper['consensus']:.1f} 引用")

                # 各智能体观点
                for agent, pred in paper['predictions'].items():
                    st.write(f"**{agent}**: {pred} 引用")

            # 用户参与
            st.divider()
            st.subheader("你的预测")
            user_pred = st.slider(
                "你预测1年后引用数：",
                0, 200, paper['consensus']
            )
            if st.button("提交预测"):
                submit_user_prediction(paper['paper_id'], user_pred)
                st.success("预测已提交！")

with tab2:
    st.header("⚔️ 论文预测对决")
    paper_id = st.selectbox(
        "选择论文",
        get_recent_papers(),
        format_func=lambda x: x['title']
    )

    if paper_id:
        battle = get_paper_battle(paper_id)
        display_battle_view(battle)

with tab3:
    st.header("✅ 验证历史")
    validations = get_recent_validations()

    for v in validations:
        with st.expander(f"{v['paper_title']} - {v['validated_at']}"):
            st.metric("实际引用", v['actual_citations'])

            # 各智能体表现
            for agent, pred in v['predictions'].items():
                error = abs(pred - v['actual_citations'])
                st.progress(1 - error/100, f"{agent}: 误差 {error}")
```

### 9.2 可视化组件

**预测分布图：**

```python
def plot_prediction_distribution(predictions):
    """绘制智能体预测分布"""
    import plotly.graph_objects as go

    agents = list(predictions.keys())
    values = list(predictions.values())

    fig = go.Figure(go.Bar(
        x=agents,
        y=values,
        marker_color=[
            'green' if v > np.mean(values) else 'gray'
            for v in values
        ]
    ))

    fig.update_layout(
        title="各智能体引用预测",
        xaxis_title="智能体",
        yaxis_title="预测引用数",
        showlegend=False
    )

    return fig
```

**智能体声誉趋势：**

```python
def plot_reputation_trend(agent_name):
    """绘制智能体声誉历史趋势"""
    history = get_reputation_history(agent_name)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(history))),
        y=history,
        mode='lines',
        name=agent_name
    ))

    fig.update_layout(
        title=f"{agent_name} 声誉趋势",
        xaxis_title="预测次数",
        yaxis_title="声誉分数"
    )

    return fig
```

---

## 10. 验证数据源

### 10.1 API集成

| 数据源 | API | 提供指标 | 免费额度 | 用途 |
|--------|-----|----------|----------|------|
| **Crossref** | `/works/{doi}` | 引用数 | 免费 | 核心引用数据 |
| **Altmetric** | `/v1/id/{doi}` | Altmetric评分 | 1000次/天 | 社会影响 |
| **OpenCitations** | `/api/v1/citations/{doi}` | 引用列表 | 免费 | 引用网络 |
| **Europe PMC** | `/MED/{doi}` | 引用+Altmetrics | 免费 | 医学文献 |
| **GitHub** | REST API | stars, forks | 5000次/小时 | 代码影响 |
| **Wikipedia** | API | 引用统计 | 免费 | 知识整合 |

### 10.2 数据获取模块

```python
# src/evo_flywheel/validation/crossref.py
import httpx

def get_citations(doi: str) -> dict:
    """从Crossref获取引用数据"""
    url = f"https://api.crossref.org/works/{doi}"
    response = httpx.get(url)
    response.raise_for_status()
    data = response.json()

    return {
        "citations": data["message"].get("is-referenced-by-count", 0),
        "references": len(data["message"].get("reference", [])),
    }

# src/evo_flywheel/validation/altmetric.py
def get_altmetric(doi: str, api_key: str) -> dict:
    """从Altmetric获取社会影响数据"""
    url = f"https://api.altmetric.com/v1/id/doi/{doi}"
    params = {"key": api_key}
    response = httpx.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    return {
        "score": data.get("score", 0),
        "news": len(data.get("cursors", {}).get("news", [])),
        "blogs": len(data.get("cursors", {}).get("blogs", [])),
        "twitter": data.get("cited_by_tweeters_count", 0),
    }
```

---

## 11. 实现路线图

### 11.1 Phase 1: 多智能体框架 (1-2周)

**任务：**
- [ ] 实现 `PaperAgent` 基类
- [ ] 实现4个基础智能体
- [ ] 实现角色特定 Prompt 模板
- [ ] 实现 `MultiAgentArena` 协调器
- [ ] 单元测试

**交付物：**
```bash
src/evo_flywheel/analyzers/
├── agents/
│   ├── __init__.py ✓
│   ├── base.py ✓
│   ├── conservative.py ✓
│   └── radical.py ✓
└── arena.py ✓
```

### 11.2 Phase 2: 数据库与验证 (3-5天)

**任务：**
- [ ] 扩展数据库模型
- [ ] 实现 CRUD 操作
- [ ] 集成 Crossref API
- [ ] 集成 Altmetric API
- [ ] 实现验证调度任务

**交付物：**
```bash
src/evo_flywheel/db/models.py ✓ 扩展
src/evo_flywheel/validation/
├── crossref.py ✓
├── altmetric.py ✓
└── scheduler.py ✓
```

### 11.3 Phase 3: API 端点 (1周)

**任务：**
- [ ] 排行榜 API
- [ ] 预测对决 API
- [ ] 争议论文 API
- [ ] 用户预测 API
- [ ] 验证 API

**交付物：**
```bash
src/evo_flywheel/api/arena.py ✓
```

### 11.4 Phase 4: Streamlit 界面 (1-2周)

**任务：**
- [ ] 智能体排行榜页面
- [ ] 预测对决页面
- [ ] 争议论文列表
- [ ] 用户预测交互
- [ ] 可视化图表

**交付物：**
```bash
streamlit/pages/
├── arena.py ✓
└── predictions.py ✓
```

### 11.5 Phase 5: 进化与优化 (持续)

**任务：**
- [ ] 基于历史数据优化权重
- [ ] 生成新的智能体变体
- [ ] A/B测试 Prompt
- [ ] 领域自适应智能体
- [ ] 用户反馈集成

---

## 12. 预期效果

### 12.1 飞轮加速指标

| 时间节点 | 智能体数量 | 预测准确率 | 论文覆盖 |
|----------|-----------|-----------|----------|
| 启动 | 4个基础智能体 | 基准 | 30篇/天 |
| 1个月 | 4个 | 50% | 900篇历史 |
| 3个月 | 5-6个（进化） | 55% | 2700篇 |
| 6个月 | 6-8个（领域分化） | 60% | 5400篇 |
| 1年 | 8-10个 | 65%+ | 10000篇+ |

### 12.2 价值验证

**对用户的价值：**
- 发现争议性论文（分歧度高）
- 理解不同评估视角
- 参与预测，测试判断力
- 比单一推荐更丰富的信息

**对学术界的价值：**
- 探索影响力量化
- 加速重要研究传播
- 促进学术讨论
- 形成预测市场

---

## 13. 风险与挑战

### 13.1 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 预测准确率低于预期 | 用户流失 | 多维度指标，早期验证 |
| API限流 | 数据缺失 | 缓存+多源整合 |
| 智能体同质化 | 分歧度低 | 强调角色差异化 |
| 验证周期长 | 反馈延迟 | 代理指标提前验证 |

### 13.2 设计挑战

**挑战1：如何避免智能体趋同？**
- 方案：强化角色约束，不同的Prompt
- 方案：惩罚过度相似的预测

**挑战2：如何处理领域差异？**
- 方案：分领域训练
- 方案：领域专用智能体

**挑战3：如何激励用户参与？**
- 方案：用户声誉系统
- 方案：预测准确率排行

---

## 14. 未来扩展

### 14.1 智能体进化

```python
# 自动生成新智能体
class AgentEvolution:
    def evolve(self, performance_history):
        """基于历史表现生成新智能体"""
        # 识别表现好的模式
        successful_patterns = self._extract_patterns(performance_history)

        # 生成新智能体
        new_agents = []
        for pattern in successful_patterns:
            new_agent = self._generate_agent(pattern)
            new_agents.append(new_agent)

        # A/B测试
        return self._ab_test(new_agents)
```

### 14.2 用户参与市场

```python
# 预测市场
class PredictionMarket:
    def create_market(self, paper):
        """为每篇论文创建预测市场"""
        market = {
            "paper_id": paper["id"],
            "contracts": [],
            "traders": [],
        }

        # 创建不同预测的合约
        for tier in ["low", "medium", "high"]:
            contract = {
                "type": tier,
                "price": self._initial_price(tier),
                "volume": 0,
            }
            market["contracts"].append(contract)

        return market
```

---

## 15. 参考资料

### 15.1 相关研究

1. **AI-Trader** (HKU)
   - GitHub: https://github.com/HKUDS/AI-Trader
   - 直播: https://ai4trade.ai

2. **TradingAgents** (BAAI)
   - 论文: https://arxiv.org/abs/2412.20138
   - 多角色协作框架

3. **Alpha Arena**
   - 主办方: nof1.ai
   - 6个AI模型实盘交易

### 15.2 学术指标研究

1. **替代计量学**
   - Altmetric.com
   - Plum Analytics
   - Impactstory

2. **引用分析**
   - Crossref
   - OpenCitations
   - Europe PMC

3. **科学学**
   - Fortunato et al. (2018) - Science of science
   - Wang et al. (2013) - Science of science

---

## 附录 A：术语表

| 术语 | 定义 |
|------|------|
| **智能体** | 具有特定评估策略的AI角色 |
| **分歧度** | 各智能体预测值的极差 |
| **共识** | 各智能体预测的均值 |
| **声誉分数** | 智能体历史预测准确率的综合评分 |
| **验证** | 将预测值与真实值对比的过程 |
| **飞轮** | 持续自我强化的循环系统 |

---

## 附录 B：配置示例

```yaml
# config/arena.yaml
arena:
  # 智能体配置
  agents:
    - name: conservative_theory
      role: 保守派理论
      model: glm-4-flash
      temperature: 0.3

    - name: radical_theory
      role: 激进派理论
      model: glm-4-flash
      temperature: 0.8

  # 验证配置
  validation:
    crossref:
      enabled: true
      api_url: https://api.crossref.org/works

    altmetric:
      enabled: true
      api_key: ${ALTMETRIC_API_KEY}

  # 调度配置
  schedule:
    collection: "0 9 * * *"      # 每天9点采集
    validation: "0 9 * * 0"      # 每周日验证
    evolution: "0 9 1 * *"       # 每月1日进化
```

---

**文档结束**

*本文档是 Evo-Flywheel 项目多智能体竞争框架的设计说明。如有问题或建议，请联系项目维护者。*
