"""数据库模型单元测试 - 报告相关

测试 DailyReport 和 PaperCluster 模型的属性和方法
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from evo_flywheel.db.models import Base, DailyReport, PaperCluster


@pytest.fixture
def db_session(temp_db_path):
    """创建临时数据库会话"""
    engine = create_engine(f"sqlite:///{temp_db_path}")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


class TestPaperCluster:
    """PaperCluster 模型测试"""

    def test_create_cluster(self, db_session):
        """测试创建聚类记录"""
        # Arrange
        report = DailyReport(
            report_date="2024-12-29",
            total_papers=10,
            high_value_papers=3,
        )
        db_session.add(report)
        db_session.commit()

        # Act
        cluster = PaperCluster(
            report_id=report.id,
            cluster_name="Drosophila_实验进化",
            paper_ids="1,2,3,4,5",
            cluster_summary="果蝇实验进化相关研究",
        )
        db_session.add(cluster)
        db_session.commit()

        # Assert
        assert cluster.id is not None
        assert cluster.cluster_name == "Drosophila_实验进化"
        assert cluster.report_id == report.id

    def test_paper_ids_list_property(self, db_session):
        """测试 paper_ids_list 属性"""
        # Arrange
        cluster = PaperCluster(
            report_id=1,
            cluster_name="Test",
            paper_ids="1,2,3,  4,5",  # 包含空格
        )

        # Act & Assert
        assert cluster.paper_ids_list == [1, 2, 3, 4, 5]

    def test_paper_ids_list_setter(self, db_session):
        """测试 paper_ids_list setter"""
        # Arrange
        cluster = PaperCluster(
            report_id=1,
            cluster_name="Test",
            paper_ids="",
        )

        # Act
        cluster.paper_ids_list = [10, 20, 30]

        # Assert
        assert cluster.paper_ids == "10,20,30"

    def test_findings_list_property(self, db_session):
        """测试 findings_list 属性"""
        # Arrange
        cluster = PaperCluster(
            report_id=1,
            cluster_name="Test",
            paper_ids="1,2,3",
            key_findings='["发现1", "发现2", "发现3"]',
        )

        # Act & Assert
        assert cluster.findings_list == ["发现1", "发现2", "发现3"]

    def test_findings_list_setter(self, db_session):
        """测试 findings_list setter"""
        # Arrange
        cluster = PaperCluster(
            report_id=1,
            cluster_name="Test",
            paper_ids="1,2,3",
        )

        # Act
        cluster.findings_list = ["新发现1", "新发现2"]

        # Assert
        import json

        assert json.loads(cluster.key_findings) == ["新发现1", "新发现2"]

    def test_findings_list_handles_invalid_json(self, db_session):
        """测试 findings_list 处理无效 JSON"""
        # Arrange
        cluster = PaperCluster(
            report_id=1,
            cluster_name="Test",
            paper_ids="1,2,3",
            key_findings="invalid json",
        )

        # Act & Assert
        assert cluster.findings_list == []

    def test_cluster_relationship_to_report(self, db_session):
        """测试聚类与报告的关系"""
        # Arrange
        report = DailyReport(
            report_date="2024-12-29",
            total_papers=10,
            high_value_papers=3,
        )
        db_session.add(report)
        db_session.commit()

        cluster = PaperCluster(
            report_id=report.id,
            cluster_name="Test Cluster",
            paper_ids="1,2,3",
        )
        db_session.add(cluster)
        db_session.commit()

        # Act
        fetched_report = db_session.query(DailyReport).first()

        # Assert
        assert len(fetched_report.clusters) == 1
        assert fetched_report.clusters[0].cluster_name == "Test Cluster"

    def test_cluster_repr(self, db_session):
        """测试 __repr__ 方法"""
        # Arrange
        cluster = PaperCluster(
            id=1,
            report_id=10,
            cluster_name="Test Cluster",
            paper_ids="1,2,3",
        )

        # Act & Assert
        assert repr(cluster) == "<PaperCluster(id=1, name='Test Cluster', report_id=10)>"


class TestDailyReport:
    """DailyReport 模型增强测试"""

    def test_report_data_property_getter(self, db_session):
        """测试 report_data 属性获取"""
        # Arrange
        import json

        data = {
            "research_summary": "测试摘要",
            "hot_topics": [{"topic": "热点1"}],
        }
        report = DailyReport(
            report_date="2024-12-29",
            report_content=json.dumps(data, ensure_ascii=False),
        )

        # Act
        result = report.report_data

        # Assert
        assert result == data
        assert result["research_summary"] == "测试摘要"

    def test_report_data_property_setter(self, db_session):
        """测试 report_data 属性设置"""
        # Arrange
        report = DailyReport(report_date="2024-12-29")

        # Act
        data = {"research_summary": "新摘要", "hot_topics": []}
        report.report_data = data

        # Assert
        import json

        assert json.loads(report.report_content) == data

    def test_report_data_handles_invalid_json(self, db_session):
        """测试 report_data 处理无效 JSON"""
        # Arrange
        report = DailyReport(
            report_date="2024-12-29",
            report_content="not valid json",
        )

        # Act & Assert
        assert report.report_data == {}

    def test_report_data_handles_empty_content(self, db_session):
        """测试 report_data 处理空内容"""
        # Arrange
        report = DailyReport(report_date="2024-12-29", report_content=None)

        # Act & Assert
        assert report.report_data == {}

    def test_clusters_cascade_delete(self, db_session):
        """测试删除报告时级联删除聚类"""
        # Arrange
        report = DailyReport(
            report_date="2024-12-29",
            total_papers=10,
            high_value_papers=3,
        )
        db_session.add(report)
        db_session.commit()

        cluster1 = PaperCluster(
            report_id=report.id,
            cluster_name="Cluster 1",
            paper_ids="1,2,3",
        )
        cluster2 = PaperCluster(
            report_id=report.id,
            cluster_name="Cluster 2",
            paper_ids="4,5,6",
        )
        db_session.add_all([cluster1, cluster2])
        db_session.commit()

        cluster_count_before = db_session.query(PaperCluster).count()

        # Act
        db_session.delete(report)
        db_session.commit()

        # Assert
        cluster_count_after = db_session.query(PaperCluster).count()
        assert cluster_count_before == 2
        assert cluster_count_after == 0


class TestDailyReportIntegration:
    """DailyReport 集成测试"""

    def test_create_full_report_with_clusters(self, db_session):
        """测试创建包含聚类的完整报告"""
        # Arrange

        report_data = {
            "research_summary": "今天的研究亮点",
            "hot_topics": [
                {"topic": "果蝇进化", "paper_count": 5},
                {"topic": "分子钟", "paper_count": 3},
            ],
            "recommended_papers": [
                {"paper_id": 1, "priority": "must_read"},
            ],
        }

        report = DailyReport(
            report_date="2024-12-29",
            total_papers=15,
            high_value_papers=5,
            top_paper_ids="1,2,3,4,5",
        )
        report.report_data = report_data
        db_session.add(report)
        db_session.commit()

        # Act
        cluster = PaperCluster(
            report_id=report.id,
            cluster_name="Drosophila_实验进化",
            paper_ids="1,2,3",
            cluster_summary="果蝇实验进化研究",
        )
        cluster.findings_list = ["发现1", "发现2"]
        db_session.add(cluster)
        db_session.commit()

        # Assert
        fetched_report = db_session.query(DailyReport).first()
        assert fetched_report.total_papers == 15
        assert fetched_report.report_data["research_summary"] == "今天的研究亮点"
        assert len(fetched_report.clusters) == 1
        assert fetched_report.clusters[0].findings_list == ["发现1", "发现2"]
