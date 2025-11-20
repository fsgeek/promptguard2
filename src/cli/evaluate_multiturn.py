#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI for evaluating multi-turn attack sequences (Phase 3 MVP).

Usage:
    uv run python src/cli/evaluate_multiturn.py --dataset xguard_train --sample 10 --detector trust_ema

Outputs:
    - Evaluation summary with detection results
    - Cost tracking
    - Detection rate statistics
"""

import argparse
import os
from pathlib import Path
from arango import ArangoClient

from src.pipeline.sequence_loader import SequenceLoader
from src.pipeline.batch_evaluator import BatchEvaluator
from src.pipeline.trajectory_analyzer import TrajectoryAnalyzer
from src.database.schemas.phase3_evaluation import EvaluationPrinciple


def main():
    parser = argparse.ArgumentParser(description="Evaluate multi-turn attack sequences")
    parser.add_argument(
        "--dataset",
        required=True,
        choices=["xguard_train", "mhj", "benign"],
        help="Dataset to evaluate",
    )
    parser.add_argument(
        "--sample",
        type=int,
        help="Limit to first N sequences (optional)",
    )
    parser.add_argument(
        "--detector",
        default="trust_ema",
        help="Detector to use (default: trust_ema)",
    )
    parser.add_argument(
        "--experiment-id",
        default="exp_phase3a_mvp",
        help="Experiment ID for provenance",
    )

    args = parser.parse_args()

    # Connect to ArangoDB
    host = os.getenv("ARANGO_HOST", "http://192.168.111.125:8529")
    client = ArangoClient(hosts=host)
    db = client.db(
        os.getenv("ARANGO_DB", "PromptGuard2"),
        username=os.getenv("ARANGO_USER", "pgtest"),
        password=os.getenv("ARANGODB_PROMPTGUARD_PASSWORD"),
    )

    print(f"\n{'='*60}")
    print(f"Phase 3 MVP: Multi-Turn Attack Evaluation")
    print(f"{'='*60}\n")

    # Step 1: Load sequences
    print(f">> Loading sequences from {args.dataset}...")
    loader = SequenceLoader(db=db)
    sequences = loader.load(dataset=args.dataset, sample=args.sample)
    print(f"   Loaded {len(sequences)} sequences\n")

    # Step 2: Evaluate sequences
    print(f">> Evaluating with observer v2.1-c...")
    evaluator = BatchEvaluator(
        db=db,
        experiment_id=args.experiment_id,
        raw_log_path=Path("logs/phase3_raw_responses.jsonl"),
    )

    total_turns = 0
    total_cost = 0.0

    for i, sequence in enumerate(sequences, 1):
        print(f"   [{i}/{len(sequences)}] Evaluating {sequence.attack_id} ({len(sequence.turns)} turns)...")

        result = evaluator.evaluate_sequence(
            sequence=sequence,
            principles=[EvaluationPrinciple.RECIPROCITY],
        )

        if result.success:
            total_turns += len(result.evaluations)
            total_cost += result.total_cost_usd
        else:
            print(f"      !! Evaluation failed: {result.error}")

    print(f"\n>> Evaluation complete: {total_turns} turn evaluations\n")

    # Step 3: Analyze trajectories
    print(f">> Analyzing trajectories with {args.detector} detector...")
    analyzer = TrajectoryAnalyzer(db=db)

    attacks_detected = 0
    for sequence in sequences:
        detection_results = analyzer.analyze(
            attack_id=sequence.attack_id,
            detector_name=args.detector,
        )

        # Check if any principle detected attack
        if any(result.attack_detected for result in detection_results.values()):
            attacks_detected += 1

    print(f"   Attacks detected: {attacks_detected}/{len(sequences)} ({attacks_detected/len(sequences)*100:.1f}%)\n")

    # Step 4: Print summary
    print(f"\n{'='*60}")
    print(f">> Evaluation Summary")
    print(f"{'='*60}")
    print(f"   Sequences: {len(sequences)}")
    print(f"   Turns: {total_turns} (avg {total_turns/len(sequences):.1f} per sequence)")
    print(f"   Principles: 1 (reciprocity)")
    print(f"   Total evaluations: {total_turns}")
    print(f"\n>> Cost: ${total_cost:.4f} ({total_turns} API calls, haiku model)")
    print(f"\n>> Detection Results:")
    print(f"   Attacks detected: {attacks_detected}/{len(sequences)} ({attacks_detected/len(sequences)*100:.1f}%)")
    print(f"   Detection by principle:")
    print(f"     - reciprocity: {attacks_detected}/{len(sequences)}")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
