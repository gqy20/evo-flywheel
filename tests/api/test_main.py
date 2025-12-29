"""FastAPI 主应用测试"""


def test_root_endpoint(client):
    """测试根端点返回正确信息"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Evo-Flywheel API"
    assert "docs" in data


def test_health_check(client):
    """测试健康检查端点"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_cors_middleware_configured(client):
    """测试 CORS 中间件已配置"""
    # 验证 CORS 中间件已添加到应用
    from evo_flywheel.api.main import app

    middleware_classes = [m.cls for m in app.user_middleware]
    from starlette.middleware.cors import CORSMiddleware

    assert CORSMiddleware in middleware_classes


def test_api_docs_accessible(client):
    """测试 API 文档可访问"""
    response = client.get("/api/v1/docs")
    # Swagger UI 返回 HTML
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
