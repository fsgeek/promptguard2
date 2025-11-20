"""Trajectory analyzer for temporal attack detection."""

from typing import Dict

from src.database.schemas.phase3_evaluation import PrincipleEvaluation, EvaluationPrinciple
from src.evaluation.temporal.factory import TemporalDetectorFactory
from src.evaluation.temporal.detector import DetectionResult


class TrajectoryAnalyzer:
    """Analyze T/I/F trajectories for attack patterns.

    Usage:
        analyzer = TrajectoryAnalyzer(db=arango_db)
        results = analyzer.analyze(attack_id="xguard_001", detector_name="trust_ema")
    """

    def __init__(self, db):
        """Initialize analyzer.

        Args:
            db: ArangoDB database connection
        """
        self.db = db

    def analyze(
        self,
        attack_id: str,
        detector_name: str = "trust_ema",
        **detector_kwargs,
    ) -> Dict[str, DetectionResult]:
        """Analyze trajectories for all evaluated principles.

        Args:
            attack_id: Attack sequence ID
            detector_name: Detector to use ("trust_ema")
            **detector_kwargs: Additional detector parameters

        Returns:
            Dict mapping principle -> DetectionResult
        """
        results = {}

        # Find all principles evaluated for this attack
        principles = self._get_evaluated_principles(attack_id)

        # Create detector
        detector = TemporalDetectorFactory.create(detector_name, **detector_kwargs)

        # Analyze each principle
        for principle in principles:
            trajectory = self._load_trajectory(attack_id, principle)

            if trajectory:
                result = detector.detect(trajectory, principle)
                results[principle] = result

        # Store detection results in evaluation_sequences metadata
        self._store_detection_results(attack_id, results)

        return results

    def _get_evaluated_principles(self, attack_id: str) -> list[str]:
        """Get list of principles evaluated for this attack."""
        aql = """
        FOR doc IN phase3_principle_evaluations
            FILTER doc.attack_id == @attack_id
            RETURN DISTINCT doc.principle
        """

        cursor = self.db.aql.execute(aql, bind_vars={"attack_id": attack_id})
        return list(cursor)

    def _load_trajectory(self, attack_id: str, principle: str) -> list[PrincipleEvaluation]:
        """Load trajectory for specific attack + principle."""
        aql = """
        FOR doc IN phase3_principle_evaluations
            FILTER doc.attack_id == @attack_id
            FILTER doc.principle == @principle
            SORT doc.turn_number ASC
            RETURN doc
        """

        cursor = self.db.aql.execute(
            aql,
            bind_vars={"attack_id": attack_id, "principle": principle},
        )

        docs = list(cursor)

        # Convert to PrincipleEvaluation objects
        from src.database.schemas.phase3_evaluation import NeutrosophicScore
        from datetime import datetime

        evaluations = []
        for doc in docs:
            eval_obj = PrincipleEvaluation(
                attack_id=doc["attack_id"],
                principle=EvaluationPrinciple(doc["principle"]),
                turn_number=doc["turn_number"],
                evaluator_model=doc["evaluator_model"],
                observer_prompt_version=doc["observer_prompt_version"],
                timestamp=datetime.fromisoformat(doc["timestamp"]) if isinstance(doc["timestamp"], str) else doc["timestamp"],
                scores=NeutrosophicScore(**doc["scores"]),
                reasoning=doc["reasoning"],
                raw_response=doc["raw_response"],
                model_temperature=doc.get("model_temperature"),
                experiment_id=doc["experiment_id"],
                cost_usd=doc.get("cost_usd"),
                latency_ms=doc.get("latency_ms"),
            )
            evaluations.append(eval_obj)

        return evaluations

    def _store_detection_results(
        self,
        attack_id: str,
        results: Dict[str, DetectionResult],
    ) -> None:
        """Store detection results in evaluation_sequences metadata."""
        coll = self.db.collection("phase3_evaluation_sequences")

        # Convert results to dict
        results_dict = {
            principle: result.model_dump(mode="json")
            for principle, result in results.items()
        }

        # Update document (embedded in metadata)
        coll.update_match(
            {"_key": attack_id},
            {"metadata.detection_results": results_dict},
        )
