"""LLM 服务模块

使用 OpenAI 兼容 API 调用 LLM 进行论文分析
"""

import json
import re
import time
from dataclasses import dataclass, field

from openai import OpenAI

from evo_flywheel.analyzers.prompts import build_analysis_prompt
from evo_flywheel.config import get_settings
from evo_flywheel.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TokenUsage:
    """Token 使用统计"""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class AnalysisResult:
    """论文分析结果"""

    taxa: str  # 研究物种
    evolutionary_scale: str  # 进化尺度
    research_method: str  # 研究方法
    key_findings: list[str]  # 关键发现
    evolutionary_mechanism: str  # 进化机制
    importance_score: int  # 重要性评分
    innovation_summary: str  # 创新性总结
    usage: TokenUsage = field(default_factory=TokenUsage)  # Token 使用


def get_openai_client() -> OpenAI:
    """获取 OpenAI 客户端

    使用配置中的 API 密钥和 base URL

    Returns:
        OpenAI: OpenAI 客户端实例
    """
    settings = get_settings()

    # 检查是否配置了 OpenAI 兼容的 API
    api_key = getattr(settings, "openai_api_key", "")
    base_url = getattr(settings, "openai_base_url", None)

    if not api_key:
        raise ValueError("未配置 API 密钥，请设置 OPENAI_API_KEY 环境变量")

    return OpenAI(
        api_key=api_key,
        base_url=base_url if base_url else None,
    )


def _fix_json(json_str: str) -> str:
    """尝试修复常见的 JSON 格式问题

    Args:
        json_str: 可能有格式问题的 JSON 字符串

    Returns:
        str: 修复后的 JSON 字符串
    """
    # 1. 替换中文标点符号为英文
    # 使用 Unicode 码点避免转义问题
    replacements = {
        "\uff1a": ":",  # 全角冒号
        "\uff0c": ",",  # 全角逗号
        "\u3010": "[",  # 【
        "\u3011": "]",  # 】
        "\uff08": "(",  # （
        "\uff09": ")",  # ）
        "\u201c": '"',  # 中文左引号 ""
        "\u201d": '"',  # 中文右引号 ""
        "\u2018": "'",  # 中文左单引号 '
        "\u2019": "'",  # 中文右单引号 '
    }
    for old, new in replacements.items():
        json_str = json_str.replace(old, new)

    # 2. 移除数组/对象末尾的逗号（在 } 或 ] 之前）
    json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)

    # 3. 确保字符串用双引号（处理单引号）
    # 将单引号键值对转换为双引号
    json_str = re.sub(r"'([^']+)'(\s*:)", r'"\1"\2', json_str)
    json_str = re.sub(r"(:\s*)'([^']+)'", r'\1"\2"', json_str)

    return json_str


def parse_llm_response(response: str) -> AnalysisResult:
    """解析 LLM 返回的 JSON 响应

    Args:
        response: LLM 返回的原始文本

    Returns:
        AnalysisResult: 解析后的分析结果

    Raises:
        ValueError: 响应为空、格式错误或缺少必需字段
    """
    if not response or not response.strip():
        raise ValueError("响应为空")

    # 尝试提取 JSON（处理 markdown 代码块）
    json_str = response.strip()

    # 移除 markdown 代码块标记
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    elif json_str.startswith("```"):
        json_str = json_str[3:]

    if json_str.endswith("```"):
        json_str = json_str[:-3]

    json_str = json_str.strip()

    # 尝试从文本中提取 JSON（处理额外文本）
    json_match = re.search(r"\{.*\}", json_str, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)

    # 尝试修复常见的 JSON 格式问题
    json_str = _fix_json(json_str)

    # 解析 JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        # 记录原始响应用于调试
        logger.error(f"JSON 解析失败: {e}")
        logger.error(f"原始响应:\n{response[:500]}...")
        logger.error(f"提取的 JSON 字符串:\n{json_str[:500]}...")
        raise ValueError(f"解析失败: {e}") from e

    # 验证必需字段
    required_fields = [
        "taxa",
        "evolutionary_scale",
        "research_method",
        "key_findings",
        "evolutionary_mechanism",
        "importance_score",
        "innovation_summary",
    ]

    missing_fields = [f for f in required_fields if f not in data]
    if missing_fields:
        raise ValueError(f"缺少必需字段: {', '.join(missing_fields)}")

    # 验证 key_findings 是列表
    if not isinstance(data["key_findings"], list):
        raise ValueError("key_findings 必须是列表")

    # 验证 importance_score 是整数
    if not isinstance(data["importance_score"], int):
        try:
            data["importance_score"] = int(data["importance_score"])
        except (ValueError, TypeError):
            raise ValueError("importance_score 必须是整数")

    return AnalysisResult(
        taxa=data["taxa"],
        evolutionary_scale=data["evolutionary_scale"],
        research_method=data["research_method"],
        key_findings=data["key_findings"],
        evolutionary_mechanism=data["evolutionary_mechanism"],
        importance_score=data["importance_score"],
        innovation_summary=data["innovation_summary"],
    )


def analyze_paper(
    title: str,
    abstract: str,
    model: str = "glm-4-flash",
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> AnalysisResult:
    """使用 LLM 分析论文

    Args:
        title: 论文标题
        abstract: 论文摘要
        model: 使用的模型名称
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）

    Returns:
        AnalysisResult: 论文分析结果

    Raises:
        Exception: API 调用失败超过最大重试次数
    """
    # 构建 Prompt
    prompt = build_analysis_prompt(title, abstract)

    # 获取客户端
    client = get_openai_client()

    # 调用 API（带重试）
    last_error: Exception | None = None
    parse_error_count = 0  # 单独追踪解析错误次数

    for attempt in range(max_retries):
        try:
            logger.info(f"调用 LLM API (尝试 {attempt + 1}/{max_retries})")

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的进化生物学研究助手，擅长分析论文并提取关键信息。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            # 解析响应
            content = response.choices[0].message.content
            result = parse_llm_response(content)

            # 添加 Token 使用统计
            result.usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
            )

            logger.info(
                f"分析完成: Tokens={result.usage.total_tokens}, Score={result.importance_score}"
            )

            return result

        except ValueError as e:
            # 解析错误：可能是格式问题，记录并重试
            parse_error_count += 1
            last_error = e
            logger.warning(
                f"JSON 解析失败 (尝试 {attempt + 1}/{max_retries}, 解析错误 #{parse_error_count}): {e}"
            )

            # 如果还有重试机会，等待后重试
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避

        except Exception as e:
            last_error = e
            logger.warning(f"API 调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")

            # 如果还有重试机会，等待后重试
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避

    # 所有重试都失败
    logger.error(f"API 调用失败，已达到最大重试次数 ({max_retries})")
    if parse_error_count > 0:
        logger.error(f"包含 {parse_error_count} 次解析错误，可能是 LLM 返回格式不规范")
    if last_error:
        raise last_error
    raise Exception("API 调用失败")
