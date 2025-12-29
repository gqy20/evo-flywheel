"""用户反馈端点测试"""

from unittest.mock import patch


def test_create_feedback_success(client, paper_factory):
    """测试成功创建反馈"""
    paper = paper_factory(title="Test Paper")

    response = client.post(
        "/api/v1/feedback",
        json={
            "paper_id": paper.id,
            "rating": 5,
            "is_helpful": True,
            "comment": "Very helpful paper",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["paper_id"] == paper.id
    assert data["rating"] == 5
    assert data["is_helpful"] is True
    assert "id" in data


def test_create_feedback_invalid_rating(client, paper_factory):
    """测试无效评分（超出范围）"""
    paper = paper_factory(title="Test Paper")

    response = client.post(
        "/api/v1/feedback",
        json={
            "paper_id": paper.id,
            "rating": 6,  # 无效：超出 1-5 范围
            "is_helpful": True,
        },
    )
    assert response.status_code == 422  # Validation error


def test_create_feedback_missing_required_field(client, paper_factory):
    """测试缺少必填字段"""
    paper = paper_factory(title="Test Paper")

    response = client.post(
        "/api/v1/feedback",
        json={
            "paper_id": paper.id,
            # 缺少 rating
            "is_helpful": True,
        },
    )
    assert response.status_code == 422  # Validation error


def test_create_feedback_paper_not_found(client):
    """测试论文不存在"""
    response = client.post(
        "/api/v1/feedback",
        json={
            "paper_id": 99999,  # 不存在的论文
            "rating": 4,
        },
    )
    assert response.status_code == 404


@patch("evo_flywheel.api.v1.feedback.create_feedback")
def test_create_feedback_db_error(mock_create, client, paper_factory):
    """测试数据库错误处理"""
    paper = paper_factory(title="Test Paper")
    mock_create.side_effect = Exception("Database error")

    response = client.post(
        "/api/v1/feedback",
        json={
            "paper_id": paper.id,
            "rating": 3,
        },
    )
    assert response.status_code == 500
    assert "detail" in response.json()


def test_get_feedbacks_by_paper(client, paper_factory):
    """测试获取论文的所有反馈"""
    paper = paper_factory(title="Test Paper")

    # 创建多条反馈
    for rating in [5, 4, 3]:
        client.post(
            "/api/v1/feedback",
            json={"paper_id": paper.id, "rating": rating},
        )

    response = client.get(f"/api/v1/feedback?paper_id={paper.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["feedbacks"]) == 3
    assert all(f["paper_id"] == paper.id for f in data["feedbacks"])
