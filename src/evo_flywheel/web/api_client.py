"""FastAPI 客户端封装

提供 Web 界面与 FastAPI 后端通信的统一接口
"""

from typing import Any

import requests
from requests import Response

from evo_flywheel.config import get_settings
from evo_flywheel.logging import get_logger

logger = get_logger(__name__)


def _parse_json(response: Response) -> dict[str, Any] | None:
    """解析响应 JSON

    Args:
        response: HTTP 响应对象

    Returns:
        解析后的字典，失败返回 None
    """
    try:
        result: Any = response.json()
        if isinstance(result, dict):
            return result
        return None
    except ValueError:
        return None


class APIClient:
    """FastAPI REST API 客户端

    提供统一的方法调用后端 API，处理错误和重试逻辑
    """

    def __init__(self, base_url: str | None = None, timeout: int = 30):
        """初始化 API 客户端

        Args:
            base_url: API 基础 URL，默认从配置读取
            timeout: 请求超时时间（秒）
        """
        settings = get_settings()
        self.base_url = base_url or getattr(settings, "api_base_url", "http://localhost:8000")
        self.timeout = timeout

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any] | None:
        """发送 HTTP 请求

        Args:
            method: HTTP 方法 (GET, POST, PUT, DELETE)
            endpoint: API 端点路径
            **kwargs: 传递给 requests 的参数

        Returns:
            响应 JSON 数据，失败返回 None
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response: Response = requests.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
            return _parse_json(response)

        except requests.HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            logger.warning(f"HTTP 错误: {status_code} - {e}")
            return None
        except requests.ConnectionError:
            logger.error("连接错误")
            return None
        except requests.RequestException as e:
            logger.error(f"请求异常: {e}")
            return None

    def get_stats_overview(self) -> dict[str, Any] | None:
        """获取系统概览统计

        Returns:
            统计数据字典，失败返回 None
        """
        return self._request("GET", "/api/v1/stats/overview")

    def get_papers(
        self,
        skip: int = 0,
        limit: int = 20,
        taxa: str | None = None,
        min_score: int | None = None,
    ) -> dict[str, Any] | None:
        """获取论文列表

        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            taxa: 筛选分类群
            min_score: 最低重要性评分

        Returns:
            论文列表数据，失败返回 None
        """
        params: dict[str, str | int] = {"skip": skip, "limit": limit}
        if taxa:
            params["taxa"] = taxa
        if min_score is not None:
            params["min_score"] = min_score

        return self._request("GET", "/api/v1/papers", params=params)

    def get_paper(self, paper_id: int) -> dict[str, Any] | None:
        """获取单篇论文详情

        Args:
            paper_id: 论文 ID

        Returns:
            论文详情数据，失败返回 None
        """
        return self._request("GET", f"/api/v1/papers/{paper_id}")

    def get_paper_detail(self, paper_id: int) -> dict[str, Any] | None:
        """获取单篇论文详情（别名方法）

        Args:
            paper_id: 论文 ID

        Returns:
            论文详情数据，失败返回 None
        """
        return self.get_paper(paper_id)

    def semantic_search(self, query: str, limit: int = 10) -> dict[str, Any] | None:
        """语义搜索论文

        Args:
            query: 搜索查询
            limit: 返回结果数

        Returns:
            搜索结果数据，失败返回 None
        """
        params: dict[str, str | int] = {"q": query, "limit": limit}
        return self._request("GET", "/api/v1/search/semantic", params=params)

    def similar_papers(self, paper_id: int, limit: int = 5) -> dict[str, Any] | None:
        """查找相似论文

        Args:
            paper_id: 参考论文 ID
            limit: 返回结果数

        Returns:
            相似论文数据，失败返回 None
        """
        params: dict[str, str | int] = {"paper_id": paper_id, "limit": limit}
        return self._request("POST", "/api/v1/search/similar", params=params)

    def hybrid_search(
        self,
        query: str,
        taxa: str | None = None,
        min_score: int | None = None,
        limit: int = 10,
    ) -> dict[str, Any] | None:
        """混合搜索（语义+元数据过滤）

        Args:
            query: 搜索查询
            taxa: 物种过滤
            min_score: 最低重要性评分
            limit: 返回结果数

        Returns:
            搜索结果数据，失败返回 None
        """
        params: dict[str, str | int] = {"q": query, "limit": limit}
        if taxa:
            params["taxa"] = taxa
        if min_score is not None:
            params["min_score"] = min_score

        return self._request("GET", "/api/v1/search/hybrid", params=params)

    def get_today_report(self) -> dict[str, Any] | None:
        """获取今日报告

        Returns:
            报告数据，失败返回 None
        """
        return self._request("GET", "/api/v1/reports/today")

    def get_report_by_date(self, report_date: str) -> dict[str, Any] | None:
        """获取指定日期的报告

        Args:
            report_date: 日期字符串 (YYYY-MM-DD)

        Returns:
            报告数据，失败返回 None
        """
        return self._request("GET", f"/api/v1/reports/{report_date}")

    def generate_report(self, date_str: str | None = None) -> dict[str, Any] | None:
        """手动生成指定日期的报告

        Args:
            date_str: 日期字符串 (YYYY-MM-DD)，默认今天

        Returns:
            生成的报告数据，失败返回 None
        """
        params: dict[str, str] = {}
        if date_str:
            params["date_str"] = date_str

        return self._request("POST", "/api/v1/reports/generate", params=params)

    def analyze_paper(self, paper_id: int) -> dict[str, Any] | None:
        """分析单篇论文

        Args:
            paper_id: 论文 ID

        Returns:
            分析结果数据，失败返回 None
        """
        return self._request("POST", f"/api/v1/papers/{paper_id}/analyze")

    def submit_feedback(
        self,
        paper_id: int,
        rating: int,
        is_helpful: bool | None = None,
        comment: str | None = None,
    ) -> dict[str, Any] | None:
        """提交用户反馈

        Args:
            paper_id: 论文 ID
            rating: 评分 1-5
            is_helpful: 是否有帮助
            comment: 评论

        Returns:
            反馈数据，失败返回 None
        """
        data: dict[str, int | str | bool | None] = {
            "paper_id": paper_id,
            "rating": rating,
        }
        if is_helpful is not None:
            data["is_helpful"] = is_helpful
        if comment:
            data["comment"] = comment

        return self._request("POST", "/api/v1/feedback", json=data)

    def get_feedbacks(self, paper_id: int | None = None) -> dict[str, Any] | None:
        """获取反馈列表

        Args:
            paper_id: 论文 ID 筛选

        Returns:
            反馈列表数据，失败返回 None
        """
        params: dict[str, int] = {}
        if paper_id is not None:
            params["paper_id"] = paper_id

        return self._request("GET", "/api/v1/feedback", params=params)

    def trigger_collection(
        self, days: int = 7, sources: str | None = None
    ) -> dict[str, Any] | None:
        """触发数据采集

        Args:
            days: 采集最近几天的论文
            sources: 指定数据源（逗号分隔）

        Returns:
            采集结果数据，失败返回 None
        """
        params: dict[str, str | int] = {"days": days}
        if sources:
            params["sources"] = sources

        return self._request("POST", "/api/v1/collection/fetch", params=params)

    def get_collection_status(self) -> dict[str, Any] | None:
        """获取采集状态

        Returns:
            采集状态数据，失败返回 None
        """
        return self._request("GET", "/api/v1/collection/status")

    def trigger_analysis(
        self, limit: int = 50, min_score: int | None = None
    ) -> dict[str, Any] | None:
        """触发论文分析

        Args:
            limit: 分析论文数量限制
            min_score: 最低重要性评分过滤

        Returns:
            分析结果数据，失败返回 None
        """
        params: dict[str, int] = {"limit": limit}
        if min_score is not None:
            params["min_score"] = min_score

        return self._request("POST", "/api/v1/analysis/trigger", params=params)

    def get_analysis_status(self) -> dict[str, Any] | None:
        """获取分析状态

        Returns:
            分析状态数据，失败返回 None
        """
        return self._request("GET", "/api/v1/analysis/status")

    def rebuild_embeddings(self, force: bool = False) -> dict[str, Any] | None:
        """重建向量索引

        Args:
            force: 是否强制重建所有论文的向量

        Returns:
            重建结果数据，失败返回 None
        """
        params: dict[str, bool] = {"force": force}
        return self._request("POST", "/api/v1/embeddings/rebuild", params=params)

    def get_embeddings_status(self) -> dict[str, Any] | None:
        """获取向量索引状态

        Returns:
            索引状态数据，失败返回 None
        """
        return self._request("GET", "/api/v1/embeddings/status")

    # 飞轮控制相关方法

    def trigger_flywheel(self) -> dict[str, Any] | None:
        """手动触发飞轮

        Returns:
            飞轮执行结果，包含 collected, analyzed, report_generated
        """
        return self._request("POST", "/api/v1/flywheel/trigger")

    def get_flywheel_status(self) -> dict[str, Any] | None:
        """获取飞轮状态

        Returns:
            飞轮状态数据，包含 running, last_run, next_run
        """
        return self._request("GET", "/api/v1/flywheel/status")

    def start_flywheel_scheduler(self) -> dict[str, Any] | None:
        """启动飞轮调度器

        Returns:
            操作结果，包含 status="started"
        """
        return self._request("POST", "/api/v1/flywheel/schedule", json={"action": "start"})

    def stop_flywheel_scheduler(self) -> dict[str, Any] | None:
        """停止飞轮调度器

        Returns:
            操作结果，包含 status="stopped"
        """
        return self._request("POST", "/api/v1/flywheel/schedule", json={"action": "stop"})

    def generate_deep_report(self, date_str: str | None = None) -> dict[str, Any] | None:
        """生成深度报告

        Args:
            date_str: 日期字符串 (YYYY-MM-DD)，默认为今天

        Returns:
            生成的报告数据
        """
        params: dict[str, str] = {}
        if date_str:
            params["date"] = date_str

        # 使用 params 传递查询参数（后端使用 Query 接收）
        return self._request("POST", "/api/v1/reports/generate-deep", params=params)

    def get_deep_report(self, report_id: int) -> dict[str, Any] | None:
        """获取指定 ID 的深度报告详情

        Args:
            report_id: 报告 ID

        Returns:
            报告详情数据，失败返回 None
        """
        return self._request("GET", f"/api/v1/reports/deep/{report_id}")

    def get_deep_reports_by_date(self, report_date: str) -> dict[str, Any] | None:
        """获取指定日期的所有深度报告

        Args:
            report_date: 日期字符串 (YYYY-MM-DD)

        Returns:
            报告列表数据，失败返回 None
        """
        return self._request("GET", f"/api/v1/reports/deep/date/{report_date}")

    def list_deep_reports(self, limit: int = 10) -> dict[str, Any] | None:
        """获取深度报告列表

        Args:
            limit: 返回数量限制

        Returns:
            报告列表数据，失败返回 None
        """
        return self._request("GET", "/api/v1/reports/deep", params={"limit": limit})
