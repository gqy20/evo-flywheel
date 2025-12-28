"""AI 分析调度器单元测试"""

from unittest import mock


class TestGetUnanalyzedPapers:
    """获取未分析论文测试"""

    def test_get_unanalyzed_papers_returns_papers_without_importance_score(
        self, monkeypatch, tmp_path
    ):
        """测试返回没有 importance_score 的论文"""
        # Arrange - 模拟数据库查询
        mock_db_result = [
            (
                1,
                "Paper 1",
                "Abstract 1",
                "10.1234/test.001",
                "https://example.com/1",
                "Author 1;Author 2",
            ),
            (
                2,
                "Paper 2",
                "Abstract 2",
                "10.1234/test.002",
                "https://example.com/2",
                "Author 3",
            ),
        ]

        mock_engine = mock.Mock()
        mock_session = mock.Mock()
        mock_result = mock.Mock()
        mock_result.__iter__ = lambda self: iter(mock_db_result)
        mock_session.execute.return_value = mock_result
        mock_session.__enter__ = mock.Mock(return_value=mock_session)
        mock_session.__exit__ = mock.Mock(return_value=False)

        def mock_session_factory(*args, **kwargs):
            return mock_session

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.create_engine",
            lambda x: mock_engine,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.Session",
            mock_session_factory,
        )

        # Act
        from evo_flywheel.scheduler.analysis import _get_unanalyzed_papers

        papers = _get_unanalyzed_papers(max_papers=100)

        # Assert
        assert len(papers) == 2
        assert papers[0]["title"] == "Paper 1"
        assert papers[0]["abstract"] == "Abstract 1"
        assert papers[0]["doi"] == "10.1234/test.001"
        assert papers[0]["authors"] == ["Author 1", "Author 2"]
        assert papers[1]["title"] == "Paper 2"

    def test_get_unanalyzed_papers_with_max_papers_limit(self, monkeypatch):
        """测试 max_papers 参数限制返回数量"""
        # Arrange
        mock_db_result = [
            (i, f"Paper {i}", f"Abstract {i}", f"10.1234/test.{i:03d}", "", "") for i in range(100)
        ]

        mock_result = mock.Mock()
        mock_result.__iter__ = lambda self: iter(mock_db_result)
        mock_session = mock.Mock()
        mock_session.execute.return_value = mock_result
        mock_session.__enter__ = mock.Mock(return_value=mock_session)
        mock_session.__exit__ = mock.Mock(return_value=False)

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.Session",
            lambda *args, **kwargs: mock_session,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.create_engine",
            lambda x: mock.Mock(),
        )

        # Act
        from evo_flywheel.scheduler.analysis import _get_unanalyzed_papers

        papers = _get_unanalyzed_papers(max_papers=10)

        # Assert
        assert len(papers) == 10

    def test_get_unanalyzed_papers_returns_empty_list_when_no_papers(self, monkeypatch):
        """测试数据库中没有未分析论文时返回空列表"""
        # Arrange
        mock_result = mock.Mock()
        mock_result.__iter__ = lambda self: iter([])
        mock_session = mock.Mock()
        mock_session.execute.return_value = mock_result
        mock_session.__enter__ = mock.Mock(return_value=mock_session)
        mock_session.__exit__ = mock.Mock(return_value=False)

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.Session",
            lambda *args, **kwargs: mock_session,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.create_engine",
            lambda x: mock.Mock(),
        )

        # Act
        from evo_flywheel.scheduler.analysis import _get_unanalyzed_papers

        papers = _get_unanalyzed_papers()

        # Assert
        assert papers == []


