"""Pytest 配置和 Fixtures"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# 添加 src 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def temp_db_path():
    """临时数据库路径"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        yield f.name
        os.unlink(f.name)


@pytest.fixture
def temp_chroma_dir():
    """临时 Chroma 目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_paper_data():
    """示例论文数据"""
    return {
        "title": "Rapid adaptation to climate change in Drosophila",
        "authors": ["Smith, J.", "Doe, A.", "Johnson, B."],
        "abstract": "This study investigates rapid adaptation to climate change in Drosophila populations...",
        "doi": "10.1101/2024.12.28.123456",
        "url": "https://www.biorxiv.org/content/10.1101/2024.12.28.123456",
        "publication_date": "2024-12-28",
        "journal": "bioRxiv",
        "source": "biorxiv_api",
    }


@pytest.fixture
def sample_analysis_result():
    """示例分析结果"""
    return {
        "taxa": "Drosophila",
        "evolutionary_scale": "Population",
        "research_method": "Experimental Evolution",
        "key_findings": [
            "Rapid adaptation observed within 10 generations",
            "Genetic basis of adaptation identified",
            "Climate change drives selection pressure",
        ],
        "evolutionary_mechanism": "Natural Selection",
        "importance_score": 85,
        "innovation_summary": "First study to document rapid climate adaptation in Drosophila",
    }
