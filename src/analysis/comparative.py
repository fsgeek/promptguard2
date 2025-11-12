"""
Comparative Analysis: Step 1 vs Step 2
FR5: Comparative Analysis

Compares baseline RLHF behavior (Step 1) against observer pre-filtering (Step 2).

Constitutional Principle VI: Data Provenance - All metrics derived from raw stored data
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
from arango.database import StandardDatabase


@dataclass
class DetectionMetrics:
    """Detection metrics for a given category or overall."""
    total_attacks: int
    total_evaluations: int  # total_attacks × num_models

    # Step 1: Baseline compliance
    step1_comply: int
    step1_refuse: int
    step1_unclear: int

    # Step 2: Pre-filter detection
    step2_detected_by_observer: int
    step2_passed_to_target: int
    step2_target_comply: int
    step2_target_refuse: int
    step2_target_unclear: int

    # Comparative metrics (calculated in __post_init__)
    detection_rate: float = 0.0  # % attacks detected by observer
    false_positive_rate: Optional[float] = None  # For reciprocal prompts only
    improvement: float = 0.0  # % reduction in compliance vs Step 1

    def __post_init__(self):
        """Calculate derived metrics."""
        # Detection rate: % of attacks where observer detected (F >= 0.7)
        self.detection_rate = (self.step2_detected_by_observer / self.total_attacks * 100) if self.total_attacks > 0 else 0.0

        # Improvement: reduction in compliance rate
        step1_compliance_rate = (self.step1_comply / self.total_evaluations * 100) if self.total_evaluations > 0 else 0.0
        step2_compliance_rate = (self.step2_target_comply / self.total_evaluations * 100) if self.total_evaluations > 0 else 0.0
        self.improvement = step1_compliance_rate - step2_compliance_rate


@dataclass
class CategoryBreakdown:
    """Breakdown by attack category (ground_truth)."""
    manipulative: DetectionMetrics
    extractive: DetectionMetrics
    borderline: DetectionMetrics
    reciprocal: DetectionMetrics
    overall: DetectionMetrics


class ComparativeAnalyzer:
    """
    Analyzes Step 1 baseline vs Step 2 pre-filter detection.

    Answers:
    - What % of attacks does observer framing detect?
    - How much does it reduce compliance vs baseline RLHF?
    - Does effectiveness vary by attack category?
    - What is the false positive rate on reciprocal prompts?
    """

    def __init__(self, db: StandardDatabase):
        """
        Initialize comparative analyzer.

        Args:
            db: ArangoDB database connection
        """
        self.db = db
        self.step1_collection = db.collection("step1_baseline_responses")
        self.step2_collection = db.collection("step2_pre_evaluations")
        self.attacks_collection = db.collection("attacks")

    def analyze(
        self,
        step1_experiment_id: str = "exp_phase1_step1_baseline_v1",
        step2_experiment_id: str = "exp_phase1_step2_pre_filter_v1"
    ) -> CategoryBreakdown:
        """
        Generate comparative analysis metrics.

        Args:
            step1_experiment_id: Step 1 experiment identifier
            step2_experiment_id: Step 2 experiment identifier

        Returns:
            CategoryBreakdown with metrics by category and overall
        """
        # Get all attacks with ground truth labels
        attacks = self._get_attacks()

        # Group attacks by category
        attacks_by_category = self._group_by_category(attacks)

        # Analyze each category
        results = {}
        for category, attack_ids in attacks_by_category.items():
            results[category] = self._analyze_category(
                attack_ids,
                step1_experiment_id,
                step2_experiment_id
            )

        # Calculate overall metrics
        results['overall'] = self._analyze_category(
            [a['_key'] for a in attacks],
            step1_experiment_id,
            step2_experiment_id
        )

        # Calculate false positive rate (reciprocal prompts only)
        if 'reciprocal' in results:
            results['reciprocal'].false_positive_rate = results['reciprocal'].detection_rate

        return CategoryBreakdown(
            manipulative=results.get('manipulative'),
            extractive=results.get('extractive'),
            borderline=results.get('borderline'),
            reciprocal=results.get('reciprocal'),
            overall=results['overall']
        )

    def _get_attacks(self) -> List[Dict]:
        """Fetch all attacks from database."""
        cursor = self.db.aql.execute(
            """
            FOR attack IN attacks
                RETURN {
                    _key: attack._key,
                    ground_truth: attack.ground_truth
                }
            """
        )
        return list(cursor)

    def _group_by_category(self, attacks: List[Dict]) -> Dict[str, List[str]]:
        """Group attack IDs by ground_truth category."""
        grouped = defaultdict(list)
        for attack in attacks:
            grouped[attack['ground_truth']].append(attack['_key'])
        return grouped

    def _analyze_category(
        self,
        attack_ids: List[str],
        step1_experiment_id: str,
        step2_experiment_id: str
    ) -> DetectionMetrics:
        """
        Analyze detection metrics for a specific category.

        Args:
            attack_ids: List of attack IDs in this category
            step1_experiment_id: Step 1 experiment ID
            step2_experiment_id: Step 2 experiment ID

        Returns:
            DetectionMetrics for this category
        """
        # Step 1: Count compliance classifications
        step1_stats = self._get_step1_stats(attack_ids, step1_experiment_id)

        # Step 2: Count detection and compliance for passed attacks
        step2_stats = self._get_step2_stats(attack_ids, step2_experiment_id)

        return DetectionMetrics(
            total_attacks=len(attack_ids),
            total_evaluations=step1_stats['total'],
            step1_comply=step1_stats['comply'],
            step1_refuse=step1_stats['refuse'],
            step1_unclear=step1_stats['unclear'],
            step2_detected_by_observer=step2_stats['detected'],
            step2_passed_to_target=step2_stats['passed'],
            step2_target_comply=step2_stats['comply'],
            step2_target_refuse=step2_stats['refuse'],
            step2_target_unclear=step2_stats['unclear']
        )

    def _get_step1_stats(self, attack_ids: List[str], experiment_id: str) -> Dict[str, int]:
        """
        Get Step 1 baseline compliance statistics.

        Returns:
            Dict with counts: {total, comply, refuse, unclear}
        """
        query = """
        FOR response IN step1_baseline_responses
            FILTER response.attack_id IN @attack_ids
            FILTER response.experiment_id == @experiment_id
            COLLECT classification = response.compliance_classification WITH COUNT INTO count
            RETURN {classification: classification, count: count}
        """

        cursor = self.db.aql.execute(
            query,
            bind_vars={
                'attack_ids': attack_ids,
                'experiment_id': experiment_id
            }
        )

        stats = {'total': 0, 'comply': 0, 'refuse': 0, 'unclear': 0}
        for result in cursor:
            classification = result['classification'] or 'unclear'
            count = result['count']
            stats[classification] = count
            stats['total'] += count

        return stats

    def _get_step2_stats(self, attack_ids: List[str], experiment_id: str) -> Dict[str, int]:
        """
        Get Step 2 pre-filter detection and compliance statistics.

        Returns:
            Dict with counts: {detected, passed, comply, refuse, unclear}
        """
        query = """
        FOR eval IN step2_pre_evaluations
            FILTER eval.attack_id IN @attack_ids
            FILTER eval.experiment_id == @experiment_id
            COLLECT
                detected = eval.detected,
                classification = eval.compliance_classification
            WITH COUNT INTO count
            RETURN {
                detected: detected,
                classification: classification,
                count: count
            }
        """

        cursor = self.db.aql.execute(
            query,
            bind_vars={
                'attack_ids': attack_ids,
                'experiment_id': experiment_id
            }
        )

        stats = {
            'detected': 0,
            'passed': 0,
            'comply': 0,
            'refuse': 0,
            'unclear': 0
        }

        for result in cursor:
            count = result['count']

            if result['detected']:
                stats['detected'] += count
            else:
                stats['passed'] += count
                classification = result['classification'] or 'unclear'
                # Handle unexpected classification values by treating them as 'unclear'
                if classification not in stats:
                    classification = 'unclear'
                stats[classification] += count

        return stats

    def get_model_breakdown(
        self,
        step1_experiment_id: str = "exp_phase1_step1_baseline_v1"
    ) -> Dict[str, Dict[str, int]]:
        """
        Get compliance breakdown by model for Step 1 baseline.

        Args:
            step1_experiment_id: Step 1 experiment identifier

        Returns:
            Dict mapping model -> {comply, refuse, unclear, total}
        """
        query = """
        FOR response IN step1_baseline_responses
            FILTER response.experiment_id == @experiment_id
            COLLECT
                model = response.target_model,
                classification = response.compliance_classification
            WITH COUNT INTO count
            RETURN {
                model: model,
                classification: classification,
                count: count
            }
        """

        cursor = self.db.aql.execute(
            query,
            bind_vars={'experiment_id': step1_experiment_id}
        )

        breakdown = defaultdict(lambda: {'comply': 0, 'refuse': 0, 'unclear': 0, 'total': 0})

        for result in cursor:
            model = result['model']
            classification = result['classification'] or 'unclear'
            count = result['count']

            breakdown[model][classification] = count
            breakdown[model]['total'] += count

        return dict(breakdown)

    def get_cost_summary(
        self,
        step1_experiment_id: str = "exp_phase1_step1_baseline_v1",
        step2_experiment_id: str = "exp_phase1_step2_pre_filter_v1"
    ) -> Dict[str, float]:
        """
        Calculate total costs for Step 1 and Step 2.

        Args:
            step1_experiment_id: Step 1 experiment identifier
            step2_experiment_id: Step 2 experiment identifier

        Returns:
            Dict with {step1_total, step2_total, combined_total}
        """
        # Step 1 cost
        step1_cursor = self.db.aql.execute(
            """
            FOR response IN step1_baseline_responses
                FILTER response.experiment_id == @experiment_id
                COLLECT AGGREGATE total_cost = SUM(response.cost_usd)
                RETURN total_cost
            """,
            bind_vars={'experiment_id': step1_experiment_id}
        )
        step1_cost = next(step1_cursor, 0.0) or 0.0

        # Step 2 cost (observer + target)
        step2_cursor = self.db.aql.execute(
            """
            FOR eval IN step2_pre_evaluations
                FILTER eval.experiment_id == @experiment_id
                COLLECT AGGREGATE
                    total_observer = SUM(eval.cost_observer),
                    total_target = SUM(eval.cost_target)
                RETURN {observer: total_observer, target: total_target}
            """,
            bind_vars={'experiment_id': step2_experiment_id}
        )
        step2_costs = next(step2_cursor, {'observer': 0.0, 'target': 0.0})
        step2_cost = (step2_costs['observer'] or 0.0) + (step2_costs['target'] or 0.0)

        return {
            'step1_total': step1_cost,
            'step2_total': step2_cost,
            'combined_total': step1_cost + step2_cost
        }
