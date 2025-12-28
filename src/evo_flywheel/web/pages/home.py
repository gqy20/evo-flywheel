"""Streamlit 首页

展示今日报告、统计数据和推荐论文
"""

from datetime import datetime

import streamlit as st
from sqlalchemy import create_engine

from evo_flywheel.config import get_settings
from evo_flywheel.logging import get_logger

logger = get_logger(__name__)


def get_db_connection():
    """获取数据库连接"""
    settings = get_settings()
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}
        if settings.database_url.startswith("sqlite")
        else {},
    )
    return engine.connect()


def render_stats_section() -> None:
    """渲染统计数据区域"""
    st.subheader("📊 统计数据")

    conn = None
    try:
        conn = get_db_connection()

        # 获取论文总数
        total_papers = conn.execute("SELECT COUNT(*) FROM papers").scalar() or 0

        # 获取最近7天新增
        recent_papers = (
            conn.execute(
                "SELECT COUNT(*) FROM papers WHERE created_at >= datetime('now', '-7 days')"
            ).scalar()
            or 0
        )

        # 获取高分论文数量
        high_score_papers = (
            conn.execute("SELECT COUNT(*) FROM papers WHERE importance_score >= 80").scalar() or 0
        )

        # 显示统计卡片
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="论文总数", value=total_papers)
        with col2:
            st.metric(label="本周新增", value=recent_papers, delta="7 天内")
        with col3:
            st.metric(label="高分论文", value=high_score_papers, help="重要性评分 ≥ 80")

    except Exception as e:
        logger.error(f"统计数据获取失败: {e}")
        st.error("统计数据加载失败")
    finally:
        if conn:
            conn.close()


def render_recommendations_section() -> None:
    """渲染推荐论文区域"""
    st.subheader("⭐ 重点推荐")

    conn = None
    try:
        conn = get_db_connection()

        # 获取高分论文
        papers = conn.execute(
            """
            SELECT id, title, abstract, authors, journal, publication_date, importance_score
            FROM papers
            WHERE importance_score >= 80
            ORDER BY importance_score DESC, publication_date DESC
            LIMIT 5
            """
        ).fetchall()

        if not papers:
            st.info("暂无推荐论文")
            return

        for i, paper in enumerate(papers, 1):
            paper_id, title, abstract, authors, journal, pub_date, score = paper

            with st.expander(f"{i}. {title} (评分: {score})", expanded=i == 1):
                st.markdown(f"**作者**: {authors or '未知'}")
                st.markdown(f"**期刊**: {journal or '未知'}")
                st.markdown(f"**发表日期**: {pub_date or '未知'}")
                st.markdown(f"**重要性评分**: :star: {score}/100")

                if abstract:
                    with st.toggle("显示摘要"):
                        st.markdown(f"> {abstract}")

    except Exception as e:
        logger.error(f"推荐论文获取失败: {e}")
        st.error("推荐论文加载失败")
    finally:
        if conn:
            conn.close()


def render_daily_report_section() -> None:
    """渲染今日报告区域"""
    st.subheader("📅 今日报告")

    today = datetime.now().strftime("%Y-%m-%d")
    conn = None

    try:
        conn = get_db_connection()

        # 尝试获取今日报告
        report = conn.execute(
            "SELECT summary, top_papers FROM daily_reports WHERE date = ?", (today,)
        ).fetchone()

        if report:
            summary, top_papers = report
            st.success(summary)

            if top_papers:
                st.markdown("**今日亮点**:")
                # top_papers 是 JSON 字符串，需要解析
                import json

                try:
                    papers_list = json.loads(top_papers)
                    for paper in papers_list:
                        st.markdown(f"- {paper}")
                except json.JSONDecodeError:
                    st.caption("(亮点数据格式错误)")
        else:
            st.info(f"今日 ({today}) 报告尚未生成")
            st.caption("报告将在每日自动采集后生成")

    except Exception as e:
        logger.error(f"今日报告获取失败: {e}")
        st.warning("今日报告加载失败")
    finally:
        if conn:
            conn.close()


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

    # 页脚
    st.markdown("---")
    st.caption("💡 提示: 使用左侧菜单导航到其他页面")
