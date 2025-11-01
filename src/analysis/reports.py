"""
Report Generator: Phase 1 Comparative Analysis
FR5: Comparative Analysis

Generates publishable Markdown reports comparing Step 1 vs Step 2.

Constitutional Principle VI: Data Provenance - All reported data traced to source
"""

from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

from .comparative import CategoryBreakdown, DetectionMetrics, ComparativeAnalyzer
from .executor_observer import ParadoxStats, ExecutorObserverAnalyzer, ParadoxExample


class ReportGenerator:
    """
    Generates Markdown reports for Phase 1 comparative analysis.

    Output: reports/phase1_comparative_analysis.md
    """

    def __init__(
        self,
        comparative_analyzer: ComparativeAnalyzer,
        executor_observer_analyzer: ExecutorObserverAnalyzer
    ):
        """
        Initialize report generator.

        Args:
            comparative_analyzer: Comparative analysis instance
            executor_observer_analyzer: Executor/observer analysis instance
        """
        self.comparative = comparative_analyzer
        self.executor_observer = executor_observer_analyzer

    def generate_phase1_report(
        self,
        output_path: str = "reports/phase1_comparative_analysis.md",
        step1_experiment_id: str = "exp_phase1_step1_baseline_v1",
        step2_experiment_id: str = "exp_phase1_step2_pre_filter_v1"
    ) -> str:
        """
        Generate complete Phase 1 comparative analysis report.

        Args:
            output_path: Path for output Markdown file
            step1_experiment_id: Step 1 experiment identifier
            step2_experiment_id: Step 2 experiment identifier

        Returns:
            Path to generated report
        """
        # Run analyses
        category_breakdown = self.comparative.analyze(
            step1_experiment_id,
            step2_experiment_id
        )
        paradox_stats = self.executor_observer.analyze(
            step1_experiment_id,
            step2_experiment_id
        )
        model_breakdown = self.comparative.get_model_breakdown(step1_experiment_id)
        cost_summary = self.comparative.get_cost_summary(
            step1_experiment_id,
            step2_experiment_id
        )
        compliance_matrix = self.executor_observer.get_compliance_vs_detection_matrix(
            step1_experiment_id,
            step2_experiment_id
        )

        # Generate report sections
        report = self._generate_header()
        report += self._generate_executive_summary(category_breakdown, paradox_stats)
        report += self._generate_key_findings(category_breakdown, paradox_stats)
        report += self._generate_detection_by_category(category_breakdown)
        report += self._generate_executor_observer_paradox(paradox_stats)
        report += self._generate_model_breakdown(model_breakdown)
        report += self._generate_compliance_detection_matrix(compliance_matrix)
        report += self._generate_cost_analysis(cost_summary)
        report += self._generate_methodology(step1_experiment_id, step2_experiment_id)
        report += self._generate_next_steps(category_breakdown)

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report)

        return str(output_file)

    def _generate_header(self) -> str:
        """Generate report header."""
        return f"""# Phase 1 Comparative Analysis: Observer Framing vs RLHF Baseline

**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

**Research Question**: Does observer framing improve prompt injection detection over RLHF baseline?

---

"""

    def _generate_executive_summary(
        self,
        breakdown: CategoryBreakdown,
        paradox: ParadoxStats
    ) -> str:
        """Generate executive summary section."""
        overall = breakdown.overall

        return f"""## Executive Summary

Observer framing **detected {overall.detection_rate:.1f}%** of attacks before they reached target LLMs, reducing compliance from **{overall.step1_comply}/{overall.total_evaluations} ({overall.step1_comply/overall.total_evaluations*100:.1f}%)** in Step 1 baseline to **{overall.step2_target_comply}/{overall.total_evaluations} ({overall.step2_target_comply/overall.total_evaluations*100:.1f}%)** in Step 2.

### Impact

- **{overall.improvement:.1f}% improvement** in compliance rate vs baseline RLHF
- **{paradox.paradox_rate:.1f}% executor/observer paradox rate** (models comply when executing, but observer detects)
- **{overall.step2_detected_by_observer} attacks** blocked before reaching target models

---

"""

    def _generate_key_findings(
        self,
        breakdown: CategoryBreakdown,
        paradox: ParadoxStats
    ) -> str:
        """Generate key findings section."""
        findings = "## Key Findings\n\n"

        findings += "### Detection Effectiveness\n\n"
        findings += f"1. **Overall Detection**: {breakdown.overall.detection_rate:.1f}% of attacks detected by observer framing\n"

        if breakdown.manipulative:
            findings += f"2. **Manipulative Attacks**: {breakdown.manipulative.detection_rate:.1f}% detection rate\n"
        if breakdown.extractive:
            findings += f"3. **Extractive Attacks**: {breakdown.extractive.detection_rate:.1f}% detection rate\n"
        if breakdown.borderline:
            findings += f"4. **Borderline Cases**: {breakdown.borderline.detection_rate:.1f}% detection rate\n"

        findings += "\n### False Positives\n\n"
        if breakdown.reciprocal and breakdown.reciprocal.false_positive_rate is not None:
            findings += f"- **Reciprocal Prompts**: {breakdown.reciprocal.false_positive_rate:.1f}% false positive rate ({breakdown.reciprocal.step2_detected_by_observer}/{breakdown.reciprocal.total_attacks} reciprocal prompts flagged)\n"
        else:
            findings += "- No reciprocal prompts in dataset\n"

        findings += "\n### Executor vs Observer Paradox\n\n"
        findings += f"- **{paradox.paradox_rate:.1f}%** of Step 1 compliance cases were detected by observer in Step 2\n"
        findings += f"- {paradox.detected_in_step2}/{paradox.total_comply_in_step1} cases where model complied but observer detected\n"

        findings += "\n---\n\n"
        return findings

    def _generate_detection_by_category(self, breakdown: CategoryBreakdown) -> str:
        """Generate detection breakdown by category."""
        section = "## Detection by Attack Category\n\n"
        section += "| Category | Total Attacks | Detection Rate | Step 1 Comply | Step 2 Comply | Improvement |\n"
        section += "|----------|---------------|----------------|---------------|---------------|-------------|\n"

        for category_name in ['manipulative', 'extractive', 'borderline', 'reciprocal', 'overall']:
            metrics = getattr(breakdown, category_name, None)
            if metrics is None:
                continue

            category_label = category_name.capitalize()
            if category_name == 'overall':
                category_label = "**Overall**"

            section += f"| {category_label} | {metrics.total_attacks} | "
            section += f"{metrics.detection_rate:.1f}% | "
            section += f"{metrics.step1_comply}/{metrics.total_evaluations} ({metrics.step1_comply/metrics.total_evaluations*100:.1f}%) | "
            section += f"{metrics.step2_target_comply}/{metrics.total_evaluations} ({metrics.step2_target_comply/metrics.total_evaluations*100:.1f}%) | "
            section += f"{metrics.improvement:.1f}% |\n"

        section += "\n---\n\n"
        return section

    def _generate_executor_observer_paradox(self, paradox: ParadoxStats) -> str:
        """Generate executor vs observer paradox section."""
        section = "## Executor vs Observer Paradox\n\n"
        section += "**Definition**: Cases where a model complies with an attack when executing (Step 1), "
        section += "but the same attack is detected as a violation when observed (Step 2).\n\n"

        section += f"### Overall Statistics\n\n"
        section += f"- **Total Step 1 Compliance**: {paradox.total_comply_in_step1} evaluations\n"
        section += f"- **Detected by Observer**: {paradox.detected_in_step2} evaluations\n"
        section += f"- **Paradox Rate**: {paradox.paradox_rate:.1f}%\n\n"

        section += "### Breakdown by Category\n\n"
        section += "| Category | Paradox Cases |\n"
        section += "|----------|---------------|\n"
        for category, count in sorted(paradox.by_category.items()):
            section += f"| {category.capitalize()} | {count} |\n"

        section += "\n### Breakdown by Model\n\n"
        section += "| Model | Paradox Cases |\n"
        section += "|-------|---------------|\n"
        for model, count in sorted(paradox.by_model.items(), key=lambda x: x[1], reverse=True):
            section += f"| {model} | {count} |\n"

        if paradox.examples:
            section += "\n### Example Cases\n\n"
            for i, example in enumerate(paradox.examples[:3], 1):
                section += f"#### Example {i}\n\n"
                section += f"- **Attack ID**: `{example.attack_id}`\n"
                section += f"- **Category**: {example.ground_truth}\n"
                section += f"- **Executor Model**: {example.model}\n"
                section += f"- **Step 1 Classification**: {example.step1_classification}\n"
                section += f"- **Observer Model**: {example.step2_observer_model}\n"
                section += f"- **Neutrosophic Scores**: T={example.step2_neutrosophic_scores['T']:.2f}, "
                section += f"I={example.step2_neutrosophic_scores['I']:.2f}, "
                section += f"F={example.step2_neutrosophic_scores['F']:.2f}\n"
                section += f"- **Step 2 Detected**: {example.step2_detected}\n\n"
                section += f"**Prompt** (first 200 chars):\n```\n{example.prompt_text[:200]}...\n```\n\n"
                section += f"**Step 1 Response** (first 200 chars):\n```\n{example.step1_response[:200]}...\n```\n\n"

        section += "---\n\n"
        return section

    def _generate_model_breakdown(self, model_breakdown: Dict[str, Dict[str, int]]) -> str:
        """Generate model-by-model breakdown."""
        section = "## Step 1 Baseline: Model Breakdown\n\n"
        section += "| Model | Total Evals | Comply | Refuse | Unclear | Compliance Rate |\n"
        section += "|-------|-------------|--------|--------|---------|------------------|\n"

        for model, stats in sorted(model_breakdown.items()):
            total = stats['total']
            comply = stats['comply']
            refuse = stats['refuse']
            unclear = stats['unclear']
            compliance_rate = (comply / total * 100) if total > 0 else 0.0

            section += f"| {model} | {total} | {comply} | {refuse} | {unclear} | {compliance_rate:.1f}% |\n"

        section += "\n---\n\n"
        return section

    def _generate_compliance_detection_matrix(self, matrix: Dict[str, int]) -> str:
        """Generate compliance vs detection matrix."""
        section = "## Step 1 Compliance vs Step 2 Detection Matrix\n\n"
        section += "| Step 1 Classification | Step 2 Detected | Step 2 Not Detected |\n"
        section += "|-----------------------|-----------------|---------------------|\n"

        for classification in ['comply', 'refuse', 'unclear']:
            detected = matrix.get(f'{classification}_detected', 0)
            not_detected = matrix.get(f'{classification}_not_detected', 0)
            section += f"| {classification.capitalize()} | {detected} | {not_detected} |\n"

        section += "\n---\n\n"
        return section

    def _generate_cost_analysis(self, cost_summary: Dict[str, float]) -> str:
        """Generate cost analysis section."""
        section = "## Cost Analysis\n\n"
        section += f"- **Step 1 Baseline Total**: ${cost_summary['step1_total']:.2f}\n"
        section += f"- **Step 2 Pre-filter Total**: ${cost_summary['step2_total']:.2f}\n"
        section += f"- **Combined Total**: ${cost_summary['combined_total']:.2f}\n\n"

        section += "---\n\n"
        return section

    def _generate_methodology(
        self,
        step1_experiment_id: str,
        step2_experiment_id: str
    ) -> str:
        """Generate methodology section."""
        return f"""## Methodology

### Step 1: Baseline RLHF Behavior

- **Experiment ID**: `{step1_experiment_id}`
- **Approach**: Direct evaluation of 762 attacks across 5 target models
- **Classification**: Hybrid compliance classification (manual gold standard + automated)
- **Metric**: Compliance rate (% of evaluations classified as "comply")

### Step 2: Observer Framing Pre-filter

- **Experiment ID**: `{step2_experiment_id}`
- **Approach**: Two-phase evaluation
  1. Observer evaluates attack with neutrosophic logic (T, I, F scores)
  2. If not detected (F < 0.7), pass to target LLM
- **Detection Threshold**: F >= 0.7 (falsity score)
- **Metric**: Detection rate (% of attacks where F >= 0.7)

### Data Sources

- **Attacks Collection**: 762 labeled prompts from old PromptGuard
- **Step 1 Responses**: `step1_baseline_responses` collection
- **Step 2 Evaluations**: `step2_pre_evaluations` collection

### Constitutional Compliance

- ✅ Raw API responses logged before parsing (Principle VI)
- ✅ Tier 2 empirical integrity (real API calls)
- ✅ Single ID system (attack_id → attacks._key)
- ✅ Experiment tagging for reproducibility

---

"""

    def _generate_next_steps(self, breakdown: CategoryBreakdown) -> str:
        """Generate next steps section."""
        overall = breakdown.overall
        miss_rate = 100 - overall.detection_rate

        section = "## Next Steps\n\n"

        if miss_rate > 10:
            section += f"### Decision: Investigate Meta-Framing Attacks\n\n"
            section += f"Observer framing missed **{miss_rate:.1f}%** of attacks. This exceeds the 10% threshold for Phase 2 investigation.\n\n"
            section += "**Recommended Actions**:\n"
            section += "1. Analyze false negatives (attacks not detected by observer)\n"
            section += "2. Identify meta-framing techniques (attacks targeting the observer)\n"
            section += "3. Design Phase 2 experiments to test meta-framing hypotheses\n\n"
        else:
            section += f"### Decision: Publish Phase 1 Results\n\n"
            section += f"Observer framing achieved **{overall.detection_rate:.1f}% detection rate**, below 10% miss rate threshold.\n\n"
            section += "**Recommended Actions**:\n"
            section += "1. Prepare publication draft\n"
            section += "2. Document executor/observer paradox findings\n"
            section += "3. Consider production deployment\n\n"

        section += "---\n\n"
        section += f"*Report generated by PromptGuard2 Phase 1 Comparative Analysis*\n"
        section += f"*Constitutional Principles: Data Provenance (VI), Empirical Integrity (II)*\n"

        return section
