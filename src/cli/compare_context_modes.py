#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare stateless vs cumulative context evaluation modes.

This script runs a 50-sequence sample comparison to determine whether
cumulative conversation context improves attack detection.

Usage:
    uv run python src/cli/compare_context_modes.py --sample 50

Outputs:
    - Cumulative context evaluations (experiment_id: exp_phase3a_cumulative)
    - Comparison analysis showing F score differences
"""

import argparse
import os
import random
from pathlib import Path
from arango import ArangoClient

from src.pipeline.sequence_loader import SequenceLoader
from src.pipeline.batch_evaluator import BatchEvaluator
from src.database.schemas.phase3_evaluation import EvaluationPrinciple


def main():
    parser = argparse.ArgumentParser(description="Compare stateless vs cumulative context modes")
    parser.add_argument(
        "--sample",
        type=int,
        default=50,
        help="Number of sequences to test (default: 50)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )

    args = parser.parse_args()

    # Set random seed for reproducibility
    random.seed(args.seed)

    # Connect to ArangoDB
    host = os.getenv("ARANGO_HOST", "http://192.168.111.125:8529")
    client = ArangoClient(hosts=host)
    db = client.db(
        os.getenv("ARANGO_DB", "PromptGuard2"),
        username=os.getenv("ARANGO_USER", "pgtest"),
        password=os.getenv("ARANGODB_PROMPTGUARD_PASSWORD"),
    )

    print(f"\n{'='*60}")
    print(f"Context Mode Comparison: Stateless vs Cumulative")
    print(f"{'='*60}\n")
    print(f"Sample size: {args.sample} sequences")
    print(f"Random seed: {args.seed}\n")

    # Step 1: Load XGuard sequences and sample randomly
    print(f">> Loading XGuard sequences...")
    loader = SequenceLoader(db=db)
    all_sequences = loader.load(dataset="xguard_train")

    # Random sample
    sampled_sequences = random.sample(all_sequences, min(args.sample, len(all_sequences)))
    print(f"   Loaded {len(all_sequences)} total sequences")
    print(f"   Sampled {len(sampled_sequences)} sequences randomly\n")

    # Step 2: Evaluate with cumulative context
    print(f">> Evaluating {len(sampled_sequences)} sequences with CUMULATIVE CONTEXT...")
    evaluator_cumulative = BatchEvaluator(
        db=db,
        experiment_id="exp_phase3a_cumulative",
        raw_log_path=Path("logs/phase3_cumulative_responses.jsonl"),
        use_cumulative_context=True,
    )

    total_turns = 0
    total_cost = 0.0

    for i, sequence in enumerate(sampled_sequences, 1):
        print(f"   [{i}/{len(sampled_sequences)}] {sequence.attack_id} ({len(sequence.turns)} turns)...")

        result = evaluator_cumulative.evaluate_sequence(
            sequence=sequence,
            principles=[EvaluationPrinciple.RECIPROCITY],
        )

        if result.success:
            total_turns += len(result.evaluations)
            total_cost += result.total_cost_usd
        else:
            print(f"      !! Evaluation failed: {result.error}")

    print(f"\n>> Cumulative evaluation complete: {total_turns} turn evaluations")
    print(f"   Cost: ${total_cost:.4f}\n")

    # Step 3: Compare results
    print(f">> Comparing stateless vs cumulative results...")

    # Query stateless results (from exp_phase3a_mvp)
    coll = db.collection('phase3_principle_evaluations')

    comparison_count = 0
    f_score_increases = 0
    f_score_decreases = 0
    total_f_delta = 0.0

    for seq in sampled_sequences:
        # Get stateless evals
        stateless_evals = list(coll.find({
            'attack_id': seq.attack_id,
            'experiment_id': 'exp_phase3a_mvp'
        }))

        # Get cumulative evals
        cumulative_evals = list(coll.find({
            'attack_id': seq.attack_id,
            'experiment_id': 'exp_phase3a_cumulative'
        }))

        if not stateless_evals or not cumulative_evals:
            continue

        # Compare F scores for each turn
        for stateless in stateless_evals:
            turn_num = stateless['turn_number']
            cumulative = next((e for e in cumulative_evals if e['turn_number'] == turn_num), None)

            if cumulative:
                f_delta = cumulative['scores']['F'] - stateless['scores']['F']
                total_f_delta += f_delta
                comparison_count += 1

                if f_delta > 0.05:  # Meaningful increase
                    f_score_increases += 1
                elif f_delta < -0.05:  # Meaningful decrease
                    f_score_decreases += 1

    if comparison_count > 0:
        avg_f_delta = total_f_delta / comparison_count
        print(f"   Comparisons: {comparison_count} turn evaluations")
        print(f"   Average ΔF: {avg_f_delta:+.3f}")
        print(f"   F increased: {f_score_increases} ({f_score_increases/comparison_count*100:.1f}%)")
        print(f"   F decreased: {f_score_decreases} ({f_score_decreases/comparison_count*100:.1f}%)")
        print(f"   F unchanged: {comparison_count - f_score_increases - f_score_decreases}\n")

        # Interpretation
        print(f"{'='*60}")
        print(f"INTERPRETATION")
        print(f"{'='*60}")
        if avg_f_delta > 0.1:
            print(f"✓ Cumulative context SIGNIFICANTLY increases F scores")
            print(f"  → Use cumulative context for full validation")
        elif avg_f_delta > 0.05:
            print(f"? Cumulative context MODERATELY increases F scores")
            print(f"  → Consider cumulative context, but effect is modest")
        elif avg_f_delta < -0.05:
            print(f"✗ Cumulative context DECREASES F scores (unexpected)")
            print(f"  → Use stateless evaluation")
        else:
            print(f"○ Cumulative context has NO SIGNIFICANT EFFECT")
            print(f"  → Use stateless evaluation (simpler, faster)")
        print(f"{'='*60}\n")
    else:
        print(f"   !! No comparisons possible (missing stateless data)")


if __name__ == "__main__":
    main()
