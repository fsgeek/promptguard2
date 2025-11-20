"""Integration test for trajectory storage round-trip (T009).

Tests that PrincipleEvaluation documents can be stored and queried correctly.
"""

import pytest
from datetime import datetime

from src.database.schemas.phase3_evaluation import (
    PrincipleEvaluation,
    NeutrosophicScore,
    EvaluationPrinciple,
)


def create_test_evaluations(attack_id: str, turns: int) -> list[PrincipleEvaluation]:
    """Create test evaluation documents for a trajectory."""
    evaluations = []

    for turn_num in range(1, turns + 1):
        # Simulate gradual drift: F score increases over turns
        f_score = 0.1 + (turn_num - 1) * 0.15

        eval_doc = PrincipleEvaluation(
            attack_id=attack_id,
            principle=EvaluationPrinciple.RECIPROCITY,
            turn_number=turn_num,
            evaluator_model="anthropic/claude-3.5-haiku",
            observer_prompt_version="v2.1-c_combined",
            timestamp=datetime.utcnow(),
            scores=NeutrosophicScore(
                T=0.8 - f_score,  # Truth decreases as falsity increases
                I=0.1,
                F=min(f_score, 1.0),
            ),
            reasoning=f"Turn {turn_num} evaluation for testing",
            raw_response=f"{{\"T\": {0.8 - f_score}, \"I\": 0.1, \"F\": {min(f_score, 1.0)}}}",
            model_temperature=0.0,
            experiment_id="test_trajectory_roundtrip",
            cost_usd=0.001,
            latency_ms=300 + turn_num * 10,
        )
        evaluations.append(eval_doc)

    return evaluations


@pytest.mark.integration
def test_trajectory_round_trip(arango_db, phase3_collections):
    """
    Test trajectory storage and retrieval round-trip.

    Verifies:
    1. PrincipleEvaluation documents can be inserted
    2. Trajectory can be queried by attack_id + principle
    3. Documents are returned in correct order (turn_number ascending)
    4. Round-trip preserves all data
    5. Pydantic validation works before insert
    """
    # Create 5 evaluations for same attack_id
    attack_id = "test_roundtrip_001"
    evaluations = create_test_evaluations(attack_id=attack_id, turns=5)

    # Get collection
    coll = arango_db.collection("phase3_principle_evaluations")

    # Insert evaluations (with Pydantic validation)
    for eval_doc in evaluations:
        # Validate with Pydantic before insert
        doc_dict = eval_doc.model_dump(mode="json")

        # Create composite key for idempotency
        key = f"{eval_doc.attack_id}_{eval_doc.principle.value}_{eval_doc.turn_number}"
        doc_dict["_key"] = key

        # Insert (idempotent - will update if exists)
        coll.insert(doc_dict, overwrite=True)

    # Query trajectory via AQL
    aql = """
    FOR doc IN phase3_principle_evaluations
        FILTER doc.attack_id == @attack_id
        FILTER doc.principle == @principle
        SORT doc.turn_number ASC
        RETURN doc
    """

    cursor = arango_db.aql.execute(
        aql,
        bind_vars={
            "attack_id": attack_id,
            "principle": EvaluationPrinciple.RECIPROCITY.value,
        },
    )

    # Convert to list
    trajectory = list(cursor)

    # Assertions
    assert len(trajectory) == 5, "Should retrieve all 5 turns"

    # Verify ordering
    for i, doc in enumerate(trajectory):
        expected_turn = i + 1
        assert doc["turn_number"] == expected_turn, f"Turn {i} should be turn_number {expected_turn}"

    # Verify round-trip data integrity
    for i, doc in enumerate(trajectory):
        original = evaluations[i]

        assert doc["attack_id"] == original.attack_id
        assert doc["principle"] == original.principle.value
        assert doc["turn_number"] == original.turn_number
        assert doc["evaluator_model"] == original.evaluator_model
        assert doc["observer_prompt_version"] == original.observer_prompt_version

        # Verify scores
        assert abs(doc["scores"]["T"] - original.scores.T) < 0.01
        assert abs(doc["scores"]["I"] - original.scores.I) < 0.01
        assert abs(doc["scores"]["F"] - original.scores.F) < 0.01

        assert doc["reasoning"] == original.reasoning
        assert doc["raw_response"] == original.raw_response
        assert doc["experiment_id"] == original.experiment_id

    # Verify trajectory shows gradual drift pattern
    f_scores = [doc["scores"]["F"] for doc in trajectory]
    assert f_scores == sorted(f_scores), "F scores should be monotonically increasing"
    assert f_scores[-1] > f_scores[0], "F should drift from low to high"

    # Cleanup
    coll.delete_many({"attack_id": attack_id})


@pytest.mark.integration
def test_multi_principle_trajectory(arango_db, phase3_collections):
    """
    Test that multiple principles can be evaluated for same attack.

    Verifies composability: adding new principles doesn't require re-evaluation.
    """
    attack_id = "test_multi_principle_001"

    # Evaluate same attack with two principles
    reciprocity_evals = create_test_evaluations(attack_id=attack_id, turns=3)

    # Create context_integrity evaluations (different scores)
    context_evals = []
    for turn_num in range(1, 4):
        eval_doc = PrincipleEvaluation(
            attack_id=attack_id,
            principle=EvaluationPrinciple.CONTEXT_INTEGRITY,
            turn_number=turn_num,
            evaluator_model="anthropic/claude-3.5-haiku",
            observer_prompt_version="v2.1-c_combined",
            timestamp=datetime.utcnow(),
            scores=NeutrosophicScore(
                T=0.5,
                I=0.3,
                F=0.2 + turn_num * 0.1,
            ),
            reasoning=f"Context integrity assessment turn {turn_num}",
            raw_response="{}",
            model_temperature=0.0,
            experiment_id="test_multi_principle",
        )
        context_evals.append(eval_doc)

    # Insert both principle evaluations
    coll = arango_db.collection("phase3_principle_evaluations")

    for eval_doc in reciprocity_evals + context_evals:
        doc_dict = eval_doc.model_dump(mode="json")
        key = f"{eval_doc.attack_id}_{eval_doc.principle.value}_{eval_doc.turn_number}"
        doc_dict["_key"] = key
        coll.insert(doc_dict, overwrite=True)

    # Query each principle separately
    for principle in [EvaluationPrinciple.RECIPROCITY, EvaluationPrinciple.CONTEXT_INTEGRITY]:
        cursor = arango_db.aql.execute(
            """
            FOR doc IN phase3_principle_evaluations
                FILTER doc.attack_id == @attack_id
                FILTER doc.principle == @principle
                SORT doc.turn_number ASC
                RETURN doc
            """,
            bind_vars={"attack_id": attack_id, "principle": principle.value},
        )

        trajectory = list(cursor)
        assert len(trajectory) == 3, f"Should have 3 turns for {principle.value}"

    # Cleanup
    coll.delete_many({"attack_id": attack_id})
