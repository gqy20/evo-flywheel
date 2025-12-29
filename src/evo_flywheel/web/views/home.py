"""Streamlit 首页

展示今日报告、统计数据和推荐论文
"""

from typing import Any

import streamlit as st

from evo_flywheel.logging import get_logger
from evo_flywheel.web.api_client import APIClient

logger = get_logger(__name__)


def get_analysis_status() -> dict[str, Any] | None:
    """获取分析状态

    Returns:
        分析状态字典，失败返回 None
    """
    try:
        client = APIClient()
        return client.get_analysis_status()
    except Exception as e:
        logger.error(f"获取分析状态失败: {e}")
        return None


def trigger_analysis(limit: int | None = 10) -> bool:
    """触发论文分析

    Args:
        limit: 分析论文数量限制，None 表示全部

    Returns:
        bool: 是否成功
    """
    try:
        client = APIClient()
        # None 传递给 API，表示不限制数量
        params: dict[str, int] = {}
        if limit is not None:
            params["limit"] = limit
        result = client.trigger_analysis(**params)

        if result is None:
            logger.error("触发分析失败")
            return False

        return True

    except Exception as e:
        logger.error(f"触发分析失败: {e}")
        return False


def rebuild_embeddings(force: bool = False) -> bool:
    """重建向量索引

    Args:
        force: 是否强制重建所有论文的向量

    Returns:
        bool: 是否成功
    """
    try:
        client = APIClient()
        result = client.rebuild_embeddings(force=force)

        if result is None:
            logger.error("重建索引失败")
            return False

        return True

    except Exception as e:
        logger.error(f"重建索引失败: {e}")
        return False


def render_stats_section() -> None:
    """渲染统计数据区域"""
    st.subheader("📊 统计数据")

    try:
        client = APIClient()
        stats = client.get_stats_overview()

        if stats is None:
            st.error("统计数据加载失败")
            return

        # 显示统计卡片
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="论文总数", value=stats.get("total_papers", 0))
        with col2:
            st.metric(label="今日新增", value=stats.get("today_new", 0))
        with col3:
            st.metric(
                label="分析率",
                value=f"{stats.get('analysis_rate', 0):.1f}%",
                help="已分析论文比例",
            )

    except Exception as e:
        logger.error(f"统计数据获取失败: {e}")
        st.error("统计数据加载失败")


def render_recommendations_section() -> None:
    """渲染推荐论文区域"""
    st.subheader("⭐ 重点推荐")

    try:
        client = APIClient()
        result = client.get_papers(skip=0, limit=5, min_score=80)

        if result is None:
            st.error("推荐论文加载失败")
            return

        papers = result.get("papers", [])

        if not papers:
            st.info("暂无推荐论文")
            return

        for i, paper in enumerate(papers, 1):
            title = paper.get("title", "无标题")
            authors = paper.get("authors", [])
            journal = paper.get("journal", "未知")
            pub_date = paper.get("publication_date", "未知")
            score = paper.get("importance_score", 0)
            abstract = paper.get("abstract", "")

            with st.expander(f"{i}. {title} (评分: {score})", expanded=i == 1):
                st.markdown(f"**作者**: {', '.join(authors) if authors else '未知'}")
                st.markdown(f"**期刊**: {journal}")
                st.markdown(f"**发表日期**: {pub_date}")
                st.markdown(f"**重要性评分**: :star: {score}/100")

                if abstract:
                    show_abstract = st.toggle("显示摘要", key=f"abstract_{paper.get('id')}")
                    if show_abstract:
                        st.markdown(f"> {abstract}")

    except Exception as e:
        logger.error(f"推荐论文获取失败: {e}")
        st.error("推荐论文加载失败")


def render_daily_report_section() -> None:
    """渲染今日报告区域"""
    st.subheader("📅 今日报告")

    try:
        client = APIClient()
        report = client.get_today_report()

        if report is None:
            st.warning("今日报告加载失败")
            return

        count = report.get("count", 0)
        papers = report.get("papers", [])
        date_str = report.get("date", "未知")

        if count > 0:
            st.success(f"今日 ({date_str}) 共采集 {count} 篇论文")

            if papers:
                st.markdown("**今日亮点**:")
                for paper in papers[:5]:
                    title = paper.get("title", "无标题")
                    score = paper.get("importance_score", 0)
                    st.markdown(f"- {title} (评分: {score})")
        else:
            st.info(f"今日 ({date_str}) 暂无新论文")
            st.caption("报告将在每日自动采集后生成")

    except Exception as e:
        logger.error(f"今日报告获取失败: {e}")
        st.warning("今日报告加载失败")


