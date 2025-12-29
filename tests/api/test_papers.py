"""论文端点测试"""


def test_list_papers_empty(client):
    """测试空论文列表"""
    response = client.get("/api/v1/papers")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["papers"] == []


def test_list_papers_with_data(client, paper_factory):
    """测试返回论文列表"""
    paper_factory(title="Paper 1", importance_score=80)
    paper_factory(title="Paper 2", importance_score=60)

    response = client.get("/api/v1/papers")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["papers"]) == 2
    # 验证返回的论文标题在预期列表中
    titles = {p["title"] for p in data["papers"]}
    assert "Paper 1" in titles
    assert "Paper 2" in titles


def test_list_papers_pagination(client, paper_factory):
    """测试分页功能"""
    # 创建 25 篇论文
    for i in range(25):
        paper_factory(title=f"Paper {i}")

    response = client.get("/api/v1/papers?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 25
    assert len(data["papers"]) == 10


def test_list_papers_filter_by_taxa(client, paper_factory):
    """测试按 taxa 筛选"""
    paper_factory(title="Mammal Study", taxa="Mammalia")
    paper_factory(title="Bird Study", taxa="Aves")
    paper_factory(title="Insect Study", taxa="Insecta")

    response = client.get("/api/v1/papers?taxa=Aves")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["papers"][0]["title"] == "Bird Study"


def test_list_papers_filter_by_min_score(client, paper_factory):
    """测试按最低分数筛选"""
    paper_factory(title="High Score", importance_score=90)
    paper_factory(title="Low Score", importance_score=40)

    response = client.get("/api/v1/papers?min_score=70")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["papers"][0]["title"] == "High Score"


def test_get_paper_detail(client, paper_factory):
    """测试获取论文详情"""
    paper = paper_factory(title="Test Paper", abstract="Test abstract")

    response = client.get(f"/api/v1/papers/{paper.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == paper.id
    assert data["title"] == "Test Paper"
    assert data["abstract"] == "Test abstract"


def test_get_paper_not_found(client):
    """测试论文不存在"""
    response = client.get("/api/v1/papers/99999")
    assert response.status_code == 404
    assert "不存在" in response.json()["detail"]
