"""Streamlit 文献列表页

展示所有论文，支持筛选、搜索、分页
"""

from typing import Any

import streamlit as st
from sqlalchemy import create_engine, text

from evo_flywheel.config import get_settings
from evo_flywheel.logging import get_logger

logger = get_logger(__name__)

# 每页显示数量
PAGE_SIZE_OPTIONS = [10, 20, 50, 100]
DEFAULT_PAGE_SIZE = 20


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


def render_filters_section() -> dict:
    """渲染筛选区域

    Returns:
        dict: 筛选条件
    """
    st.subheader("🔍 筛选条件")

    with st.expander("展开筛选选项", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            # 物种筛选
            taxa = st.text_input(
                "物种 (如: Drosophila, Homo sapiens)",
                help="输入物种名称进行筛选",
                key="filter_taxa",
            )

        with col2:
            # 期刊筛选
            journal = st.text_input(
                "期刊 (如: Nature, Science)",
                help="输入期刊名称进行筛选",
                key="filter_journal",
            )

        with col3:
            # 最低评分
            min_score = st.slider(
                "最低重要性评分",
                min_value=0,
                max_value=100,
                value=0,
                step=5,
                help="只显示评分高于此值的论文",
                key="filter_min_score",
            )

        col4, col5 = st.columns(2)

        with col4:
            # 起始日期
            date_from = st.date_input(
                "起始日期",
                value=None,
                key="filter_date_from",
            )

        with col5:
            # 结束日期
            date_to = st.date_input(
                "结束日期",
                value=None,
                key="filter_date_to",
            )

    # 关键词搜索
    keyword = st.text_input(
        "🔎 关键词搜索",
        placeholder="搜索标题或摘要中的关键词...",
        key="search_keyword",
    )

    return {
        "taxa": taxa if taxa else None,
        "journal": journal if journal else None,
        "min_score": min_score if min_score > 0 else None,
        "date_from": date_from.strftime("%Y-%m-%d") if date_from else None,
        "date_to": date_to.strftime("%Y-%m-%d") if date_to else None,
        "keyword": keyword if keyword else None,
    }


def render_paper_list(filters: dict, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> int:
    """渲染论文列表

    Args:
        filters: 筛选条件
        page: 当前页码
        page_size: 每页数量

    Returns:
        int: 总记录数
    """
    conn = None
    try:
        conn = get_db_connection()

        # 构建 SQL 查询
        where_clauses = []
        params: list[Any] = []

        # 应用筛选条件
        if filters.get("taxa"):
            where_clauses.append("taxa LIKE ?")
            params.append(f"%{filters['taxa']}%")

        if filters.get("journal"):
            where_clauses.append("journal LIKE ?")
            params.append(f"%{filters['journal']}%")

        if filters.get("min_score"):
            where_clauses.append("importance_score >= ?")
            params.append(filters["min_score"])

        if filters.get("date_from"):
            where_clauses.append("publication_date >= ?")
            params.append(filters["date_from"])

        if filters.get("date_to"):
            where_clauses.append("publication_date <= ?")
            params.append(filters["date_to"])

        if filters.get("keyword"):
            where_clauses.append("(title LIKE ? OR abstract LIKE ?)")
            params.extend([f"%{filters['keyword']}%", f"%{filters['keyword']}%"])

        # WHERE 子句
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # 获取总数 (SQL injection prevented by parameterized queries)
        count_query = text(f"SELECT COUNT(*) FROM papers WHERE {where_sql}")  # nosec B608
        total_count = conn.execute(count_query, params).scalar() or 0

        # 分页查询 (SQL injection prevented by parameterized queries)
        offset = (page - 1) * page_size
        data_query = text(f"""
            SELECT id, title, authors, abstract, journal, publication_date, importance_score, taxa
            FROM papers
            WHERE {where_sql}
            ORDER BY importance_score DESC, publication_date DESC
            LIMIT ? OFFSET ?
        """)  # nosec B608
        params.extend([page_size, offset])

        papers = conn.execute(data_query, params).fetchall()

        # 显示论文列表
        if not papers:
            st.info("没有找到符合条件的论文")
            return total_count

        for paper in papers:
            paper_id, title, authors, abstract, journal, pub_date, score, taxa = paper

            with st.container():
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"### {title}")
                    st.caption(
                        f"📄 {journal or '未知期刊'} | 📅 {pub_date or '未知日期'} | 🧬 {taxa or '未知物种'}"
                    )
                    if authors:
                        st.caption(f"👥 {authors}")

                    if abstract:
                        with st.expander("显示摘要"):
                            st.markdown(f"> {abstract}")

                with col2:
                    st.metric("", value=score or 0, label="评分", help="重要性评分")

                st.markdown("---")

        return total_count

    except Exception as e:
        logger.error(f"论文列表获取失败: {e}")
        st.error("论文列表加载失败")
        return 0
    finally:
        if conn:
            conn.close()


def render_pagination(total_count: int, page: int, page_size: int) -> tuple[int, int]:
    """渲染分页控件

    Args:
        total_count: 总记录数
        page: 当前页码
        page_size: 每页数量

    Returns:
        tuple: (新页码, 新页大小)
    """
    total_pages = max(1, (total_count + page_size - 1) // page_size)

    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

    with col1:
        if st.button("⬅️ 上一页", disabled=page <= 1, key="pagination_prev"):
            st.session_state.list_page = max(1, page - 1)
            st.rerun()

    with col2:
        if st.button("下一页 ➡️", disabled=page >= total_pages, key="pagination_next"):
            st.session_state.list_page = page + 1
            st.rerun()

    with col3:
        new_page = st.slider(
            "页码",
            min_value=1,
            max_value=total_pages,
            value=page,
            key="pagination_page",
        )

    with col4:
        page_size = st.selectbox(
            "每页数量",
            options=PAGE_SIZE_OPTIONS,
            index=PAGE_SIZE_OPTIONS.index(page_size) if page_size in PAGE_SIZE_OPTIONS else 0,
            key="pagination_size",
        )

    with col5:
        st.caption(f"共 {total_count} 条 / {total_pages} 页")

    return new_page, page_size


def render_export_section(total_count: int):
    """渲染导出区域

    Args:
        total_count: 当前结果数量
    """
    if total_count == 0:
        return

    st.subheader("📥 导出数据")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("导出 CSV (当前筛选结果)", key="export_csv"):
            st.info("CSV 导出功能开发中...")

    with col2:
        if st.button("导出 Excel (当前筛选结果)", key="export_excel"):
            st.info("Excel 导出功能开发中...")

    st.caption("💡 提示: 导出将包含当前筛选条件下的所有结果")


def render() -> None:
    """渲染文献列表页"""
    st.title("📚 文献列表")
    st.markdown("---")

    # 初始化 session state
    if "list_page" not in st.session_state:
        st.session_state.list_page = 1
    if "list_page_size" not in st.session_state:
        st.session_state.list_page_size = DEFAULT_PAGE_SIZE

    # 筛选区域
    filters = render_filters_section()

    # 论文列表
    st.markdown("---")
    total_count = render_paper_list(
        filters=filters,
        page=st.session_state.list_page,
        page_size=st.session_state.list_page_size,
    )

    # 分页
    if total_count > 0:
        st.markdown("---")
        new_page, new_page_size = render_pagination(
            total_count=total_count,
            page=st.session_state.list_page,
            page_size=st.session_state.list_page_size,
        )

        # 更新 session state
        if new_page != st.session_state.list_page:
            st.session_state.list_page = new_page
            st.rerun()
        if new_page_size != st.session_state.list_page_size:
            st.session_state.list_page_size = new_page_size
            st.session_state.list_page = 1  # 重置到第一页
            st.rerun()

    # 导出区域
    st.markdown("---")
    render_export_section(total_count)
