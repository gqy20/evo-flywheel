"""Streamlit 主应用

Evo-Flywheel Web 界面入口
"""

import streamlit as st

from evo_flywheel.logging import get_logger
from evo_flywheel.web.pages import home, list, search

logger = get_logger(__name__)

# 页面配置
st.set_page_config(
    page_title="Evo-Flywheel - 进化生物学学术飞轮",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义 CSS
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main() -> None:
    """主应用入口"""
    # 侧边栏
    with st.sidebar:
        st.title("🧬 Evo-Flywheel")
        st.markdown("---")

        # 导航菜单
        pages = {
            "🏠 首页": home.render,
            "📚 文献列表": list.render,
            "🔍 语义搜索": search.render,
            "📄 论文详情": lambda: st.info("论文详情页开发中..."),
            "📊 报告生成": lambda: st.info("报告生成页开发中..."),
        }

        # 显示导航
        for page_name, _page_func in pages.items():
            if st.button(page_name, key=page_name, use_container_width=True):
                st.session_state.current_page = page_name

        st.markdown("---")
        st.caption("v0.1.4 - Phase 5 开发中")

    # 主内容区
    if "current_page" not in st.session_state:
        st.session_state.current_page = "🏠 首页"

    # 显示当前页面
    current_page_func = pages.get(st.session_state.current_page, home.render)
    current_page_func()


if __name__ == "__main__":
    main()