class TestUpdateAnalysisToDb:
    """保存分析结果到数据库测试"""

    def test_update_analysis_to_db_updates_papers_by_doi(self, monkeypatch, tmp_path):
        """测试通过 DOI 更新论文分析结果"""
        # Arrange
        analyzed_papers = [
            {
                "doi": "10.1234/test.001",
                "title": "Paper 1",
                "taxa": "Drosophila",
                "evolutionary_scale": "种群",
                "research_method": "实验",
                "key_findings": ["Finding 1", "Finding 2"],
                "evolutionary_mechanism": "自然选择",
                "importance_score": 85,
                "innovation_summary": "Methodological innovation",
            },
            {
                "doi": "10.1234/test.002",
                "title": "Paper 2",
                "taxa": "E. coli",
                "evolutionary_scale": "分子",
                "research_method": "比较",
                "key_findings": ["Finding 3"],
                "evolutionary_mechanism": "突变",
                "importance_score": 70,
                "innovation_summary": "New discovery",
            },
        ]

        mock_papers = []
        dois = ["10.1234/test.001", "10.1234/test.002"]
        for i, _doi in enumerate(dois):
            mock_paper = mock.Mock()
            mock_paper.id = i + 1
            mock_paper.doi = dois[i]
            mock_papers.append(mock_paper)

        def mock_get_by_doi(session, doi):
            for p in mock_papers:
                if p.doi == doi:
                    return p
            return None

        call_log = []

        def mock_update_paper(session, paper_id, **kwargs):
            call_log.append({"id": paper_id, "fields": kwargs})
            return mock_papers[paper_id - 1]

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.crud.get_paper_by_doi",
            mock_get_by_doi,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.crud.update_paper",
            mock_update_paper,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.create_engine",
            lambda x: mock.Mock(),
        )

        mock_session = mock.Mock()
        mock_session.__enter__ = mock.Mock(return_value=mock_session)
        mock_session.commit = mock.Mock()
        mock_session.__exit__ = mock.Mock(return_value=False)

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.Session",
            lambda *args, **kwargs: mock_session,
        )

        # Act
        from evo_flywheel.scheduler.analysis import _update_analysis_to_db

        count = _update_analysis_to_db(analyzed_papers)

        # Assert
        assert count == 2
        assert len(call_log) == 2
        assert call_log[0]["fields"]["taxa"] == "Drosophila"
        assert call_log[0]["fields"]["importance_score"] == 85
        assert call_log[1]["fields"]["taxa"] == "E. coli"

    def test_update_analysis_to_db_skips_unknown_papers(self, monkeypatch):
        """测试跳过数据库中不存在的论文"""
        # Arrange
        analyzed_papers = [
            {
                "doi": "10.1234/unknown.001",
                "title": "Unknown Paper",
                "taxa": "Unknown",
                "evolutionary_scale": "种群",
                "research_method": "实验",
                "key_findings": ["Finding"],
                "evolutionary_mechanism": "自然选择",
                "importance_score": 50,
                "innovation_summary": "Test",
            }
        ]

        def mock_get_by_doi(session, doi):
            return None  # 论文不存在

        call_log = []

        def mock_update_paper(session, paper_id, **kwargs):
            call_log.append({"id": paper_id})
            return None

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.crud.get_paper_by_doi",
            mock_get_by_doi,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.crud.update_paper",
            mock_update_paper,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.create_engine",
            lambda x: mock.Mock(),
        )

        mock_session = mock.Mock()
        mock_session.__enter__ = mock.Mock(return_value=mock_session)
        mock_session.commit = mock.Mock()
        mock_session.__exit__ = mock.Mock(return_value=False)

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.Session",
            lambda *args, **kwargs: mock_session,
        )

        # Act
        from evo_flywheel.scheduler.analysis import _update_analysis_to_db

        count = _update_analysis_to_db(analyzed_papers)

        # Assert
        assert count == 0
        assert len(call_log) == 0


class TestAnalyzeUnanalyzedPapers:
    """批量分析论文测试"""

    def test_analyze_unanalyzed_papers_calls_batch_analyzer(self, monkeypatch):
        """测试调用批量分析器"""
        # Arrange
        unanalyzed_papers = [
            {
                "id": 1,
                "title": "Paper 1",
                "abstract": "Abstract 1",
                "doi": "10.1234/test.001",
                "url": "https://example.com/1",
                "authors": ["Author 1"],
            },
            {
                "id": 2,
                "title": "Paper 2",
                "abstract": "Abstract 2",
                "doi": "10.1234/test.002",
                "url": "https://example.com/2",
                "authors": ["Author 2"],
            },
        ]

        analyzed_papers = [
            {
                **unanalyzed_papers[0],
                "taxa": "Drosophila",
                "evolutionary_scale": "种群",
                "research_method": "实验",
                "key_findings": ["Finding 1"],
                "evolutionary_mechanism": "自然选择",
                "importance_score": 85,
                "innovation_summary": "Innovation",
            },
            {
                **unanalyzed_papers[1],
                "taxa": "E. coli",
                "evolutionary_scale": "分子",
                "research_method": "比较",
                "key_findings": ["Finding 2"],
                "evolutionary_mechanism": "突变",
                "importance_score": 70,
                "innovation_summary": "Discovery",
            },
        ]

        call_log = []

        def mock_get_unanalyzed(max_papers=None):
            call_log.append(("get_unanalyzed", max_papers))
            return unanalyzed_papers

        def mock_analyze_batch(papers, **kwargs):
            call_log.append(("analyze_batch", len(papers)))
            return analyzed_papers

        def mock_update_to_db(papers):
            call_log.append(("update_to_db", len(papers)))
            return 2

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis._get_unanalyzed_papers",
            mock_get_unanalyzed,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.analyze_papers_batch",
            mock_analyze_batch,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis._update_analysis_to_db",
            mock_update_to_db,
        )

        # Act
        from evo_flywheel.scheduler.analysis import analyze_unanalyzed_papers

        result = analyze_unanalyzed_papers(max_papers=50)

        # Assert
        assert len(call_log) == 3
        assert call_log[0] == ("get_unanalyzed", 50)
        assert call_log[1] == ("analyze_batch", 2)
        assert call_log[2] == ("update_to_db", 2)
        assert result["analyzed"] == 2

    def test_analyze_unanalyzed_papers_returns_zero_when_no_papers(self, monkeypatch):
        """测试没有论文时返回零"""

        # Arrange
        def mock_get_unanalyzed(max_papers=None):
            return []

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis._get_unanalyzed_papers",
            mock_get_unanalyzed,
        )

        # Act
        from evo_flywheel.scheduler.analysis import analyze_unanalyzed_papers

        result = analyze_unanalyzed_papers()

        # Assert
        assert result["analyzed"] == 0
        assert result["skipped"] == 0


