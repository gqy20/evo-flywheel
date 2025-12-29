"""Streamlit 论文详情页

显示单篇论文的完整信息，包括分析结果和反馈功能
"""

from typing import Any

import streamlit as st

from evo_flywheel.logging import get_logger
from evo_flywheel.web.api_client import APIClient

logger = get_logger(__name__)


def get_paper_detail(paper_id: int) -> dict[str, Any] | None:
    """获取论文详情

    Args:
        paper_id: 论文 ID

    Returns:
        dict | None: 论文详情字典，失败时返回 None
    """
    try:
        client = APIClient()
        result = client.get_paper_detail(paper_id=paper_id)

        if result is None:
            logger.error(f"论文详情获取失败: paper_id={paper_id}")
            return None

        return result

    except Exception as e:
        logger.error(f"论文详情获取失败: {e}")
        return None


def submit_feedback(paper_id: int, rating: int, comment: str = "") -> bool:
    """提交论文反馈

    Args:
        paper_id: 论文 ID
        rating: 评分 (1-5)
        comment: 评论内容

    Returns:
        bool: 是否提交成功
    """
    try:
        client = APIClient()
        result = client.submit_feedback(
            paper_id=paper_id,
            rating=rating,
            comment=comment,
        )

        if result is None:
            logger.error(f"反馈提交失败: paper_id={paper_id}")
            return False

        success: bool = result.get("success", False)
        return success

    except Exception as e:
        logger.error(f"反馈提交失败: {e}")
        return False


def render_feedback_section(paper_id: int) -> None:
    """渲染反馈区域

    Args:
        paper_id: 论文 ID
    """
    st.subheader("📝 论文反馈")

    with st.expander("提交您对这篇论文的评价", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            rating = st.slider(
                "评分",
                min_value=1,
                max_value=5,
                value=3,
                step=1,
                help="1=不相关, 5=非常重要",
                key=f"feedback_rating_{paper_id}",
            )

        with col2:
            st.caption("💡 您的评分将帮助改进推荐系统")

        comment = st.text_area(
            "评论 (可选)",
            placeholder="分享您对这篇论文的看法...",
            key=f"feedback_comment_{paper_id}",
            height=100,
        )

        if st.button("提交反馈", key=f"feedback_submit_{paper_id}", type="secondary"):
            if submit_feedback(paper_id=paper_id, rating=rating, comment=comment):
                st.success("✅ 感谢您的反馈！")
                st.balloons()
            else:
                st.error("❌ 反馈提交失败，请稍后重试")


def render_paper_info(paper: dict[str, Any]) -> None:
    """渲染论文基本信息

    Args:
        paper: 论文数据字典
    """
    st.markdown("## 📄 基本信息")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**标题**: {paper.get('title', '无标题')}")
        st.markdown(f"**期刊**: {paper.get('journal', '未知')}")
        st.markdown(f"**发布日期**: {paper.get('publication_date', '未知')}")

    with col2:
        st.markdown(f"**DOI**: {paper.get('doi', '无')}")
        if paper.get("url"):
            st.markdown(f"**链接**: [{paper.get('url')}]({paper.get('url')})")

    authors = paper.get("authors", [])
    if authors:
        st.markdown(f"**作者**: {', '.join(authors)}")

    if paper.get("abstract"):
        st.markdown("---")
        st.markdown("### 📝 摘要")
        st.markdown(f"> {paper.get('abstract')}")


def render_analysis_info(paper: dict[str, Any]) -> None:
    """渲染分析结果信息

    Args:
        paper: 论文数据字典
    """
    st.markdown("---")
    st.markdown("## 🤖 AI 分析结果")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "重要性评分",
            value=paper.get("importance_score", 0),
            help="基于进化生物学相关性的 AI 评分",
        )

    with col2:
        taxa = paper.get("taxa", "未知")
        st.metric(
            "研究物种",
            value=taxa if len(taxa) < 20 else taxa[:20] + "...",
            help="研究涉及的物种分类",
        )

    # 关键发现
    key_findings = paper.get("key_findings", [])
    if key_findings:
        st.markdown("### 🔬 关键发现")
        for i, finding in enumerate(key_findings, 1):
            st.markdown(f"{i}. {finding}")

    # 进化机制
    if paper.get("evolutionary_mechanism"):
        st.markdown("### 🧬 进化机制")
        st.markdown(f"**{paper.get('evolutionary_mechanism')}**")

    # 分析日期
    if paper.get("analysis_date"):
        st.caption(f"📅 分析日期: {paper.get('analysis_date')}")


def render() -> None:
    """渲染论文详情页"""
    st.title("📄 论文详情")
    st.markdown("---")

    # 获取论文 ID 参数
    paper_id = st.query_params.get("id")

    if not paper_id:
        st.error("缺少论文 ID 参数")
        st.info("请从论文列表或搜索结果中选择一篇论文查看详情")
        return

    try:
        paper_id_int = int(paper_id)
    except ValueError:
        st.error("无效的论文 ID")
        return

    # 获取论文详情
    paper = get_paper_detail(paper_id=paper_id_int)

    if paper is None:
        st.error("论文详情加载失败")
        st.info("该论文可能不存在或已被删除")
        return

    # 渲染论文信息
    render_paper_info(paper)

    # 渲染分析结果
    render_analysis_info(paper)

    # 渲染反馈区域
    st.markdown("---")
    render_feedback_section(paper_id=paper_id_int)

    # 返回按钮
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col2:
        if st.button("← 返回列表", key="detail_back", use_container_width=True):
            st.query_params.clear()
            st.rerun()
