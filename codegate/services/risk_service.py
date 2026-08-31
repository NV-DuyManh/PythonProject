import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from codegate.engines.risk.engine import RiskScoreEngine
from codegate.engines.risk.explanation import build_risk_breakdown
from codegate.repositories.analysis_store import analysis_store
from codegate.repositories.risk_store import risk_store
from codegate.schemas.risk import RiskScoreResponse

logger = logging.getLogger(__name__)

class RiskScoreService:
    def calculate_and_persist(self, db: Session, analysis_run_id: int) -> Optional[RiskScoreResponse]:
        analysis_run = analysis_store.get_by_id(db, analysis_run_id)
        if not analysis_run:
            logger.error(f"Cannot calculate risk: AnalysisRun {analysis_run_id} not found")
            return None
            
        try:
            # Inputs
            pr = analysis_run.pull_request
            pr_files = pr.files if pr else []
            findings = analysis_run.findings
            metrics = analysis_run.code_metrics
            analyzer_runs = analysis_run.analyzer_runs
            
            # Engine calculation
            engine_result = RiskScoreEngine.calculate(pr, pr_files, findings, metrics, analyzer_runs)
            
            # Persist
            breakdown = build_risk_breakdown(engine_result)
            
            # Map component scores
            component_scores = {}
            for comp in engine_result.components:
                component_scores[f"{comp.name}_risk"] = comp.risk

            obj_in = {
                "analysis_run_id": analysis_run_id,
                "overall_risk": engine_result.overall_risk,
                "risk_level": engine_result.risk_level,
                "available_weight": engine_result.available_weight,
                "is_complete": engine_result.is_complete,
                "missing_dimensions": engine_result.missing_dimensions,
                "breakdown_json": breakdown,
                "calculation_version": engine_result.calculation_version,
                **component_scores
            }
            
            rs = risk_store.upsert(db, obj_in)
            
            # Format response properly
            resp = self._format_response(rs)
            logger.info(f"Risk score for analysis {analysis_run_id} calculated successfully. Score: {resp.overall_risk}, Level: {resp.risk_level}")
            return resp
            
        except Exception as e:
            logger.error(f"Failed to calculate risk score for analysis {analysis_run_id}: {e}", exc_info=True)
            return None
            
    def get_risk(self, db: Session, analysis_run_id: int) -> RiskScoreResponse:
        # First verify analysis run exists
        analysis_run = analysis_store.get_by_id(db, analysis_run_id)
        if not analysis_run:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found")
            
        rs = risk_store.get_latest_for_analysis(db, analysis_run_id)
        if not rs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk score not calculated for this analysis run")
            
        return self._format_response(rs)
        
    def recalculate(self, db: Session, analysis_run_id: int) -> RiskScoreResponse:
        # Verify analysis run exists
        analysis_run = analysis_store.get_by_id(db, analysis_run_id)
        if not analysis_run:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found")
            
        resp = self.calculate_and_persist(db, analysis_run_id)
        if not resp:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to recalculate risk score")
            
        return resp
        
    def _format_response(self, rs) -> RiskScoreResponse:
        """Hydrates the breakdown_json back into the response schema structure"""
        return RiskScoreResponse(
            id=rs.id,
            analysis_run_id=rs.analysis_run_id,
            overall_risk=rs.overall_risk,
            risk_level=rs.risk_level,
            change_surface_risk=rs.change_surface_risk,
            sensitive_path_risk=rs.sensitive_path_risk,
            security_risk=rs.security_risk,
            complexity_risk=rs.complexity_risk,
            is_complete=rs.is_complete,
            available_weight=rs.available_weight,
            missing_dimensions=rs.missing_dimensions,
            components=rs.breakdown_json.get("components", []),
            flags=rs.breakdown_json.get("flags", []),
            calculation_version=rs.calculation_version,
            created_at=rs.created_at,
            updated_at=rs.updated_at
        )

risk_service = RiskScoreService()