class TestGetUnembeddedPapers:
    """获取未向量化论文测试"""

    def test_get_unembedded_papers_returns_papers_with_embedded_false(self, monkeypatch):
        """测试返回 embedded=False 的论文"""
        # Arrange
        mock_db_result = [
            (1, "Paper 1", "Abstract 1", "10.1234/test.001"),
            (2, "Paper 2", "Abstract 2", "10.1234/test.002"),
        ]

        mock_result = mock.Mock()
        mock_result.__iter__ = lambda self: iter(mock_db_result)
        mock_session = mock.Mock()
        mock_session.execute.return_value = mock_result
        mock_session.__enter__ = mock.Mock(return_value=mock_session)
        mock_session.__exit__ = mock.Mock(return_value=False)

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.Session",
            lambda *args, **kwargs: mock_session,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.create_engine",
            lambda x: mock.Mock(),
        )

        # Act
        from evo_flywheel.scheduler.analysis import _get_unembedded_papers

        papers = _get_unembedded_papers(max_papers=100)

        # Assert
        assert len(papers) == 2
        assert papers[0]["id"] == 1
        assert papers[0]["abstract"] == "Abstract 1"
        assert papers[1]["abstract"] == "Abstract 2"


class TestSaveEmbeddingsToChroma:
    """保存向量到 Chroma 测试"""

    def test_save_embeddings_to_chroma_saves_vectors(self, monkeypatch):
        """测试保存向量到 Chroma"""
        # Arrange
        papers = [
            {"id": 1, "title": "Paper 1", "abstract": "Abstract 1", "doi": "10.1234/test.001"},
            {"id": 2, "title": "Paper 2", "abstract": "Abstract 2", "doi": "10.1234/test.002"},
        ]
        vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

        mock_collection = mock.Mock()
        mock_client = mock.Mock()
        mock_client.get_or_create_collection.return_value = mock_collection

        mock_db_paper_1 = mock.Mock()
        mock_db_paper_1.id = 1
        mock_db_paper_2 = mock.Mock()
        mock_db_paper_2.id = 2

        call_log = []

        def mock_get_by_doi(session, doi):
            call_log.append(("get_by_doi", doi))
            if doi == "10.1234/test.001":
                return mock_db_paper_1
            return mock_db_paper_2

        def mock_update_paper(session, paper_id, **kwargs):
            call_log.append(("update_paper", paper_id, kwargs))
            return mock_db_paper_1 if paper_id == 1 else mock_db_paper_2

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.get_chroma_client",
            lambda: mock_client,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.crud.get_paper_by_doi",
            mock_get_by_doi,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.crud.update_paper",
            mock_update_paper,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.create_engine",
            lambda x: mock.Mock(),
        )

        mock_session = mock.Mock()
        mock_session.__enter__ = mock.Mock(return_value=mock_session)
        mock_session.commit = mock.Mock()
        mock_session.__exit__ = mock.Mock(return_value=False)

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.Session",
            lambda *args, **kwargs: mock_session,
        )

        # Act
        from evo_flywheel.scheduler.analysis import _save_embeddings_to_chroma

        count = _save_embeddings_to_chroma(papers, vectors)

        # Assert
        assert count == 2
        assert mock_collection.add.call_count == 2
        assert any("update_paper" in log for log in call_log)

    def test_save_embeddings_skips_none_vectors(self, monkeypatch):
        """测试跳过 None 向量"""
        # Arrange
        papers = [
            {"id": 1, "title": "Paper 1", "abstract": "Abstract 1", "doi": "10.1234/test.001"},
            {"id": 2, "title": "Paper 2", "abstract": "Abstract 2", "doi": "10.1234/test.002"},
        ]
        vectors = [[0.1, 0.2, 0.3], None]  # 第二个向量失败

        mock_collection = mock.Mock()
        mock_client = mock.Mock()
        mock_client.get_or_create_collection.return_value = mock_collection

        mock_db_paper = mock.Mock()
        mock_db_paper.id = 1

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.get_chroma_client",
            lambda: mock_client,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.crud.get_paper_by_doi",
            lambda session, doi: mock_db_paper if doi == "10.1234/test.001" else None,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.crud.update_paper",
            lambda session, paper_id, **kwargs: mock_db_paper,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.create_engine",
            lambda x: mock.Mock(),
        )

        mock_session = mock.Mock()
        mock_session.__enter__ = mock.Mock(return_value=mock_session)
        mock_session.commit = mock.Mock()
        mock_session.__exit__ = mock.Mock(return_value=False)

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.Session",
            lambda *args, **kwargs: mock_session,
        )

        # Act
        from evo_flywheel.scheduler.analysis import _save_embeddings_to_chroma

        count = _save_embeddings_to_chroma(papers, vectors)

        # Assert
        assert count == 1
        assert mock_collection.add.call_count == 1


