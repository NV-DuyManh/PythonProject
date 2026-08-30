import logging
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from codegate.repositories.analysis_store import analysis_store
from codegate.repositories.quality_store import quality_store
from codegate.engines.quality.engine import QualityScoreEngine
from codegate.engines.quality.explanation import build_breakdown_json
from codegate.engines.quality.config import CALCULATION_VERSION
from codegate.schemas.quality import QualityScoreResponse

logger = logging.getLogger(__name__)

class QualityScoreService:
    def calculate_and_persist(self, db: Session, analysis_run_id: int) -> Optional[QualityScoreResponse]:
        analysis_run = analysis_store.get_by_id(db, analysis_run_id)
        if not analysis_run:
            logger.error(f"Cannot calculate quality: AnalysisRun {analysis_run_id} not found")
            return None
            
        try:
            # Inputs
            findings = analysis_run.findings
            metrics = analysis_run.code_metrics
            
            # Testing Component Fetching
            testing_score = None
            try:
                from codegate.repositories.testing_store import TestingStore
                from codegate.engines.testing.schemas import ExecutionStatus, TestOutcome
                testing_store = TestingStore()
                test_run = testing_store.get_test_run(db, analysis_run_id)
                if test_run and test_run.execution_status == ExecutionStatus.COMPLETED.value:
                    if test_run.test_outcome == TestOutcome.FAILED.value:
                        testing_score = 0.0
                    elif test_run.test_outcome == TestOutcome.PASSED.value:
                        cov_report = test_run.coverage_report
                        if cov_report and cov_report.changed_line_coverage is not None:
                            testing_score = cov_report.changed_line_coverage
                        elif cov_report and cov_report.line_coverage is not None:
                            testing_score = cov_report.line_coverage
            except ImportError:
                pass # If testing not fully initialized
            
            # Engine calculation
            engine_result = QualityScoreEngine.calculate(findings, metrics, testing_score)
            
            # Persist
            breakdown = build_breakdown_json(engine_result)
            
            # Map component scores
            component_scores = {}
            for comp in engine_result.components:
                component_scores[f"{comp.name}_score"] = comp.score

            obj_in = {
                "analysis_run_id": analysis_run_id,
                "overall_score": engine_result.overall_score,
                "grade": engine_result.grade,
                "available_weight": engine_result.available_weight,
                "is_complete": engine_result.is_complete,
                "missing_dimensions": engine_result.missing_dimensions,
                "breakdown_json": breakdown,
                "calculation_version": engine_result.calculation_version,
                **component_scores
            }
            
            qs = quality_store.upsert(db, obj_in)
            
            # Format response properly so it matches QualityScoreResponse structure
            resp = self._format_response(qs)
            logger.info(f"Quality score for analysis {analysis_run_id} calculated successfully. Score: {resp.overall_score}, Grade: {resp.grade}")
            return resp
            
        except Exception as e:
            logger.error(f"Failed to calculate quality score for analysis {analysis_run_id}: {e}", exc_info=True)
            return None
            
    def get_quality(self, db: Session, analysis_run_id: int) -> QualityScoreResponse:
        # First verify analysis run exists
        analysis_run = analysis_store.get_by_id(db, analysis_run_id)
        if not analysis_run:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found")
            
        qs = quality_store.get_latest_for_analysis(db, analysis_run_id)
        if not qs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quality score not calculated for this analysis run")
            
        return self._format_response(qs)
        
    def recalculate(self, db: Session, analysis_run_id: int) -> QualityScoreResponse:
        # Verify analysis run exists
        analysis_run = analysis_store.get_by_id(db, analysis_run_id)
        if not analysis_run:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found")
            
        resp = self.calculate_and_persist(db, analysis_run_id)
        if not resp:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to recalculate quality score")
            
        return resp
        
    def _format_response(self, qs) -> QualityScoreResponse:
        """Hydrates the breakdown_json back into the response schema structure"""
        return QualityScoreResponse(
            id=qs.id,
            analysis_run_id=qs.analysis_run_id,
            overall_score=qs.overall_score,
            grade=qs.grade,
            is_complete=qs.is_complete,
            available_weight=qs.available_weight,
            missing_dimensions=qs.missing_dimensions,
            components=qs.breakdown_json.get("components", []),
            calculation_version=qs.calculation_version,
            created_at=qs.created_at,
            updated_at=qs.updated_at
        )

quality_service = QualityScoreService()
