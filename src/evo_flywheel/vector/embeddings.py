"""Embedding 服务模块

提供文本向量化功能，使用远程 Embedding API
"""

from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx

from evo_flywheel.config import get_settings
from evo_flywheel.logging import get_logger

logger = get_logger(__name__)

# 全局客户端单例
_client: httpx.Client | None = None


def get_embedding_client() -> httpx.Client:
    """获取 Embedding API 客户端

    Returns:
        httpx.Client: HTTP 客户端实例

    Raises:
        ValueError: 未配置 API Key 或 URL
    """
    global _client

    if _client is not None:
        return _client

    settings = get_settings()

    # 从配置获取
    api_url = settings.embedding_api_url
    api_key = settings.embedding_api_key

    if not api_key:
        raise ValueError("未配置 EMBEDDING_API_KEY 环境变量")

    # 构造完整的 base URL（如果需要）
    # 用户配置的 base_url 应该是 https://api.xxx.com/v1 形式
    # httpx 会自动将其与 "/embeddings" 拼接
    _client = httpx.Client(
        base_url=api_url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30.0,
    )

    return _client


def get_embedding_model() -> str:
    """获取配置的 Embedding 模型名称

    Returns:
        str: 模型名称
    """
    settings = get_settings()
    return settings.embedding_model


def generate_embedding(text: str, model: str | None = None) -> list[float]:
    """生成单个文本的向量表示

    Args:
        text: 输入文本
        model: Embedding 模型名称（默认使用配置中的模型）

    Returns:
        list[float]: 向量表示（384维或1536维）

    Raises:
        ValueError: 文本为空
        Exception: API 调用失败
    """
    if not text or not text.strip():
        raise ValueError("文本不能为空")

    # 使用传入的模型，或使用配置中的默认模型
    if model is None:
        model = get_embedding_model()

    client = get_embedding_client()

    try:
        logger.debug(f"生成文本向量: {text[:50]}...")

        # 调用 OpenAI 兼容的 Embedding API
        response = client.post(
            "/embeddings",
            json={
                "input": text,
                "model": model,
            },
        )

        response.raise_for_status()

        # 解析响应
        try:
            data = response.json()
        except AttributeError:
            # Mock 对象直接返回数据
            data = response

        # 提取向量
        embedding: list[float] = data["data"][0]["embedding"]
        logger.debug(f"向量维度: {len(embedding)}")

        return embedding

    except httpx.HTTPStatusError as e:
        logger.error(f"Embedding API 调用失败: {e.response.status_code} {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"生成向量失败: {e}")
        raise


def generate_embeddings_batch(
    texts: list[str],
    model: str | None = None,
    max_concurrent: int = 5,
    continue_on_error: bool = False,
) -> list[list[float] | None]:
    """批量生成文本向量

    Args:
        texts: 文本列表
        model: Embedding 模型名称（默认使用配置中的模型）
        max_concurrent: 最大并发数
        continue_on_error: 遇到错误是否继续

    Returns:
        list[list[float] | None]: 向量列表，失败的项为 None
    """
    if not texts:
        return []

    # 使用传入的模型，或使用配置中的默认模型
    if model is None:
        model = get_embedding_model()

    results: list[list[float] | None] = [None] * len(texts)

    def _embed_single(index: int, text: str) -> tuple[int, list[float] | None]:
        """嵌入单篇文本"""
        try:
            vector = generate_embedding(text, model)
            return (index, vector)
        except Exception as e:
            logger.warning(f"文本 {index} 向量化失败: {e}")
            if continue_on_error:
                return (index, None)
            raise

    # 使用线程池并发处理
    with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        futures = {executor.submit(_embed_single, i, text): i for i, text in enumerate(texts)}

        for future in as_completed(futures):
            try:
                index, vector = future.result()
                results[index] = vector
            except Exception as e:
                index = futures[future]
                logger.error(f"处理文本 {index} 时发生错误: {e}")
                if not continue_on_error:
                    raise
                results[index] = None

    logger.info(f"批量向量化完成: {len(texts)} 篇, 成功: {sum(1 for v in results if v)}")

    return results
