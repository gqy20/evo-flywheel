"""飞轮控制页面

提供手动触发飞轮、查看状态、控制调度器和生成报告的 UI
"""

import time
from datetime import datetime

import streamlit as st

from evo_flywheel.logging import get_logger
from evo_flywheel.web.api_client import APIClient

logger = get_logger(__name__)


def render() -> None:
    """渲染飞轮控制页面"""
    client = APIClient()
    render_flywheel_page(client)


def render_flywheel_page(client: APIClient) -> None:
    st.title("🎯 飞轮控制")
    st.markdown("---")

    # 初始化 session state
    if "flywheel_status" not in st.session_state:
        st.session_state.flywheel_status = None
    if "trigger_result" not in st.session_state:
        st.session_state.trigger_result = None
    if "report_result" not in st.session_state:
        st.session_state.report_result = None

    # 状态卡片 - 自动刷新
    st.subheader("📊 飞轮状态")
    status_col1, status_col2, status_col3 = st.columns(3)

    with status_col1:
        # 刷新按钮
        if st.button("🔄 刷新状态", key="refresh_status", use_container_width=True):
            st.session_state.flywheel_status = client.get_flywheel_status()
            st.rerun()

    # 获取并显示状态
    status = st.session_state.flywheel_status
    if status is None:
        with status_col2:
            st.info("正在加载状态...")
        status = client.get_flywheel_status()
        st.session_state.flywheel_status = status

    if status:
        with status_col2:
            running = status.get("running", False)
            status_text = "🟢 运行中" if running else "🔴 已停止"
            st.metric("调度器状态", status_text)

        with status_col3:
            last_run = status.get("last_run")
            if last_run:
                try:
                    last_run_dt = datetime.fromisoformat(last_run)
                    time_ago = _format_time_ago(last_run_dt)
                    st.metric("上次运行", time_ago)
                except (ValueError, OSError):
                    st.metric("上次运行", last_run[:19] if len(last_run) > 19 else last_run)
            else:
                st.metric("上次运行", "从未运行")

        next_run = status.get("next_run")
        if next_run:
            st.caption(f"⏰ 下次运行: {next_run[:19] if len(next_run) > 19 else next_run}")

    st.markdown("---")

    # 手动触发区域
    st.subheader("🚀 手动触发飞轮")
    st.markdown("立即执行完整的飞轮流程：采集论文 → 分析论文 → 生成报告")

    trigger_col1, trigger_col2 = st.columns([1, 2])

    with trigger_col1:
        if st.button(
            "▶️ 立即触发", key="trigger_flywheel", use_container_width=True, type="primary"
        ):
            # 清除旧结果
            st.session_state.trigger_result = None
            with st.spinner("飞轮运行中..."):
                result = client.trigger_flywheel()
                st.session_state.trigger_result = result
                st.session_state.flywheel_status = client.get_flywheel_status()
            st.rerun()

    with trigger_col2:
        if st.session_state.trigger_result:
            result = st.session_state.trigger_result
            if result:
                st.success(
                    f"✅ 飞轮运行完成！采集 {result.get('collected', 0)} 篇，"
                    f"分析 {result.get('analyzed', 0)} 篇，"
                    f"报告生成: {'是' if result.get('report_generated') else '否'}"
                )
            else:
                st.error("❌ 飞轮运行失败，请查看日志")

    st.markdown("---")

    # 调度器控制区域
    st.subheader("⚙️ 调度器控制")
    st.markdown("启动或停止自动调度器（每 4 小时自动运行一次）")

    scheduler_col1, scheduler_col2, scheduler_col3 = st.columns(3)

    with scheduler_col1:
        is_running = status.get("running", False) if status else False
        if st.button(
            "▶️ 启动调度器",
            key="start_scheduler",
            use_container_width=True,
            disabled=is_running,
            type="primary" if not is_running else "secondary",
        ):
            result = client.start_flywheel_scheduler()
            if result and result.get("status") == "started":
                st.success("✅ 调度器已启动")
                st.session_state.flywheel_status = client.get_flywheel_status()
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ 启动调度器失败")

    with scheduler_col2:
        if st.button(
            "⏹️ 停止调度器",
            key="stop_scheduler",
            use_container_width=True,
            disabled=not is_running,
        ):
            result = client.stop_flywheel_scheduler()
            if result and result.get("status") == "stopped":
                st.success("✅ 调度器已停止")
                st.session_state.flywheel_status = client.get_flywheel_status()
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ 停止调度器失败")

    with scheduler_col3:
        st.metric("运行间隔", "4 小时")

    st.markdown("---")

    # 报告生成区域
    st.subheader("📄 深度报告生成")
    st.markdown("为指定日期生成深度分析报告")

    report_col1, report_col2, report_col3 = st.columns([1, 1, 2])

    with report_col1:
        report_date = st.date_input("选择日期", value=datetime.now().date())

    with report_col2:
        date_str = report_date.strftime("%Y-%m-%d")
        if st.button("📝 生成报告", key="generate_report", use_container_width=True):
            # 清除旧结果
            st.session_state.report_result = None
            with st.spinner(f"正在生成 {date_str} 的报告..."):
                result = client.generate_deep_report(date_str)
                st.session_state.report_result = result
            st.rerun()

    with report_col3:
        if st.session_state.report_result:
            result = st.session_state.report_result
            if result:
                st.success(
                    f"✅ 报告生成成功！ID: {result.get('id')}, "
                    f"总论文: {result.get('total_papers', 0)}, "
                    f"高价值: {result.get('high_value_papers', 0)}"
                )
            else:
                st.error("❌ 报告生成失败")

    st.markdown("---")

    # 最新报告查看区域
    st.subheader("📖 最新深度报告")
    st.markdown("查看最近生成的深度分析报告")

    # 获取最新报告
    today_str = datetime.now().strftime("%Y-%m-%d")
    reports_response = client.list_deep_reports(limit=5)

    if reports_response and reports_response.get("content"):
        reports = reports_response["content"]
        if reports:
            # 显示报告列表
            for report in reports:
                with st.expander(
                    f"📅 {report.get('report_date', today_str)} - "
                    f"{report.get('total_papers', 0)} 篇论文, "
                    f"{report.get('high_value_papers', 0)} 篇高价值"
                ):
                    # 显示报告内容
                    content = report.get("content", {})
                    if content:
                        # 研究概要
                        if summary := content.get("research_summary"):
                            st.markdown("### 📌 研究概要")
                            st.markdown(summary)

                        # 热点话题
                        if hot_topics := content.get("hot_topics"):
                            st.markdown("### 🔥 热点话题")
                            for topic in hot_topics:
                                st.markdown(
                                    f"- **{topic.get('topic', 'N/A')}**: {topic.get('description', '')}"
                                )

                        # 推荐论文
                        if recommended := content.get("recommended_papers"):
                            st.markdown("### ⭐ 推荐论文")
                            for i, paper in enumerate(recommended[:5], 1):
                                st.markdown(f"{i}. **{paper.get('title', 'N/A')}**")
                                if reason := paper.get("reason"):
                                    st.caption(f"推荐理由: {reason}")
        else:
            st.info("暂无深度报告，请先生成报告")
    else:
        st.info("暂无深度报告，请先生成报告")

    # 自动刷新提示
    st.markdown("---")
    st.caption("💡 提示：状态会自动更新，也可以点击刷新按钮手动更新。")


def _format_time_ago(dt: datetime) -> str:
    """格式化时间为"多久之前"

    Args:
        dt: 目标时间

    Returns:
        格式化的时间字符串
    """
    now = datetime.now(dt.tzinfo)
    delta = now - dt

    seconds = int(delta.total_seconds())

    if seconds < 60:
        return f"{seconds} 秒前"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} 分钟前"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} 小时前"
    else:
        days = seconds // 86400
        return f"{days} 天前"
