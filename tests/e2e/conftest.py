"""E2E 测试配置和 fixtures"""

import subprocess
from collections.abc import Generator

import pytest
from playwright.sync_api import Browser, Page


@pytest.fixture(scope="session")
def streamlit_server() -> Generator[subprocess.Popen]:
    """启动 Streamlit 服务器

    Yields:
        subprocess.Popen: Streamlit 进程
    """
    # 启动 Streamlit
    proc = subprocess.Popen(
        [
            "uv",
            "run",
            "streamlit",
            "run",
            "src/evo_flywheel/web/app.py",
            "--server.headless",
            "true",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # 等待服务器启动
    import time

    time.sleep(5)

    yield proc

    # 清理
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture(scope="function")
def streamlit_page(browser: Browser, streamlit_server: subprocess.Popen) -> Page:
    """创建 Streamlit 页面

    Args:
        browser: Playwright 浏览器实例
        streamlit_server: Streamlit 服务器进程

    Returns:
        Page: Playwright 页面实例
    """
    page = browser.new_page()
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")
    return page
