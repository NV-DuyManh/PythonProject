from typing import Optional, List
from sqlalchemy.orm import Session
from codegate.database.models.testing import TestConfiguration, TestRun, CoverageReport

class TestingStore:
    def get_test_configuration(self, db: Session, repository_id: int) -> Optional[TestConfiguration]:
        return db.query(TestConfiguration).filter(TestConfiguration.repository_id == repository_id).first()
        
    def upsert_test_configuration(self, db: Session, repository_id: int, config_data: dict) -> TestConfiguration:
        config = self.get_test_configuration(db, repository_id)
        if config:
            for key, value in config_data.items():
                setattr(config, key, value)
        else:
            config = TestConfiguration(repository_id=repository_id, **config_data)
            db.add(config)
        db.flush()
        return config

    def get_test_run(self, db: Session, analysis_run_id: int) -> Optional[TestRun]:
        return db.query(TestRun).filter(TestRun.analysis_run_id == analysis_run_id).first()
        
    def create_test_run(self, db: Session, test_run_data: dict) -> TestRun:
        test_run = TestRun(**test_run_data)
        db.add(test_run)
        db.flush()
        return test_run
        
    def update_test_run(self, db: Session, analysis_run_id: int, update_data: dict) -> Optional[TestRun]:
        test_run = self.get_test_run(db, analysis_run_id)
        if test_run:
            for key, value in update_data.items():
                setattr(test_run, key, value)
            db.flush()
        return test_run
        
    def upsert_test_run(self, db: Session, analysis_run_id: int, test_run_data: dict) -> TestRun:
        test_run = self.get_test_run(db, analysis_run_id)
        if test_run:
            for key, value in test_run_data.items():
                setattr(test_run, key, value)
        else:
            test_run = TestRun(analysis_run_id=analysis_run_id, **test_run_data)
            db.add(test_run)
        db.flush()
        return test_run
        
    def get_coverage_report(self, db: Session, test_run_id: int) -> Optional[CoverageReport]:
        return db.query(CoverageReport).filter(CoverageReport.test_run_id == test_run_id).first()
        
    def upsert_coverage_report(self, db: Session, test_run_id: int, coverage_data: dict) -> CoverageReport:
        report = self.get_coverage_report(db, test_run_id)
        if report:
            for key, value in coverage_data.items():
                setattr(report, key, value)
        else:
            report = CoverageReport(test_run_id=test_run_id, **coverage_data)
            db.add(report)
        db.flush()
        return report
