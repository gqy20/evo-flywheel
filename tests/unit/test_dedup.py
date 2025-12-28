"""数据去重单元测试"""

from evo_flywheel.collectors.dedup import (
    extract_paper_key,
    is_duplicate_paper,
    remove_duplicate_papers,
)


class TestExtractPaperKey:
    """论文键提取测试"""

    def test_extract_paper_key_with_doi(self):
        """测试从 DOI 提取键"""
        # Arrange
        paper = {
            "doi": "10.1101/2024.12.28.123456",
            "title": "Some Paper",
        }

        # Act
        key = extract_paper_key(paper)

        # Assert
        assert key == "doi:10.1101/2024.12.28.123456"

    def test_extract_paper_key_with_title_only(self):
        """测试仅从标题提取键"""
        # Arrange
        paper = {
            "title": "Evolution of Gene Regulation in Drosophila",
        }

        # Act
        key = extract_paper_key(paper)

        # Assert
        assert key == "title:evolution of gene regulation in drosophila"

    def test_extract_paper_key_with_empty_title(self):
        """测试空标题"""
        # Arrange
        paper = {
            "title": "",
        }

        # Act
        key = extract_paper_key(paper)

        # Assert
        assert key is None

    def test_extract_paper_key_normalizes_title(self):
        """测试标题规范化"""
        # Arrange
        paper = {
            "title": "  Multiple   Spaces\tand\nCAPS  ",
        }

        # Act
        key = extract_paper_key(paper)

        # Assert
        assert key == "title:multiple spaces and caps"

    def test_extract_paper_key_with_unicode(self):
        """测试 Unicode 字符处理"""
        # Arrange
        paper = {
            "title": "Évolution çaractères ½",
        }

        # Act
        key = extract_paper_key(paper)

        # Assert
        assert key == "title:evolution caracteres 1/2"


class TestIsDuplicatePaper:
    """单个论文去重测试"""

    def test_is_duplicate_paper_by_doi(self):
        """测试通过 DOI 判断重复"""
        # Arrange
        paper = {"doi": "10.1101/2024.12.28.123456"}
        existing_keys = {"doi:10.1101/2024.12.28.123456"}

        # Act
        is_dup = is_duplicate_paper(paper, existing_keys)

        # Assert
        assert is_dup is True

    def test_is_duplicate_paper_by_title(self):
        """测试通过标题判断重复"""
        # Arrange
        paper = {"title": "Test Paper"}
        existing_keys = {"title:test paper"}

        # Act
        is_dup = is_duplicate_paper(paper, existing_keys)

        # Assert
        assert is_dup is True

    def test_is_duplicate_paper_not_duplicate(self):
        """测试非重复论文"""
        # Arrange
        paper = {"title": "New Paper", "doi": "10.1101/2024.12.28.999999"}
        existing_keys = {"title:old paper", "doi:10.1101/2024.12.28.111111"}

        # Act
        is_dup = is_duplicate_paper(paper, existing_keys)

        # Assert
        assert is_dup is False

    def test_is_duplicate_paper_empty_input(self):
        """测试空论文"""
        # Arrange
        paper = {}
        existing_keys = {"title:test paper"}

        # Act
        is_dup = is_duplicate_paper(paper, existing_keys)

        # Assert
        assert is_dup is True  # 无法提取键，视为重复（跳过）


class TestRemoveDuplicatePapers:
    """批量论文去重测试"""

    def test_remove_duplicate_papers_with_duplicates(self):
        """测试过滤重复论文"""
        # Arrange
        papers = [
            {"title": "Paper 1", "doi": "10.1101/2024.12.28.111111"},
            {"title": "Paper 2", "doi": "10.1101/2024.12.28.222222"},
            {"title": "Paper 1", "doi": "10.1101/2024.12.28.111111"},  # 重复
            {"title": "Paper 3", "doi": "10.1101/2024.12.28.333333"},
        ]

        # Act
        result = remove_duplicate_papers(papers)

        # Assert
        assert len(result) == 3
        titles = [p["title"] for p in result]
        assert "Paper 1" in titles
        assert "Paper 2" in titles
        assert "Paper 3" in titles

    def test_remove_duplicate_papers_empty_list(self):
        """测试空列表"""
        # Arrange
        papers = []

        # Act
        result = remove_duplicate_papers(papers)

        # Assert
        assert result == []

    def test_remove_duplicate_papers_all_unique(self):
        """测试全部唯一"""
        # Arrange
        papers = [
            {"title": "Paper A", "doi": "10.1101/2024.12.28.111111"},
            {"title": "Paper B", "doi": "10.1101/2024.12.28.222222"},
            {"title": "Paper C", "doi": "10.1101/2024.12.28.333333"},
        ]

        # Act
        result = remove_duplicate_papers(papers)

        # Assert
        assert len(result) == 3

    def test_remove_duplicate_papers_preserves_first_occurrence(self):
        """测试保留第一次出现"""
        # Arrange
        papers = [
            {"title": "Paper X", "source": "source_a"},
            {"title": "Paper Y", "source": "source_a"},
            {"title": "Paper X", "source": "source_b"},  # 重复，应跳过
            {"title": "Paper Z", "source": "source_a"},
        ]

        # Act
        result = remove_duplicate_papers(papers)

        # Assert
        assert len(result) == 3
        assert result[0]["source"] == "source_a"  # 保留第一个
        assert result[1]["source"] == "source_a"
        assert result[2]["source"] == "source_a"

    def test_remove_duplicate_papers_with_invalid_papers(self):
        """测试包含无效论文"""
        # Arrange
        papers = [
            {"title": "Valid Paper", "doi": "10.1101/2024.12.28.111111"},
            {},  # 无效（无标题无DOI）
            {"title": "Another Valid Paper", "doi": "10.1101/2024.12.28.222222"},
        ]

        # Act
        result = remove_duplicate_papers(papers)

        # Assert
        # 无效论文被视为重复（跳过）
        assert len(result) == 2
        titles = [p.get("title") for p in result]
        assert "Valid Paper" in titles
        assert "Another Valid Paper" in titles
