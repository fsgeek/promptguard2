#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run cumulative context evaluation on the same 50 sequences for comparison."""

import random
from pathlib import Path
from arango import ArangoClient
import os

from src.pipeline.sequence_loader import SequenceLoader
from src.pipeline.batch_evaluator import BatchEvaluator
from src.database.schemas.phase3_evaluation import EvaluationPrinciple


def main():
    # Use same seed to get same 50 sequences
    random.seed(42)

    # Connect to ArangoDB
    host = os.getenv("ARANGO_HOST", "http://192.168.111.125:8529")
    client = ArangoClient(hosts=host)
    db = client.db(
        os.getenv("ARANGO_DB", "PromptGuard2"),
        username=os.getenv("ARANGO_USER", "pgtest"),
        password=os.getenv("ARANGODB_PROMPTGUARD_PASSWORD"),
    )

    # Load and sample same sequences
    loader = SequenceLoader(db=db)
    all_sequences = loader.load(dataset="xguard_train")
    sampled_sequences = random.sample(all_sequences, 50)

    print(f">> Evaluating 50 sequences with CUMULATIVE CONTEXT mode...")

    evaluator = BatchEvaluator(
        db=db,
        experiment_id="exp_phase3a_cumulative",
        raw_log_path=Path("logs/phase3_cumulative_50_responses.jsonl"),
        use_cumulative_context=True,  # Key difference
    )

    total_turns = 0
    total_cost = 0.0

    for i, sequence in enumerate(sampled_sequences, 1):
        print(f"   [{i}/50] {sequence.attack_id} ({len(sequence.turns)} turns)...")

        result = evaluator.evaluate_sequence(
            sequence=sequence,
            principles=[EvaluationPrinciple.RECIPROCITY],
        )

        if result.success:
            total_turns += len(result.evaluations)
            total_cost += result.total_cost_usd
        else:
            print(f"      !! Failed: {result.error}")

    print(f"\n>> Complete: {total_turns} evaluations, ${total_cost:.4f}")


if __name__ == "__main__":
    main()
