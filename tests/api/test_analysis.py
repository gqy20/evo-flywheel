"""分析调度端点测试"""

import pytest


@pytest.mark.skip(reason="需要实际的分析模块")
def test_trigger_analysis(client):
    """测试触发论文分析"""
    response = client.post("/api/v1/analysis/trigger")
    assert response.status_code == 200
    data = response.json()
    assert "analyzed" in data


def test_analysis_endpoint_exists():
    """测试分析端点存在"""
    from evo_flywheel.api.v1 import analysis

    # 验证模块存在
    assert hasattr(analysis, "router")


def test_trigger_analysis_endpoint_exists():
    """测试 /analysis/trigger 端点存在"""
    from evo_flywheel.api.v1 import analysis

    # 验证端点存在
    routes = [r.path for r in analysis.router.routes]
    # 路由路径不包含前缀
    assert "/trigger" in routes
    assert "/status" in routes