def render_analysis_progress() -> None:
    """渲染分析进度显示"""
    status = get_analysis_status()

    if status is None:
        st.warning("⚠️ 无法获取分析状态")
        return

    total = status.get("total", 0)
    analyzed = status.get("analyzed", 0)
    unanalyzed = status.get("unanalyzed", 0)
    progress = status.get("progress", 0)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总论文", total)
    with col2:
        st.metric("已分析", analyzed)
    with col3:
        st.metric("待分析", unanalyzed)

    if total > 0:
        st.progress(progress / 100, text=f"分析进度: {progress:.1f}%")

    if unanalyzed > 0:
        st.info(f"📌 还有 {unanalyzed} 篇论文待分析")
    elif analyzed > 0:
        st.success("✅ 所有论文已完成分析")


def render_admin_panel() -> None:
    """渲染管理面板区域"""
    st.subheader("🔧 系统管理")

    with st.expander("管理操作", expanded=False):
        # 显示分析进度
        st.markdown("### 📈 分析与索引状态")
        render_analysis_progress()

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🤖 AI 分析")
            analyze_all = st.checkbox(
                "分析全部论文",
                value=False,
                help="选中后将分析所有未分析的论文",
                key="admin_analyze_all",
            )

            if not analyze_all:
                limit = st.number_input(
                    "分析数量",
                    min_value=1,
                    max_value=10000,
                    value=10,
                    step=10,
                    help="批量分析未分析的论文数量",
                    key="admin_analysis_limit",
                )
            else:
                limit = None
                st.info("将分析所有未分析的论文")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button(
                    "🚀 触发分析",
                    key="admin_trigger_analysis",
                    type="secondary",
                    use_container_width=True,
                ):
                    with st.spinner("正在分析中..."):
                        if trigger_analysis(limit=limit):
                            if limit is None:
                                st.success("✅ 成功触发全部分析")
                            else:
                                st.success(f"✅ 成功触发分析，最多处理 {limit} 篇论文")
                            st.balloons()
                        else:
                            st.error("❌ 分析触发失败，请稍后重试")

            with col_btn2:
                if st.button("🔄 刷新状态", key="admin_refresh_status", use_container_width=True):
                    st.rerun()

            st.caption("💡 定时调度器会自动处理，仅在需要时手动触发")

        with col2:
            st.markdown("#### 🔍 向量索引")

            # 显示索引进度
            status = get_analysis_status()
            if status:
                # 使用 embedding_rate 作为索引进度
                total = status.get("total", 0)
                analyzed = status.get("analyzed", 0)
                # 简单估算：已向量化 ≈ 已分析
                embedded = analyzed  # API 没有单独的 embedded 统计
                if total > 0:
                    embed_progress = (embedded / total) * 100
                    st.progress(embed_progress / 100, text=f"索引进度: {embed_progress:.1f}%")
                    st.caption(f"已向量化: {embedded}/{total}")

            st.markdown("**索引操作**")

            col_btn3, col_btn4 = st.columns(2)
            with col_btn3:
                if st.button(
                    "▶️ 继续索引",
                    key="admin_continue_embeddings",
                    type="secondary",
                    use_container_width=True,
                ):
                    with st.spinner("正在继续索引..."):
                        if rebuild_embeddings(force=False):
                            st.success("✅ 成功触发增量索引")
                            st.balloons()
                        else:
                            st.error("❌ 索引发起失败，请稍后重试")

            with col_btn4:
                force_confirmed = st.checkbox(
                    "确认强制重建", value=False, key="confirm_force_rebuild"
                )
                if (
                    st.button(
                        "🔄 强制重建",
                        key="admin_force_rebuild",
                        type="secondary",
                        use_container_width=True,
                    )
                    and force_confirmed
                ):
                    with st.spinner("正在重建索引..."):
                        if rebuild_embeddings(force=True):
                            st.success("✅ 成功触发强制重建索引")
                            st.balloons()
                        else:
                            st.error("❌ 索引进建失败，请稍后重试")

            st.caption("💡 继续索引仅处理未向量化的论文，强制重建会重新处理全部")

        st.markdown("---")
        st.info(
            """
            **管理提示**:
            - 这些操作通常由定时调度器自动完成
            - 手动触发适用于系统维护或故障恢复
            - 分析和向量化可能需要几分钟时间
            - 使用"刷新状态"按钮查看最新进度
            """
        )


def render() -> None:
    """渲染首页"""
    st.title("🧬 Evo-Flywheel - 进化生物学学术飞轮")
    st.markdown("---")

    # 统计数据
    render_stats_section()

    st.markdown("---")

    # 推荐论文
    render_recommendations_section()

    st.markdown("---")

    # 今日报告
    render_daily_report_section()

    st.markdown("---")

    # 管理面板
    render_admin_panel()

    # 页脚
    st.markdown("---")
    st.caption("💡 提示: 使用左侧菜单导航到其他页面")
