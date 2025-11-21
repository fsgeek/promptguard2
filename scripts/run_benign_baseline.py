#!/usr/bin/env python3
"""
Run Benign Sequence Baseline Evaluation

Task: Evaluate benign sequences in both stateless and cumulative modes to establish
false positive baseline for Phase 4.

Expected results:
- Benign sequences should show low F-scores (reciprocity violations)
- High dyadic T (truth/reciprocity present)
- Low empty-chair F (no third-party harm)

Strategy:
1. Load all 50 benign sequences from database (already stratified by length)
2. Run two experiments:
   - exp_phase4_benign_stateless (use_cumulative_context=False)
   - exp_phase4_benign_cumulative (use_cumulative_context=True)
3. Use RECIPROCITY principle only (matches Phase 3 methodology)
4. Log results to separate log files

Cost estimate: ~$20 total (~500 evaluations × $0.02 per evaluation)
Runtime: 1-2 hours depending on API latency
"""

import os
import random
from pathlib import Path
from datetime import datetime
from arango import ArangoClient

from src.pipeline.sequence_loader import SequenceLoader
from src.pipeline.batch_evaluator import BatchEvaluator
from src.database.schemas.phase3_evaluation import EvaluationPrinciple


def print_banner(text: str):
    """Print formatted banner."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def run_evaluation_mode(
    db,
    sequences,
    experiment_id: str,
    log_filename: str,
    use_cumulative_context: bool
):
    """Run evaluation in specified context mode.

    Args:
        db: ArangoDB database connection
        sequences: List of evaluation sequences
        experiment_id: Experiment identifier
        log_filename: Name of log file (will be placed in logs/)
        use_cumulative_context: Whether to use cumulative context mode

    Returns:
        Dict with summary statistics
    """
    mode_name = "CUMULATIVE" if use_cumulative_context else "STATELESS"
    print_banner(f"Running {mode_name} Mode Evaluation")
    print(f"Experiment ID: {experiment_id}")
    print(f"Log file: logs/{log_filename}")
    print(f"Sequences: {len(sequences)}")
    print(f"Cumulative context: {use_cumulative_context}")

    # Initialize evaluator
    evaluator = BatchEvaluator(
        db=db,
        experiment_id=experiment_id,
        raw_log_path=Path(f"logs/{log_filename}"),
        use_cumulative_context=use_cumulative_context,
    )

    # Track statistics
    total_sequences = len(sequences)
    total_turns = 0
    total_evaluations = 0
    total_cost = 0.0
    failed_sequences = []
    start_time = datetime.now()

    # Evaluate each sequence
    for i, sequence in enumerate(sequences, 1):
        num_turns = len(sequence.turns)
        print(f"[{i}/{total_sequences}] {sequence.attack_id} ({num_turns} turns)...", end=" ")

        result = evaluator.evaluate_sequence(
            sequence=sequence,
            principles=[EvaluationPrinciple.RECIPROCITY],
        )

        if result.success:
            total_turns += num_turns
            total_evaluations += len(result.evaluations)
            total_cost += result.total_cost_usd
            print(f"✓ {len(result.evaluations)} evaluations, ${result.total_cost_usd:.4f}")
        else:
            failed_sequences.append({
                "attack_id": sequence.attack_id,
                "error": result.error
            })
            print(f"✗ FAILED: {result.error}")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Print summary
    print_banner(f"{mode_name} Mode Summary")
    print(f"Total sequences: {total_sequences}")
    print(f"Total turns: {total_turns}")
    print(f"Total evaluations: {total_evaluations}")
    print(f"Failed sequences: {len(failed_sequences)}")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"Avg time per evaluation: {duration/total_evaluations:.2f} seconds")

    if failed_sequences:
        print("\nFailed sequences:")
        for fail in failed_sequences:
            print(f"  - {fail['attack_id']}: {fail['error']}")

    return {
        "mode": mode_name,
        "experiment_id": experiment_id,
        "total_sequences": total_sequences,
        "total_turns": total_turns,
        "total_evaluations": total_evaluations,
        "failed_sequences": len(failed_sequences),
        "total_cost_usd": total_cost,
        "duration_seconds": duration,
        "avg_seconds_per_eval": duration / total_evaluations if total_evaluations > 0 else 0,
    }


def main():
    """Main evaluation routine."""
    print_banner("Benign Sequence Baseline Evaluation")
    print(f"Started at: {datetime.now().isoformat()}")

    # Connect to ArangoDB
    host = os.getenv("ARANGO_HOST", "http://192.168.111.125:8529")
    print(f"Connecting to ArangoDB at {host}...")
    client = ArangoClient(hosts=host)
    db = client.db(
        os.getenv("ARANGO_DB", "PromptGuard2"),
        username=os.getenv("ARANGO_USER", "pgtest"),
        password=os.getenv("ARANGODB_PROMPTGUARD_PASSWORD"),
    )
    print("✓ Connected to database")

    # Load benign sequences
    print("\nLoading benign sequences from database...")
    loader = SequenceLoader(db=db)
    benign_sequences = loader.load(dataset="benign")

    print(f"✓ Loaded {len(benign_sequences)} benign sequences")

    # Print sequence distribution
    turn_distribution = {}
    for seq in benign_sequences:
        num_turns = len(seq.turns)
        turn_distribution[num_turns] = turn_distribution.get(num_turns, 0) + 1

    print("\nSequence distribution by turn count:")
    for num_turns in sorted(turn_distribution.keys()):
        count = turn_distribution[num_turns]
        print(f"  {num_turns} turns: {count} sequences")

    # Calculate expected evaluations
    total_expected_turns = sum(len(seq.turns) for seq in benign_sequences)
    print(f"\nExpected evaluations: {total_expected_turns} (1 principle × {total_expected_turns} turns)")
    print(f"Expected cost per mode: ~${total_expected_turns * 0.0017:.2f}")
    print(f"Expected total cost: ~${2 * total_expected_turns * 0.0017:.2f}")

    # Run stateless evaluation first
    stateless_summary = run_evaluation_mode(
        db=db,
        sequences=benign_sequences,
        experiment_id="exp_phase4_benign_stateless",
        log_filename="benign_baseline_stateless.log",
        use_cumulative_context=False,
    )

    # Run cumulative evaluation second
    cumulative_summary = run_evaluation_mode(
        db=db,
        sequences=benign_sequences,
        experiment_id="exp_phase4_benign_cumulative",
        log_filename="benign_baseline_cumulative.log",
        use_cumulative_context=True,
    )

    # Print final summary
    print_banner("Final Summary - Both Modes")
    print(f"Stateless mode:")
    print(f"  - Evaluations: {stateless_summary['total_evaluations']}")
    print(f"  - Cost: ${stateless_summary['total_cost_usd']:.2f}")
    print(f"  - Duration: {stateless_summary['duration_seconds']/60:.1f} minutes")
    print(f"  - Failed: {stateless_summary['failed_sequences']}")

    print(f"\nCumulative mode:")
    print(f"  - Evaluations: {cumulative_summary['total_evaluations']}")
    print(f"  - Cost: ${cumulative_summary['total_cost_usd']:.2f}")
    print(f"  - Duration: {cumulative_summary['duration_seconds']/60:.1f} minutes")
    print(f"  - Failed: {cumulative_summary['failed_sequences']}")

    print(f"\nTotals:")
    print(f"  - Total evaluations: {stateless_summary['total_evaluations'] + cumulative_summary['total_evaluations']}")
    print(f"  - Total cost: ${stateless_summary['total_cost_usd'] + cumulative_summary['total_cost_usd']:.2f}")
    print(f"  - Total duration: {(stateless_summary['duration_seconds'] + cumulative_summary['duration_seconds'])/60:.1f} minutes")

    print(f"\nCompleted at: {datetime.now().isoformat()}")

    # Write summary to file
    summary_file = Path("logs/benign_baseline_summary.txt")
    with open(summary_file, "w") as f:
        f.write(f"Benign Sequence Baseline Evaluation Summary\n")
        f.write(f"{'=' * 80}\n\n")
        f.write(f"Started: {datetime.now().isoformat()}\n\n")
        f.write(f"Stateless Mode (exp_phase4_benign_stateless):\n")
        f.write(f"  Sequences: {stateless_summary['total_sequences']}\n")
        f.write(f"  Turns: {stateless_summary['total_turns']}\n")
        f.write(f"  Evaluations: {stateless_summary['total_evaluations']}\n")
        f.write(f"  Cost: ${stateless_summary['total_cost_usd']:.2f}\n")
        f.write(f"  Duration: {stateless_summary['duration_seconds']/60:.1f} minutes\n")
        f.write(f"  Failed: {stateless_summary['failed_sequences']}\n\n")
        f.write(f"Cumulative Mode (exp_phase4_benign_cumulative):\n")
        f.write(f"  Sequences: {cumulative_summary['total_sequences']}\n")
        f.write(f"  Turns: {cumulative_summary['total_turns']}\n")
        f.write(f"  Evaluations: {cumulative_summary['total_evaluations']}\n")
        f.write(f"  Cost: ${cumulative_summary['total_cost_usd']:.2f}\n")
        f.write(f"  Duration: {cumulative_summary['duration_seconds']/60:.1f} minutes\n")
        f.write(f"  Failed: {cumulative_summary['failed_sequences']}\n\n")
        f.write(f"Totals:\n")
        f.write(f"  Total evaluations: {stateless_summary['total_evaluations'] + cumulative_summary['total_evaluations']}\n")
        f.write(f"  Total cost: ${stateless_summary['total_cost_usd'] + cumulative_summary['total_cost_usd']:.2f}\n")
        f.write(f"  Total duration: {(stateless_summary['duration_seconds'] + cumulative_summary['duration_seconds'])/60:.1f} minutes\n")

    print(f"\nSummary written to: {summary_file}")

    print_banner("Evaluation Complete")


if __name__ == "__main__":
    main()
