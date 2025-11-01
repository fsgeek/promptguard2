"""
Executor vs Observer Paradox Analysis
FR5: Comparative Analysis

Analyzes the phenomenon where models comply when executing (Step 1)
but detect as violations when observing (Step 2).

Constitutional Principle VI: Data Provenance - All analysis derived from raw data
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from arango.database import StandardDatabase


@dataclass
class ParadoxExample:
    """Single example of executor/observer paradox."""
    attack_id: str
    prompt_text: str
    ground_truth: str
    model: str
    step1_response: str
    step1_classification: str  # comply/refuse/unclear
    step2_observer_model: str
    step2_neutrosophic_scores: Dict[str, float]  # {T, I, F}
    step2_detected: bool


@dataclass
class ParadoxStats:
    """Statistics for executor/observer paradox."""
    total_comply_in_step1: int  # Total evaluations where model complied in Step 1
    detected_in_step2: int  # Of those, how many were detected by observer
    paradox_rate: float  # % of Step 1 compliance that observer detected

    # Breakdown by category
    by_category: Dict[str, int]  # category -> count of paradox cases
    by_model: Dict[str, int]  # model -> count of paradox cases

    # Example cases
    examples: List[ParadoxExample]


class ExecutorObserverAnalyzer:
    """
    Analyzes executor vs observer paradox.

    Research Question:
    When a model complies with an attack in Step 1 (executor role),
    does an observer model detect it as a violation in Step 2?

    This reveals the gap between execution behavior (RLHF baseline) and
    detection capability (observer framing).
    """

    def __init__(self, db: StandardDatabase):
        """
        Initialize executor/observer analyzer.

        Args:
            db: ArangoDB database connection
        """
        self.db = db

    def analyze(
        self,
        step1_experiment_id: str = "exp_phase1_step1_baseline_v1",
        step2_experiment_id: str = "exp_phase1_step2_pre_filter_v1",
        max_examples: int = 10
    ) -> ParadoxStats:
        """
        Analyze executor vs observer paradox.

        Args:
            step1_experiment_id: Step 1 experiment identifier
            step2_experiment_id: Step 2 experiment identifier
            max_examples: Maximum number of example cases to include

        Returns:
            ParadoxStats with metrics and examples
        """
        # Find cases where Step 1 = comply AND Step 2 = detected
        paradox_cases = self._find_paradox_cases(
            step1_experiment_id,
            step2_experiment_id
        )

        # Count total Step 1 compliance (denominator)
        total_comply = self._count_step1_compliance(step1_experiment_id)

        # Calculate rate
        detected_count = len(paradox_cases)
        paradox_rate = (detected_count / total_comply * 100) if total_comply > 0 else 0.0

        # Break down by category and model
        by_category = self._breakdown_by_category(paradox_cases)
        by_model = self._breakdown_by_model(paradox_cases)

        # Get example cases with full details
        examples = self._get_example_details(paradox_cases[:max_examples])

        return ParadoxStats(
            total_comply_in_step1=total_comply,
            detected_in_step2=detected_count,
            paradox_rate=paradox_rate,
            by_category=by_category,
            by_model=by_model,
            examples=examples
        )

    def _find_paradox_cases(
        self,
        step1_experiment_id: str,
        step2_experiment_id: str
    ) -> List[Dict]:
        """
        Find cases where model complied in Step 1 but observer detected in Step 2.

        Returns:
            List of {attack_id, model, ground_truth} for paradox cases
        """
        query = """
        FOR step1 IN step1_baseline_responses
            FILTER step1.experiment_id == @step1_exp
            FILTER step1.compliance_classification == "comply"

            FOR step2 IN step2_pre_evaluations
                FILTER step2.experiment_id == @step2_exp
                FILTER step2.attack_id == step1.attack_id
                FILTER step2.detected == true

                RETURN {
                    attack_id: step1.attack_id,
                    model: step1.target_model,
                    ground_truth: step1.ground_truth,
                    observer_model: step2.observer_model
                }
        """

        cursor = self.db.aql.execute(
            query,
            bind_vars={
                'step1_exp': step1_experiment_id,
                'step2_exp': step2_experiment_id
            }
        )

        return list(cursor)

    def _count_step1_compliance(self, step1_experiment_id: str) -> int:
        """Count total compliance cases in Step 1."""
        query = """
        FOR response IN step1_baseline_responses
            FILTER response.experiment_id == @experiment_id
            FILTER response.compliance_classification == "comply"
            COLLECT WITH COUNT INTO count
            RETURN count
        """

        cursor = self.db.aql.execute(
            query,
            bind_vars={'experiment_id': step1_experiment_id}
        )

        return next(cursor, 0)

    def _breakdown_by_category(self, paradox_cases: List[Dict]) -> Dict[str, int]:
        """Count paradox cases by ground_truth category."""
        breakdown = {}
        for case in paradox_cases:
            category = case['ground_truth']
            breakdown[category] = breakdown.get(category, 0) + 1
        return breakdown

    def _breakdown_by_model(self, paradox_cases: List[Dict]) -> Dict[str, int]:
        """Count paradox cases by model."""
        breakdown = {}
        for case in paradox_cases:
            model = case['model']
            breakdown[model] = breakdown.get(model, 0) + 1
        return breakdown

    def _get_example_details(self, paradox_cases: List[Dict]) -> List[ParadoxExample]:
        """
        Get full details for example paradox cases.

        Args:
            paradox_cases: List of {attack_id, model, ground_truth} dicts

        Returns:
            List of ParadoxExample objects with full details
        """
        examples = []

        for case in paradox_cases:
            # Get Step 1 details
            step1_data = self._get_step1_details(case['attack_id'], case['model'])
            if not step1_data:
                continue

            # Get Step 2 details
            step2_data = self._get_step2_details(case['attack_id'])
            if not step2_data:
                continue

            examples.append(ParadoxExample(
                attack_id=case['attack_id'],
                prompt_text=step1_data['prompt_text'],
                ground_truth=case['ground_truth'],
                model=case['model'],
                step1_response=step1_data['response_text'],
                step1_classification=step1_data['classification'],
                step2_observer_model=step2_data['observer_model'],
                step2_neutrosophic_scores=step2_data['scores'],
                step2_detected=step2_data['detected']
            ))

        return examples

    def _get_step1_details(self, attack_id: str, model: str) -> Optional[Dict]:
        """Get Step 1 response details."""
        query = """
        FOR response IN step1_baseline_responses
            FILTER response.attack_id == @attack_id
            FILTER response.target_model == @model
            LIMIT 1
            RETURN {
                prompt_text: response.prompt_text,
                response_text: response.response_text,
                classification: response.compliance_classification
            }
        """

        cursor = self.db.aql.execute(
            query,
            bind_vars={'attack_id': attack_id, 'model': model}
        )

        return next(cursor, None)

    def _get_step2_details(self, attack_id: str) -> Optional[Dict]:
        """Get Step 2 observer evaluation details."""
        query = """
        FOR eval IN step2_pre_evaluations
            FILTER eval.attack_id == @attack_id
            FILTER eval.detected == true
            LIMIT 1
            RETURN {
                observer_model: eval.observer_model,
                scores: eval.neutrosophic_scores,
                detected: eval.detected
            }
        """

        cursor = self.db.aql.execute(
            query,
            bind_vars={'attack_id': attack_id}
        )

        return next(cursor, None)

    def get_compliance_vs_detection_matrix(
        self,
        step1_experiment_id: str = "exp_phase1_step1_baseline_v1",
        step2_experiment_id: str = "exp_phase1_step2_pre_filter_v1"
    ) -> Dict[str, Dict[str, int]]:
        """
        Generate 2x2 matrix of Step 1 compliance vs Step 2 detection.

        Returns:
            Dict: {
                'comply_detected': count,
                'comply_not_detected': count,
                'refuse_detected': count,
                'refuse_not_detected': count
            }
        """
        query = """
        FOR step1 IN step1_baseline_responses
            FILTER step1.experiment_id == @step1_exp

            FOR step2 IN step2_pre_evaluations
                FILTER step2.experiment_id == @step2_exp
                FILTER step2.attack_id == step1.attack_id

                COLLECT
                    step1_classification = step1.compliance_classification,
                    step2_detected = step2.detected
                WITH COUNT INTO count

                RETURN {
                    step1: step1_classification,
                    step2_detected: step2_detected,
                    count: count
                }
        """

        cursor = self.db.aql.execute(
            query,
            bind_vars={
                'step1_exp': step1_experiment_id,
                'step2_exp': step2_experiment_id
            }
        )

        matrix = {
            'comply_detected': 0,
            'comply_not_detected': 0,
            'refuse_detected': 0,
            'refuse_not_detected': 0,
            'unclear_detected': 0,
            'unclear_not_detected': 0
        }

        for result in cursor:
            step1_class = result['step1'] or 'unclear'
            detected = result['step2_detected']
            count = result['count']

            key = f"{step1_class}_{'detected' if detected else 'not_detected'}"
            if key in matrix:
                matrix[key] = count

        return matrix

    def get_model_observer_pairs(
        self,
        step1_experiment_id: str = "exp_phase1_step1_baseline_v1",
        step2_experiment_id: str = "exp_phase1_step2_pre_filter_v1"
    ) -> Dict[str, Dict[str, float]]:
        """
        Analyze paradox rate for each (executor_model, observer_model) pair.

        Returns:
            Dict: {
                'model1': {
                    'observer1': paradox_rate,
                    'observer2': paradox_rate
                },
                ...
            }
        """
        # Get all comply cases with observer detection
        query = """
        FOR step1 IN step1_baseline_responses
            FILTER step1.experiment_id == @step1_exp
            FILTER step1.compliance_classification == "comply"

            FOR step2 IN step2_pre_evaluations
                FILTER step2.experiment_id == @step2_exp
                FILTER step2.attack_id == step1.attack_id

                COLLECT
                    executor = step1.target_model,
                    observer = step2.observer_model,
                    detected = step2.detected
                WITH COUNT INTO count

                RETURN {
                    executor: executor,
                    observer: observer,
                    detected: detected,
                    count: count
                }
        """

        cursor = self.db.aql.execute(
            query,
            bind_vars={
                'step1_exp': step1_experiment_id,
                'step2_exp': step2_experiment_id
            }
        )

        # Build matrix
        pairs = {}
        for result in cursor:
            executor = result['executor']
            observer = result['observer']
            detected = result['detected']
            count = result['count']

            if executor not in pairs:
                pairs[executor] = {'detected': 0, 'not_detected': 0}

            if detected:
                pairs[executor]['detected'] += count
            else:
                pairs[executor]['not_detected'] += count

        # Calculate rates
        rates = {}
        for executor, counts in pairs.items():
            total = counts['detected'] + counts['not_detected']
            rate = (counts['detected'] / total * 100) if total > 0 else 0.0
            rates[executor] = {
                'paradox_rate': rate,
                'comply_detected': counts['detected'],
                'comply_not_detected': counts['not_detected']
            }

        return rates
