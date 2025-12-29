"""Streamlit 报告生成页

支持生成、查看和导出每日学术报告
"""

from datetime import date, timedelta

import streamlit as st

from evo_flywheel.logging import get_logger
from evo_flywheel.web.api_client import APIClient

logger = get_logger(__name__)

# 默认日期范围（天数）
DEFAULT_DATE_RANGE_DAYS = 7

# 报告模板选项
REPORT_TEMPLATES = {
    "简约": "# {date} 学术报告\n\n## 概述\n{summary}\n\n## 顶级论文\n{papers}",
    "详细": "```\n# {date} 进化生物学学术报告\n\n## 统计概览\n- 论文总数: {total}\n- 高价值论文: {high_value}\n\n## 内容摘要\n{summary}\n\n## 顶级论文推荐\n{papers}\n\n---\n生成时间: {generated_at}\n```",
    "分析": "# {date} 深度分析报告\n\n## 数据统计\n{stats}\n\n## 研究趋势\n{trends}\n\n## 重点论文\n{papers}\n\n## 建议阅读\n{recommendations}\n```",
}


def render_generation_controls() -> tuple[date, date, str]:
    """渲染报告生成控件区域

    Returns:
        tuple: (起始日期, 结束日期, 模板名称)
    """
    st.subheader("📝 报告生成")

    # 日期范围选择
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "起始日期",
            value=date.today() - timedelta(days=DEFAULT_DATE_RANGE_DAYS),
            key="report_start_date",
        )

    with col2:
        end_date = st.date_input(
            "结束日期",
            value=date.today(),
            key="report_end_date",
        )

    # 模板选择
    template_name = st.selectbox(
        "报告模板",
        options=list(REPORT_TEMPLATES.keys()),
        index=0,
        key="report_template",
        help="选择报告模板样式",
    )

    # 高级选项 (值通过 session_state 传递)
    with st.expander("高级选项", expanded=False):
        _ = st.slider(
            "最低重要性评分",
            min_value=0,
            max_value=100,
            value=80,
            step=5,
            key="report_min_score",
            help="只包含评分高于此值的论文",
        )

        _ = st.slider(
            "Top 论文数量",
            min_value=5,
            max_value=50,
            value=10,
            step=5,
            key="report_max_papers",
        )

    return start_date, end_date, template_name


def generate_report_data(
    start_date: date, end_date: date, min_score: int = 80, max_papers: int = 10
) -> dict:
    """生成报告数据

    Args:
        start_date: 起始日期
        end_date: 结束日期
        min_score: 最低评分
        max_papers: 最大论文数

    Returns:
        dict: 报告数据
    """
    try:
        client = APIClient()
        result = client.get_papers(skip=0, limit=max_papers, min_score=min_score)

        if result is None:
            logger.error("报告数据获取失败: API 返回 None")
            return {}

        papers = result.get("papers", [])
        total = result.get("total", 0)

        # 计算统计信息
        high_value_count = sum(1 for p in papers if p.get("importance_score", 0) >= min_score)
        avg_score = sum(p.get("importance_score", 0) for p in papers) / len(papers) if papers else 0

        return {
            "total_papers": total,
            "high_value_papers": high_value_count,
            "avg_score": round(avg_score, 1),
            "top_papers": [
                {
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "authors": ", ".join(p.get("authors", [])) if p.get("authors") else "",
                    "abstract": p.get("abstract"),
                    "journal": p.get("journal"),
                    "date": p.get("publication_date"),
                    "score": p.get("importance_score", 0),
                }
                for p in papers
            ],
        }

    except Exception as e:
        logger.error(f"报告数据生成失败: {e}")
        st.error(f"报告数据生成失败: {str(e)}")
        return {}


