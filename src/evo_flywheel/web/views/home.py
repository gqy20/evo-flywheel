"""Streamlit 首页

展示今日报告、统计数据和推荐论文
"""

import time
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


def get_embeddings_status() -> dict[str, Any] | None:
    """获取索引进度

    Returns:
        索引状态字典，失败返回 None
    """
    try:
        client = APIClient()
        return client.get_embeddings_status()
    except Exception as e:
        logger.error(f"获取索引进度失败: {e}")
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
                    # 使用 st.status 显示实时进度
                    with st.status("正在分析...", expanded=True) as status:
                        # 获取初始状态
                        initial_status = get_analysis_status()
                        initial_unanalyzed = (
                            initial_status.get("unanalyzed", 0) if initial_status else 0
                        )

                        # 触发分析
                        result = trigger_analysis(limit=limit)
                        if result:
                            status.update(label="分析进行中...", state="running")

                            # 轮询进度
                            max_wait = 60  # 最多等待 60 秒
                            start_time = time.time()
                            last_unanalyzed = initial_unanalyzed
                            placeholder = st.empty()

                            while time.time() - start_time < max_wait:
                                current_status = get_analysis_status()
                                if current_status:
                                    current_unanalyzed = current_status.get("unanalyzed", 0)
                                    total = current_status.get("total", 0)
                                    analyzed = current_status.get("analyzed", 0)
                                    progress = current_status.get("progress", 0)

                                    # 使用占位符显示进度（会替换之前的内容）
                                    with placeholder.container():
                                        st.metric(
                                            "已分析", f"{analyzed}/{total}", f"{progress:.1f}%"
                                        )
                                        st.progress(progress / 100)

                                    # 检查是否完成
                                    if current_unanalyzed == 0:
                                        status.update(
                                            label="✅ 分析完成！",
                                            state="complete",
                                            expanded=False,
                                        )
                                        placeholder.empty()
                                        st.balloons()
                                        break
                                    # 检查是否有进展
                                    if current_unanalyzed < last_unanalyzed:
                                        last_unanalyzed = current_unanalyzed

                                time.sleep(2)  # 每 2 秒轮询一次
                            else:
                                # 超时，但已触发
                                placeholder.empty()
                                status.update(
                                    label="⏳ 分析已触发（后台运行中）",
                                    state="running",
                                    expanded=False,
                                )
                                st.info("💡 分析正在后台进行，请稍后刷新状态查看结果")
                        else:
                            status.update(label="❌ 分析触发失败", state="error")
                            st.error("❌ 分析触发失败，请稍后重试")

            with col_btn2:
                if st.button("🔄 刷新状态", key="admin_refresh_status", use_container_width=True):
                    st.rerun()

            st.caption("💡 定时调度器会自动处理，仅在需要时手动触发")

        with col2:
            st.markdown("#### 🔍 向量索引")

            # 显示索引进度
            embed_status = get_embeddings_status()
            if embed_status:
                total = embed_status.get("total", 0)
                embedded = embed_status.get("embedded", 0)
                unembedded = embed_status.get("unembedded", 0)
                progress = embed_status.get("progress", 0)

                if total > 0:
                    st.progress(progress / 100, text=f"索引进度: {progress:.1f}%")
                    st.caption(f"已向量化: {embedded}/{total} (待处理: {unembedded})")

            st.markdown("**索引操作**")

            col_btn3, col_btn4 = st.columns(2)
            with col_btn3:
                if st.button(
                    "▶️ 继续索引",
                    key="admin_continue_embeddings",
                    type="secondary",
                    use_container_width=True,
                ):
                    with st.status("正在索引...", expanded=True) as status:
                        # 获取初始状态
                        initial_status = get_embeddings_status()
                        initial_unembedded = (
                            initial_status.get("unembedded", 0) if initial_status else 0
                        )

                        result = rebuild_embeddings(force=False)
                        if result:
                            status.update(label="索引进行中...", state="running")

                            # 轮询进度
                            max_wait = 60  # 最多等待 60 秒
                            start_time = time.time()
                            last_unembedded = initial_unembedded
                            placeholder = st.empty()

                            while time.time() - start_time < max_wait:
                                current_status = get_embeddings_status()
                                if current_status:
                                    total = current_status.get("total", 0)
                                    embedded = current_status.get("embedded", 0)
                                    unembedded = current_status.get("unembedded", 0)
                                    progress = current_status.get("progress", 0)

                                    # 使用占位符显示进度（会替换之前的内容）
                                    with placeholder.container():
                                        st.metric(
                                            "已向量化", f"{embedded}/{total}", f"{progress:.1f}%"
                                        )
                                        st.progress(progress / 100)

                                    # 检查是否完成
                                    if unembedded == 0:
                                        status.update(
                                            label="✅ 索引完成！",
                                            state="complete",
                                            expanded=False,
                                        )
                                        placeholder.empty()
                                        st.balloons()
                                        break
                                    # 检查是否有进展
                                    if unembedded < last_unembedded:
                                        last_unembedded = unembedded

                                time.sleep(2)
                            else:
                                placeholder.empty()
                                status.update(
                                    label="⏳ 索引已触发（后台运行中）",
                                    state="running",
                                    expanded=False,
                                )
                                st.info("💡 索引正在后台进行，请稍后刷新状态查看结果")
                        else:
                            status.update(label="❌ 索引发起失败", state="error")
                            st.error("❌ 索引发起失败，请稍后重试")

            with col_btn4:
                if st.button(
                    "🔄 强制重建",
                    key="admin_force_rebuild",
                    type="secondary",
                    use_container_width=True,
                ):
                    with st.status("正在重建索引...", expanded=True) as status:
                        result = rebuild_embeddings(force=True)
                        if result:
                            status.update(
                                label="⏳ 强制重建已触发（后台运行中）",
                                state="running",
                                expanded=False,
                            )
                            st.info("💡 强制重建正在后台进行，可能需要较长时间")
                            st.balloons()
                        else:
                            status.update(label="❌ 索引进建失败", state="error")
                            st.error("❌ 索引进建失败，请稍后重试")

            st.caption("💡 继续索引仅处理未向量化的论文，强制重建会重新处理全部")

        st.markdown("---")
        st.info(
            """
            **管理提示**:
            - 这些操作通常由定时调度器自动完成
            - 手动触发适用于系统维护或故障恢复
            - 分析和向量化可能需要几分钟时间
            - 进度会实时更新，完成后自动刷新
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
