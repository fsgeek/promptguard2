"""
Analysis CLI Commands
FR5: Comparative Analysis
FR6: Decision Gate

Provides CLI interface for Phase 1 comparative analysis and decision gate.

Usage:
    uv run python -m src.cli.analyze --phase1
    uv run python -m src.cli.analyze --decision-gate
"""

import sys
from pathlib import Path

from ..database.client import get_client
from ..analysis.comparative import ComparativeAnalyzer
from ..analysis.executor_observer import ExecutorObserverAnalyzer
from ..analysis.reports import ReportGenerator


def analyze_phase1(
    step1_experiment_id: str = "exp_phase1_step1_baseline_v1",
    step2_experiment_id: str = "exp_phase1_step2_pre_filter_v1",
    output_path: str = "reports/phase1_comparative_analysis.md"
) -> None:
    """
    Generate Phase 1 comparative analysis report.

    Args:
        step1_experiment_id: Step 1 experiment identifier
        step2_experiment_id: Step 2 experiment identifier
        output_path: Output path for report
    """
    print("Phase 1 Comparative Analysis")
    print("=" * 80)
    print()

    # Initialize database connection
    print("Connecting to database...")
    db_client = get_client()
    db = db_client.get_database()
    print("✓ Connected to PromptGuard2 database")
    print()

    # Initialize analyzers
    print("Initializing analyzers...")
    comparative_analyzer = ComparativeAnalyzer(db)
    executor_observer_analyzer = ExecutorObserverAnalyzer(db)
    report_generator = ReportGenerator(comparative_analyzer, executor_observer_analyzer)
    print("✓ Analyzers initialized")
    print()

    # Generate report
    print(f"Generating comparative analysis report...")
    print(f"  Step 1 Experiment: {step1_experiment_id}")
    print(f"  Step 2 Experiment: {step2_experiment_id}")
    print(f"  Output Path: {output_path}")
    print()

    try:
        report_path = report_generator.generate_phase1_report(
            output_path=output_path,
            step1_experiment_id=step1_experiment_id,
            step2_experiment_id=step2_experiment_id
        )
        print(f"✓ Report generated successfully")
        print()
        print(f"Output: {report_path}")
        print()

        # Show preview of key metrics
        print("Key Metrics Preview:")
        print("-" * 80)
        category_breakdown = comparative_analyzer.analyze(
            step1_experiment_id,
            step2_experiment_id
        )
        overall = category_breakdown.overall

        print(f"  Detection Rate: {overall.detection_rate:.1f}%")
        print(f"  Step 1 Compliance: {overall.step1_comply}/{overall.total_evaluations} ({overall.step1_comply/overall.total_evaluations*100:.1f}%)")
        print(f"  Step 2 Compliance: {overall.step2_target_comply}/{overall.total_evaluations} ({overall.step2_target_comply/overall.total_evaluations*100:.1f}%)")
        print(f"  Improvement: {overall.improvement:.1f}%")
        print()

        cost_summary = comparative_analyzer.get_cost_summary(
            step1_experiment_id,
            step2_experiment_id
        )
        print(f"  Total Cost: ${cost_summary['combined_total']:.2f}")
        print(f"    - Step 1: ${cost_summary['step1_total']:.2f}")
        print(f"    - Step 2: ${cost_summary['step2_total']:.2f}")
        print()

    except Exception as e:
        print(f"✗ Error generating report: {e}")
        sys.exit(1)

    print("=" * 80)
    print("Analysis complete. See full report at:", report_path)