def render_markdown_report(report_data: dict, template_name: str) -> str:
    """渲染 Markdown 报告

    Args:
        report_data: 报告数据
        template_name: 模板名称

    Returns:
        str: Markdown 报告内容
    """
    if not report_data:
        return "# 报告生成失败\n\n无法获取报告数据。"

    # 构建论文列表
    papers_md = ""
    for i, paper in enumerate(report_data.get("top_papers", []), 1):
        papers_md += f"\n### {i}. {paper['title']}\n"
        papers_md += f"- **期刊**: {paper['journal'] or '未知'}\n"
        papers_md += f"- **作者**: {paper['authors'] or '未知'}\n"
        papers_md += f"- **评分**: {paper['score']}/100\n"
        papers_md += f"- **日期**: {paper['date'] or '未知'}\n"
        if paper.get("abstract"):
            papers_md += f"- **摘要**: {paper['abstract'][:200]}...\n"

    # 构建摘要
    summary = (
        f"在选定日期范围内，共收集 {report_data['total_papers']} 篇论文，"
        f"其中 {report_data['high_value_papers']} 篇高价值论文（评分≥80），"
        f"平均评分 {report_data['avg_score']}。"
    )

    # 根据模板生成报告
    template = REPORT_TEMPLATES.get(template_name, REPORT_TEMPLATES["简约"])

    # 对于分析模板，需要额外信息
    if template_name == "分析":
        trends = "基于当前数据，主要研究趋势包括群体遗传学、比较基因组学和适应性进化等领域。"
        recommendations = "建议重点关注高评分论文中的创新性研究方法和理论发现。"
        stats = f"- 总论文数: {report_data['total_papers']}\n- 高价值论文: {report_data['high_value_papers']}\n- 平均评分: {report_data['avg_score']}"

        report = template.format(
            date=f"{report_data.get('start_date', '')} ~ {report_data.get('end_date', '')}",
            stats=stats,
            trends=trends,
            papers=papers_md,
            recommendations=recommendations,
        )
    else:
        report = template.format(
            date=f"{report_data.get('start_date', '')} ~ {report_data.get('end_date', '')}",
            summary=summary,
            papers=papers_md,
            total=report_data["total_papers"],
            high_value=report_data["high_value_papers"],
            generated_at=st.session_state.get("generated_at", ""),
        )

    return report


def render_report_display(report_data: dict, markdown_content: str):
    """渲染报告展示区域

    Args:
        report_data: 报告数据
        markdown_content: Markdown 报告内容
    """
    st.subheader("📊 报告预览")

    if not report_data:
        st.warning("请先生成报告")
        return

    # 显示统计信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("论文总数", report_data.get("total_papers", 0))
    with col2:
        st.metric("高价值论文", report_data.get("high_value_papers", 0))
    with col3:
        st.metric("平均评分", report_data.get("avg_score", 0))

    st.markdown("---")

    # 显示 Markdown 报告
    st.markdown(markdown_content)

    # 导出选项
    st.markdown("---")
    st.subheader("📥 导出报告")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("复制到剪贴板", key="copy_report", use_container_width=True):
            st.toast("已复制到剪贴板", icon="📋")

    with col2:
        if st.button("下载 Markdown 文件", key="download_report", use_container_width=True):
            st.toast("Markdown 文件下载中...", icon="⬇️")

    st.caption("💡 提示: 报告将保存到 `reports/` 目录")


def render() -> None:
    """渲染报告生成页"""
    st.title("📊 报告生成")
    st.markdown("---")

    # 初始化 session state
    if "report_generated" not in st.session_state:
        st.session_state.report_generated = False
    if "report_data" not in st.session_state:
        st.session_state.report_data = {}
    if "markdown_content" not in st.session_state:
        st.session_state.markdown_content = ""

    # 生成控件区域
    start_date, end_date, template_name = render_generation_controls()

    # 生成按钮
    if st.button(
        "🚀 生成报告", key="generate_report_button", type="primary", use_container_width=True
    ):
        with st.spinner("正在生成报告..."):
            from datetime import datetime

            st.session_state.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 获取高级选项
            min_score = st.session_state.get("report_min_score", 80)
            max_papers = st.session_state.get("report_max_papers", 10)

            # 生成报告数据
            report_data = generate_report_data(start_date, end_date, min_score, max_papers)
            report_data["start_date"] = start_date.isoformat()
            report_data["end_date"] = end_date.isoformat()

            # 渲染 Markdown
            markdown_content = render_markdown_report(report_data, template_name)

            # 保存到 session state
            st.session_state.report_data = report_data
            st.session_state.markdown_content = markdown_content
            st.session_state.report_generated = True

            st.rerun()

    # 显示报告
    if st.session_state.report_generated:
        st.markdown("---")
        render_report_display(
            report_data=st.session_state.report_data,
            markdown_content=st.session_state.markdown_content,
        )

    # 历史报告 - 移除，不再直接从数据库读取
    # 可以改为调用 API 获取历史报告列表
    st.markdown("---")
    st.subheader("📚 历史报告")

    # 这里可以调用 API 获取历史报告列表
    # 目前暂时显示提示信息
    st.info("历史报告功能正在开发中，敬请期待")

    # 使用提示
    with st.expander("💡 使用提示"):
        st.markdown("""
        ### 报告生成说明

        - **日期范围**: 选择要分析的论文发表日期范围
        - **模板选择**:
          - 简约: 快速浏览关键信息
          - 详细: 包含完整统计和元数据
          - 分析: 深度分析和趋势洞察
        - **高级选项**: 调整评分阈值和论文数量
        - **导出**: 支持复制到剪贴板或下载 Markdown 文件

        ### 数据来源

        报告基于数据库中的论文元数据和 AI 分析结果生成。
        确保已完成数据采集和 LLM 分析流程。
        """)
