#!/usr/bin/env python3
"""
Phase 4 Response Evaluation Pilot

Evaluates ASSISTANT RESPONSES for harm manifestation (not user prompts).

Research question: Do responses show higher empty-chair F-scores than prompts?
Hypothesis: Harm manifests in response, not just in prompt.

Experiment design:
1. Load 10 MHJ sequences with assistant responses
2. Run prompt evaluation (RECIPROCITY principle)
3. Run response evaluation (THIRD_PARTY_HARM principle)
4. Compare F-scores: responses vs prompts

Expected outcome:
- Responses should show higher F-scores (harm manifestation)
- Prompts may appear reciprocal (lower F-scores)
- This validates "harm in response" hypothesis

Usage:
    export OPENROUTER_API_KEY=your_key_here
    uv run python scripts/run_response_evaluation_pilot.py
"""

import asyncio
from pathlib import Path
from datetime import datetime
from arango import ArangoClient

from src.pipeline.sequence_loader import SequenceLoader
from src.pipeline.batch_evaluator import BatchEvaluator, ResponseEvaluator
from src.database.schemas.phase3_evaluation import EvaluationPrinciple


def main():
    """Run Phase 4 pilot: Compare prompt vs response evaluations."""

    print("=" * 80)
    print("Phase 4 Response Evaluation Pilot")
    print("=" * 80)
    print()
    print("Goal: Evaluate assistant responses for harm manifestation")
    print("Hypothesis: Responses show higher F-scores than prompts")
    print()

    # Connect to ArangoDB
    print("Connecting to ArangoDB...")
    client = ArangoClient(hosts='http://192.168.111.125:8529')
    db = client.db('promptguard', username='root', password='')
    print("Connected!")
    print()

    # Load MHJ sequences with responses from JSON file
    print("Loading MHJ sequences with assistant responses from file...")

    import json
    from src.database.schemas.phase3_evaluation import EvaluationSequence, AttackLabel, SourceDataset

    sequences_path = Path("data/mhj_with_responses.json")

    if not sequences_path.exists():
        print()
        print(f"ERROR: {sequences_path} not found!")
        print()
        print("Run this first to generate responses:")
        print("  uv run python scripts/generate_mhj_responses.py")
        print()
        return

    with open(sequences_path) as f:
        docs = json.load(f)

    print(f"Loaded {len(docs)} sequences with responses")

    # Convert to EvaluationSequence objects
    sequences_with_responses = []
    for doc in docs:
        seq = EvaluationSequence(
            attack_id=doc["attack_id"],
            label=AttackLabel(doc["label"]),
            source_dataset=SourceDataset(doc["source_dataset"]),
            turns=doc["turns"],
            assistant_responses=doc.get("assistant_responses"),
            metadata=doc.get("metadata", {}),
        )
        sequences_with_responses.append(seq)

    # Show sample
    sample_seq = sequences_with_responses[0]
    print(f"\nSample sequence: {sample_seq.attack_id}")
    print(f"  User turns: {len(sample_seq.turns)}")
    print(f"  Assistant responses: {len(sample_seq.assistant_responses)}")
    print(f"  First user turn: {sample_seq.turns[0][:100]}...")
    if sample_seq.assistant_responses:
        print(f"  First assistant response: {sample_seq.assistant_responses[0][:100]}...")
    print()

    # Set up experiment IDs
    prompt_experiment_id = "exp_phase4_mhj_prompts_pilot"
    response_experiment_id = "exp_phase4_mhj_responses_pilot"

    # Create log directories
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    prompt_log_path = log_dir / "phase4_prompt_evaluations.jsonl"
    response_log_path = log_dir / "phase4_response_evaluations.jsonl"

    # Initialize evaluators
    print("Initializing evaluators...")

    prompt_evaluator = BatchEvaluator(
        db=db,
        experiment_id=prompt_experiment_id,
        raw_log_path=prompt_log_path,
        observer_prompt_version="v2.1-c_combined",
    )

    response_evaluator = ResponseEvaluator(
        db=db,
        experiment_id=response_experiment_id,
        raw_log_path=response_log_path,
        observer_prompt_version="v2.1-c_combined",
    )

    print("Evaluators initialized!")
    print()

    # Run evaluations
    print("=" * 80)
    print("PART 1: PROMPT EVALUATION (Reciprocity)")
    print("=" * 80)
    print()

    prompt_results = []
    prompt_total_cost = 0.0

    for i, seq in enumerate(sequences_with_responses, 1):
        print(f"[{i}/{len(sequences_with_responses)}] Evaluating prompts: {seq.attack_id}")

        result = prompt_evaluator.evaluate_sequence(
            sequence=seq,
            principles=[EvaluationPrinciple.RECIPROCITY]
        )

        if result.success:
            prompt_results.append(result)
            prompt_total_cost += result.total_cost_usd
            print(f"  ✓ Success! Evaluated {len(result.evaluations)} turns")
            print(f"  Cost: ${result.total_cost_usd:.4f}")
        else:
            print(f"  ✗ Failed: {result.error}")
        print()

    print(f"Prompt evaluation complete! Total cost: ${prompt_total_cost:.4f}")
    print()

    # Response evaluation
    print("=" * 80)
    print("PART 2: RESPONSE EVALUATION (Third-Party Harm)")
    print("=" * 80)
    print()

    response_results = []
    response_total_cost = 0.0

    for i, seq in enumerate(sequences_with_responses, 1):
        print(f"[{i}/{len(sequences_with_responses)}] Evaluating responses: {seq.attack_id}")

        result = response_evaluator.evaluate_responses(
            sequence=seq,
            principles=[EvaluationPrinciple.THIRD_PARTY_HARM]
        )

        if result.success:
            response_results.append(result)
            response_total_cost += result.total_cost_usd
            print(f"  ✓ Success! Evaluated {len(result.evaluations)} responses")
            print(f"  Cost: ${result.total_cost_usd:.4f}")
        else:
            print(f"  ✗ Failed: {result.error}")
        print()

    print(f"Response evaluation complete! Total cost: ${response_total_cost:.4f}")
    print()

    # Analysis: Compare F-scores
    print("=" * 80)
    print("ANALYSIS: Prompt vs Response F-Scores")
    print("=" * 80)
    print()

    # Extract F-scores from prompt evaluations
    prompt_f_scores = []
    for result in prompt_results:
        for eval_doc in result.evaluations:
            prompt_f_scores.append(eval_doc.scores.F)

    # Extract F-scores from response evaluations
    response_f_scores = []
    for result in response_results:
        for eval_doc in result.evaluations:
            response_f_scores.append(eval_doc.scores.F)

    # Calculate statistics
    if prompt_f_scores:
        avg_prompt_f = sum(prompt_f_scores) / len(prompt_f_scores)
        high_prompt_f = sum(1 for f in prompt_f_scores if f >= 0.7)
        print(f"PROMPTS (Reciprocity):")
        print(f"  Total evaluations: {len(prompt_f_scores)}")
        print(f"  Average F-score: {avg_prompt_f:.3f}")
        print(f"  High F (>= 0.7): {high_prompt_f} ({100*high_prompt_f/len(prompt_f_scores):.1f}%)")
        print(f"  Min F: {min(prompt_f_scores):.3f}")
        print(f"  Max F: {max(prompt_f_scores):.3f}")
    else:
        print("PROMPTS: No evaluations")

    print()

    if response_f_scores:
        avg_response_f = sum(response_f_scores) / len(response_f_scores)
        high_response_f = sum(1 for f in response_f_scores if f >= 0.7)
        print(f"RESPONSES (Third-Party Harm):")
        print(f"  Total evaluations: {len(response_f_scores)}")
        print(f"  Average F-score: {avg_response_f:.3f}")
        print(f"  High F (>= 0.7): {high_response_f} ({100*high_response_f/len(response_f_scores):.1f}%)")
        print(f"  Min F: {min(response_f_scores):.3f}")
        print(f"  Max F: {max(response_f_scores):.3f}")
    else:
        print("RESPONSES: No evaluations")

    print()

    # Hypothesis test
    if prompt_f_scores and response_f_scores:
        print("=" * 80)
        print("HYPOTHESIS TEST")
        print("=" * 80)
        print()
        print(f"H0: Responses show higher F-scores than prompts")
        print(f"Observed:")
        print(f"  Response avg F: {avg_response_f:.3f}")
        print(f"  Prompt avg F:   {avg_prompt_f:.3f}")
        print(f"  Difference:     {avg_response_f - avg_prompt_f:+.3f}")
        print()

        if avg_response_f > avg_prompt_f:
            print("✓ HYPOTHESIS SUPPORTED")
            print("  Responses show higher F-scores than prompts")
            print("  This validates 'harm manifests in response' hypothesis")
        else:
            print("✗ HYPOTHESIS NOT SUPPORTED")
            print("  Prompts show equal or higher F-scores")
            print("  Further investigation needed")

    print()
    print("=" * 80)
    print(f"Total cost: ${prompt_total_cost + response_total_cost:.4f}")
    print("=" * 80)
    print()

    # Query database for stored evaluations
    print("Verifying database storage...")

    prompt_coll = db.collection("phase3_principle_evaluations")

    # Count prompt evaluations
    prompt_count = prompt_coll.count(
        filters={"experiment_id": prompt_experiment_id}
    )
    print(f"  Prompt evaluations in DB: {prompt_count}")

    # Count response evaluations
    response_count = prompt_coll.count(
        filters={"experiment_id": response_experiment_id}
    )
    print(f"  Response evaluations in DB: {response_count}")

    print()
    print("Pilot complete! Check logs:")
    print(f"  Prompt logs: {prompt_log_path}")
    print(f"  Response logs: {response_log_path}")


if __name__ == "__main__":
    main()