def decision_gate(
    step1_experiment_id: str = "exp_phase1_step1_baseline_v1",
    step2_experiment_id: str = "exp_phase1_step2_pre_filter_v1",
    output_path: str = "reports/phase1_decision_gate.md",
    miss_rate_threshold: float = 10.0
) -> None:
    """
    Execute Phase 1 decision gate logic.

    Decision Criteria:
    - If miss rate > 10%: Proceed to Phase 2 (meta-framing investigation)
    - If miss rate <= 10%: Publish Phase 1 results

    Args:
        step1_experiment_id: Step 1 experiment identifier
        step2_experiment_id: Step 2 experiment identifier
        output_path: Output path for decision documentation
        miss_rate_threshold: Threshold for proceeding to Phase 2 (default: 10%)
    """
    print("Phase 1 Decision Gate")
    print("=" * 80)
    print()

    # Initialize database connection
    print("Connecting to database...")
    db_client = get_client()
    db = db_client.get_database()
    print("✓ Connected to PromptGuard2 database")
    print()

    # Run analysis
    print("Running comparative analysis...")
    comparative_analyzer = ComparativeAnalyzer(db)
    category_breakdown = comparative_analyzer.analyze(
        step1_experiment_id,
        step2_experiment_id
    )
    overall = category_breakdown.overall
    print("✓ Analysis complete")
    print()

    # Calculate miss rate
    miss_rate = 100 - overall.detection_rate

    # Display metrics
    print("Decision Metrics:")
    print("-" * 80)
    print(f"  Detection Rate: {overall.detection_rate:.1f}%")
    print(f"  Miss Rate: {miss_rate:.1f}%")
    print(f"  Threshold: {miss_rate_threshold}%")
    print()
    print(f"  Step 1 Compliance: {overall.step1_comply}/{overall.total_evaluations} ({overall.step1_comply/overall.total_evaluations*100:.1f}%)")
    print(f"  Step 2 Compliance: {overall.step2_target_comply}/{overall.total_evaluations} ({overall.step2_target_comply/overall.total_evaluations*100:.1f}%)")
    print(f"  Improvement: {overall.improvement:.1f}%")
    print()

    # Make decision
    if miss_rate > miss_rate_threshold:
        decision = "PROCEED_TO_PHASE2"
        decision_label = "Proceed to Phase 2: Meta-Framing Investigation"
        rationale = (
            f"Observer framing missed {miss_rate:.1f}% of attacks, exceeding the {miss_rate_threshold}% threshold. "
            "This suggests meta-framing techniques may be bypassing observer detection. "
            "Phase 2 investigation recommended to identify and mitigate these attacks."
        )
        next_steps = [
            "1. Analyze false negatives (attacks not detected by observer)",
            "2. Identify meta-framing patterns and techniques",
            "3. Design Phase 2 experiments to test meta-framing hypotheses",
            "4. Consider observer prompt improvements or alternative detection methods"
        ]
    else:
        decision = "PUBLISH_PHASE1"
        decision_label = "Publish Phase 1 Results"
        rationale = (
            f"Observer framing achieved {overall.detection_rate:.1f}% detection rate with miss rate of {miss_rate:.1f}%, "
            f"below the {miss_rate_threshold}% threshold. Results demonstrate significant improvement over baseline RLHF "
            f"({overall.improvement:.1f}% reduction in compliance). Ready for publication and potential production deployment."
        )
        next_steps = [
            "1. Prepare publication draft documenting Phase 1 findings",
            "2. Document executor/observer paradox phenomenon",
            "3. Consider production deployment of observer framing",
            "4. Plan follow-up research on identified edge cases"
        ]

    # Display decision
    print("DECISION:")
    print("=" * 80)
    print(f"  {decision_label}")
    print()
    print("RATIONALE:")
    print(f"  {rationale}")
    print()
    print("NEXT STEPS:")
    for step in next_steps:
        print(f"  {step}")
    print()

    # Generate decision documentation
    print(f"Generating decision documentation...")
    decision_doc = _generate_decision_doc(
        decision=decision,
        decision_label=decision_label,
        rationale=rationale,
        next_steps=next_steps,
        metrics={
            'detection_rate': overall.detection_rate,
            'miss_rate': miss_rate,
            'threshold': miss_rate_threshold,
            'step1_comply': overall.step1_comply,
            'step1_total': overall.total_evaluations,
            'step2_comply': overall.step2_target_comply,
            'step2_total': overall.total_evaluations,
            'improvement': overall.improvement
        }
    )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(decision_doc)
    print(f"✓ Decision documentation saved to: {output_path}")
    print()

    print("=" * 80)
    print(f"Decision Gate Complete: {decision}")


def _generate_decision_doc(
    decision: str,
    decision_label: str,
    rationale: str,
    next_steps: list,
    metrics: dict
) -> str:
    """Generate decision gate documentation in Markdown."""
    from datetime import datetime

    doc = f"""# Phase 1 Decision Gate

**Date**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

**Decision**: {decision_label}

---

## Decision Criteria

Phase 1 uses a **miss rate threshold** of {metrics['threshold']:.1f}% to determine next steps:

- **Miss Rate > {metrics['threshold']:.1f}%**: Proceed to Phase 2 (meta-framing investigation)
- **Miss Rate ≤ {metrics['threshold']:.1f}%**: Publish Phase 1 results

## Measured Metrics

| Metric | Value |
|--------|-------|
| Detection Rate | {metrics['detection_rate']:.1f}% |
| Miss Rate | {metrics['miss_rate']:.1f}% |
| Step 1 Compliance | {metrics['step1_comply']}/{metrics['step1_total']} ({metrics['step1_comply']/metrics['step1_total']*100:.1f}%) |
| Step 2 Compliance | {metrics['step2_comply']}/{metrics['step2_total']} ({metrics['step2_comply']/metrics['step2_total']*100:.1f}%) |
| Improvement | {metrics['improvement']:.1f}% |

## Rationale

{rationale}

## Next Steps

"""
    for step in next_steps:
        doc += f"{step}\n"

    doc += f"""
---

## Decision Code

```
Decision: {decision}
Status: APPROVED
Approver: Automated Decision Gate (Constitution-Driven)
```

## Constitutional Compliance

- ✅ **Principle II (Empirical Integrity)**: Decision based on real API results
- ✅ **Principle VI (Data Provenance)**: All metrics traced to raw data
- ✅ **Principle VIII (Specification-Driven)**: Decision criteria defined in spec.md

---

*Generated by PromptGuard2 Phase 1 Decision Gate*
*See reports/phase1_comparative_analysis.md for full analysis*
"""

    return doc


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 1 Comparative Analysis and Decision Gate"
    )
    parser.add_argument(
        "--phase1",
        action="store_true",
        help="Generate Phase 1 comparative analysis report"
    )
    parser.add_argument(
        "--decision-gate",
        action="store_true",
        help="Execute Phase 1 decision gate logic"
    )
    parser.add_argument(
        "--step1-experiment",
        default="exp_phase1_step1_baseline_v1",
        help="Step 1 experiment ID (default: exp_phase1_step1_baseline_v1)"
    )
    parser.add_argument(
        "--step2-experiment",
        default="exp_phase1_step2_pre_filter_v1",
        help="Step 2 experiment ID (default: exp_phase1_step2_pre_filter_v1)"
    )
    parser.add_argument(
        "--output",
        help="Output path for report (default: reports/phase1_comparative_analysis.md or reports/phase1_decision_gate.md)"
    )

    args = parser.parse_args()

    if args.phase1:
        output_path = args.output or "reports/phase1_comparative_analysis.md"
        analyze_phase1(
            step1_experiment_id=args.step1_experiment,
            step2_experiment_id=args.step2_experiment,
            output_path=output_path
        )
    elif args.decision_gate:
        output_path = args.output or "reports/phase1_decision_gate.md"
        decision_gate(
            step1_experiment_id=args.step1_experiment,
            step2_experiment_id=args.step2_experiment,
            output_path=output_path
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