class TestEmbedUnembeddedPapers:
    """批量向量化测试"""

    def test_embed_unembedded_papers_calls_embedding_functions(self, monkeypatch):
        """测试调用向量化函数"""
        # Arrange
        unembedded_papers = [
            {"id": 1, "abstract": "Abstract 1", "doi": "10.1234/test.001"},
            {"id": 2, "abstract": "Abstract 2", "doi": "10.1234/test.002"},
        ]

        vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

        call_log = []

        def mock_get_unembedded(max_papers=None):
            call_log.append(("get_unembedded", max_papers))
            return unembedded_papers

        def mock_generate_batch(texts, **kwargs):
            call_log.append(("generate_batch", len(texts)))
            return vectors

        def mock_save_to_chroma(papers, vectors):
            call_log.append(("save_to_chroma", len(papers)))
            return 2

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis._get_unembedded_papers",
            mock_get_unembedded,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.generate_embeddings_batch",
            mock_generate_batch,
        )
        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis._save_embeddings_to_chroma",
            mock_save_to_chroma,
        )

        # Act
        from evo_flywheel.scheduler.analysis import embed_unembedded_papers

        result = embed_unembedded_papers(max_papers=50)

        # Assert
        assert len(call_log) == 3
        assert call_log[0] == ("get_unembedded", 50)
        assert call_log[1] == ("generate_batch", 2)
        assert call_log[2] == ("save_to_chroma", 2)
        assert result["embedded"] == 2


class TestMainAnalysis:
    """CLI 入口测试"""

    def test_main_analyze_mode_calls_analyze_function(self, monkeypatch):
        """测试分析模式调用分析函数"""
        # Arrange
        call_log = []

        def mock_analyze(**kwargs):
            call_log.append(("analyze", kwargs))
            return {"analyzed": 10, "skipped": 0}

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.analyze_unanalyzed_papers",
            mock_analyze,
        )
        monkeypatch.setattr("sys.argv", ["evo-analyze"])

        # Act
        from evo_flywheel.scheduler.analysis import main

        main()

        # Assert
        assert len(call_log) == 1
        assert call_log[0][0] == "analyze"

    def test_main_embed_only_mode_calls_embed_function(self, monkeypatch):
        """测试仅向量化模式"""
        # Arrange
        call_log = []

        def mock_embed(**kwargs):
            call_log.append(("embed", kwargs))
            return {"embedded": 10}

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.embed_unembedded_papers",
            mock_embed,
        )
        monkeypatch.setattr("sys.argv", ["evo-analyze", "--embed-only"])

        # Act
        from evo_flywheel.scheduler.analysis import main

        main()

        # Assert
        assert len(call_log) == 1
        assert call_log[0][0] == "embed"

    def test_main_with_max_papers_argument(self, monkeypatch):
        """测试 --max 参数传递"""
        # Arrange
        call_log = []

        def mock_analyze(**kwargs):
            call_log.append(("analyze", kwargs))
            return {"analyzed": 5}

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.analyze_unanalyzed_papers",
            mock_analyze,
        )
        monkeypatch.setattr("sys.argv", ["evo-analyze", "--max", "5"])

        # Act
        from evo_flywheel.scheduler.analysis import main

        main()

        # Assert
        assert call_log[0][1]["max_papers"] == 5

    def test_main_handles_exceptions_gracefully(self, monkeypatch):
        """测试异常处理"""

        # Arrange
        def mock_analyze(**kwargs):
            raise Exception("Analysis failed")

        monkeypatch.setattr(
            "evo_flywheel.scheduler.analysis.analyze_unanalyzed_papers",
            mock_analyze,
        )
        monkeypatch.setattr("sys.argv", ["evo-analyze"])

        # Act & Assert
        from evo_flywheel.scheduler.analysis import main

        # 不应该抛出异常
        try:
            main()
        except Exception as e:
            raise AssertionError(f"main() should handle exceptions, but raised: {e}") from e
