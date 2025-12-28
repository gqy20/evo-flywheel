"""Streamlit 语义搜索页

支持自然语言查询和相似论文推荐
"""

import streamlit as st

from evo_flywheel.logging import get_logger
from evo_flywheel.vector import search as vector_search

logger = get_logger(__name__)

# 默认搜索结果数量
DEFAULT_N_RESULTS = 10


def render_search_input() -> tuple[str, int, dict]:
    """渲染搜索输入区域

    Returns:
        tuple: (查询文本, 结果数量, 筛选条件)
    """
    st.subheader("🔍 语义搜索")

    # 自然语言查询输入
    query = st.text_input(
        "输入搜索查询",
        placeholder="例如: evolutionary genetics in Drosophila...",
        key="search_query",
        help="使用自然语言描述您想搜索的内容",
    )

    # 精细化筛选选项
    with st.expander("搜索选项", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            # 结果数量
            n_results = st.slider(
                "返回结果数量",
                min_value=5,
                max_value=50,
                value=DEFAULT_N_RESULTS,
                step=5,
                key="search_n_results",
            )

            # 最低评分
            min_score = st.slider(
                "最低重要性评分",
                min_value=0,
                max_value=100,
                value=0,
                step=5,
                key="search_min_score",
            )

        with col2:
            # 物种筛选
            taxa = st.text_input(
                "物种筛选",
                placeholder="如: Drosophila, Homo sapiens",
                key="search_taxa",
            )

            # 期刊筛选
            journal = st.text_input(
                "期刊筛选",
                placeholder="如: Nature, Science",
                key="search_journal",
            )

    # 构建筛选条件
    filters = {}
    if min_score > 0:
        filters["min_score"] = min_score
    if taxa:
        filters["taxa"] = taxa
    if journal:
        filters["journal"] = journal

    return query, n_results, filters


def render_search_results(query: str, n_results: int, filters: dict) -> bool:
    """渲染搜索结果

    Args:
        query: 查询文本
        n_results: 结果数量
        filters: 筛选条件

    Returns:
        bool: 是否执行了搜索
    """
    if not query or not query.strip():
        st.info("请输入搜索查询")
        return False

    try:
        # 执行语义搜索
        results = vector_search.semantic_search_by_text(
            query_text=query,
            n_results=n_results,
            where=filters if filters else None,
        )

        if results["total"] == 0:
            st.info("没有找到相关结果")
            return True

        # 显示查询信息
        st.caption(f"查询: {query} | 找到 {results['total']} 条结果")

        # 显示结果
        for i, result in enumerate(results["results"], 1):
            distance = result.get("distance", 1.0)
            similarity = max(0, (1 - distance) * 100)  # 转换为相似度百分比

            with st.container():
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"### {i}. {result.get('title', '无标题')}")
                    st.caption(
                        f"📄 {result.get('journal', '未知')} | "
                        f"🧬 {result.get('taxa', '未知')} | "
                        f"⭐ 评分: {result.get('importance_score', 0)}/100"
                    )

                    if result.get("authors"):
                        st.caption(f"👥 {result['authors']}")

                    if result.get("abstract"):
                        with st.expander("显示摘要"):
                            st.markdown(f"> {result['abstract']}")

                with col2:
                    # 显示相似度
                    st.metric(
                        "",
                        value=f"{similarity:.1f}%",
                        label="相似度",
                        help=f"距离: {distance:.4f} (越小越相似)",
                    )

                st.markdown("---")

        return True

    except Exception as e:
        logger.error(f"搜索失败: {e}")
        st.error(f"搜索失败: {str(e)}")
        return False


def render_similar_papers(paper_id: int | None = None):
    """渲染相似论文推荐

    Args:
        paper_id: 论文 ID (可选)
    """
    if paper_id is None:
        return

    st.subheader("📎 相似论文推荐")

    try:
        # 获取相似论文
        results = vector_search.semantic_search_similar_paper(
            paper_id=paper_id,
            n_results=5,
        )

        if results["total"] == 0:
            st.info("没有找到相似论文")
            return

        st.caption(f"基于论文 ID: {paper_id} 找到 {results['total']} 篇相似论文")

        for i, result in enumerate(results["results"], 1):
            with st.container():
                st.markdown(f"**{i}. {result.get('title', '无标题')}**")
                st.caption(
                    f"📄 {result.get('journal', '未知')} | "
                    f"相似度: {max(0, (1 - result.get('distance', 1)) * 100):.1f}%"
                )

                if result.get("abstract"):
                    with st.expander("显示摘要"):
                        st.text(result["abstract"])

                st.markdown("---")

    except Exception as e:
        logger.error(f"获取相似论文失败: {e}")
        st.warning("获取相似论文失败")


def render() -> None:
    """渲染语义搜索页"""
    st.title("🔍 语义搜索")
    st.markdown("---")

    # 初始化 session state
    if "search_results" not in st.session_state:
        st.session_state.search_results = None

    # 搜索输入区域
    query, n_results, filters = render_search_input()

    # 搜索按钮
    if (
        st.button("🔍 搜索", key="search_button", type="primary", use_container_width=True)
        and query
        and query.strip()
    ):
        st.session_state.search_query = query
        st.session_state.search_n_results = n_results
        st.session_state.search_filters = filters
        st.rerun()

    # 显示搜索结果
    if hasattr(st.session_state, "search_query"):
        st.markdown("---")
        render_search_results(
            query=st.session_state.search_query,
            n_results=st.session_state.search_n_results,
            filters=st.session_state.search_filters,
        )

        # 显示相似论文选项
        st.markdown("---")
        st.subheader("📎 查找相似论文")

        paper_id_input = st.text_input(
            "输入论文 ID",
            placeholder="例如: 123",
            key="similar_paper_id",
        )

        if st.button("查找相似论文", key="find_similar_button"):
            if paper_id_input and paper_id_input.isdigit():
                render_similar_papers(paper_id=int(paper_id_input))
            else:
                st.warning("请输入有效的论文 ID")

    # 使用提示
    with st.expander("💡 使用提示"):
        st.markdown("""
        ### 语义搜索技巧

        - 使用自然语言描述您想搜索的内容
        - 例如: "evolutionary adaptations in high-altitude environments"
        - 例如: "gene flow between populations"
        - 例如: "phylogenetic analysis methods"

        ### 相似论文推荐

        - 输入论文 ID 可以找到与该论文最相似的其他研究
        - 相似度基于论文摘要的语义向量计算
        - 原论文不会出现在相似结果中
        """)
