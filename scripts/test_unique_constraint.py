#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test that unique constraint prevents duplicate evaluations."""

import os
from arango import ArangoClient
from src.pipeline.batch_evaluator import BatchEvaluator
from src.pipeline.sequence_loader import SequenceLoader
from src.database.schemas.phase3_evaluation import EvaluationPrinciple
from pathlib import Path


def main():
    # Connect to ArangoDB
    host = os.getenv("ARANGO_HOST", "http://192.168.111.125:8529")
    client = ArangoClient(hosts=host)
    db = client.db(
        os.getenv("ARANGO_DB", "PromptGuard2"),
        username=os.getenv("ARANGO_USER", "pgtest"),
        password=os.getenv("ARANGODB_PROMPTGUARD_PASSWORD"),
    )

    print("Testing unique constraint...")
    print()

    # Load sequences and take first one
    loader = SequenceLoader(db=db)
    all_sequences = loader.load(dataset="xguard_train")
    sequences = [all_sequences[0]] if all_sequences else []

    if not sequences:
        print("✗ No sequences found")
        return

    sequence = sequences[0]
    print(f"Using test sequence: {sequence.attack_id} ({len(sequence.turns)} turns)")
    print()

    # Create evaluator with test experiment ID
    evaluator = BatchEvaluator(
        db=db,
        experiment_id="test_unique_constraint",
        raw_log_path=Path("logs/test_unique_constraint.jsonl"),
        use_cumulative_context=False,
    )

    # First evaluation should succeed
    print("1. First evaluation (should succeed)...")
    result1 = evaluator.evaluate_sequence(
        sequence=sequence,
        principles=[EvaluationPrinciple.RECIPROCITY],
    )

    if result1.success:
        print(f"   ✓ Success: {len(result1.evaluations)} evaluations inserted")
    else:
        print(f"   ✗ Failed: {result1.error}")
        return

    # Second evaluation with same experiment_id should fail (duplicate)
    print("2. Second evaluation with same experiment_id (should fail with duplicate error)...")
    result2 = evaluator.evaluate_sequence(
        sequence=sequence,
        principles=[EvaluationPrinciple.RECIPROCITY],
    )

    if not result2.success and "duplicate" in result2.error.lower():
        print(f"   ✓ Correctly rejected duplicate: {result2.error}")
    else:
        print(f"   ✗ Should have failed but didn't: success={result2.success}, error={result2.error}")
        return

    # Third evaluation with different experiment_id should succeed
    print("3. Third evaluation with different experiment_id (should succeed)...")
    evaluator2 = BatchEvaluator(
        db=db,
        experiment_id="test_unique_constraint_2",  # Different experiment
        raw_log_path=Path("logs/test_unique_constraint_2.jsonl"),
        use_cumulative_context=False,
    )

    result3 = evaluator2.evaluate_sequence(
        sequence=sequence,
        principles=[EvaluationPrinciple.RECIPROCITY],
    )

    if result3.success:
        print(f"   ✓ Success: {len(result3.evaluations)} evaluations inserted")
    else:
        print(f"   ✗ Failed: {result3.error}")
        return

    print()
    print("=" * 60)
    print("✓ All tests passed!")
    print("  - UUID keys allow different experiments on same sequences")
    print("  - Unique index prevents duplicate (experiment, attack, turn)")
    print("  - Clear error messages when duplicates detected")
    print("=" * 60)

    # Cleanup test data
    print()
    print("Cleaning up test data...")
    coll = db.collection("phase3_principle_evaluations")
    deleted = 0
    for exp_id in ["test_unique_constraint", "test_unique_constraint_2"]:
        query = """
        FOR doc IN phase3_principle_evaluations
            FILTER doc.experiment_id == @exp_id
            REMOVE doc IN phase3_principle_evaluations
        """
        cursor = db.aql.execute(query, bind_vars={"exp_id": exp_id})
        deleted += sum(1 for _ in cursor)

    print(f"✓ Cleaned up {deleted} test evaluations")


if __name__ == "__main__":
    main()
