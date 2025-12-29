"""Paper 测试数据工厂"""

import uuid
from datetime import datetime

import pytest

from evo_flywheel.db.models import Paper


@pytest.fixture
def paper_factory(test_db):
    """论文工厂函数"""

    def _create(**kwargs):
        defaults = {
            "title": "Test Paper",
            "abstract": "Test abstract",
            "doi": f"10.1234/test-{uuid.uuid4().hex[:8]}",  # 唯一 DOI
            "url": "https://example.com/paper",
            "publication_date": datetime.now(),
            "source": "test",
            "taxa": None,
            "evolutionary_scale": None,
            "research_method": None,
            "evolutionary_mechanism": None,
            "importance_score": None,
            "key_findings": None,
            "innovation_summary": None,
            "embedded": False,
        }
        defaults.update(kwargs)

        paper = Paper(**defaults)
        # 使用 authors_list property 设置
        paper.authors_list = defaults.get("authors", ["Author 1", "Author 2"])

        test_db.add(paper)
        test_db.commit()
        test_db.refresh(paper)
        return paper

    return _create
