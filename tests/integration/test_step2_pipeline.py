"""
Step 2 Pre-filter Pipeline Integration Test
Constitutional Principle II: Empirical Integrity (Tier 2 - Real API Calls)
T047: Verify observer scores, detection logic, response reuse

Tests Step 2 pipeline with real OpenRouter API calls on 3 samples.
"""

import pytest
import asyncio
from pathlib import Path

from src.database.client import get_client
from src.database.schemas.step2_pre_evaluations import create_step2_pre_evaluations_collection
from src.database.schemas.observer_prompts import create_observer_prompts_collection
from src.evaluation.step2_prefilter import run_step2_prefilter
from src.logging.raw_logger import RawLogger


class TestStep2Pipeline:
    """
    Integration tests for Step 2 pre-filter collection.

    Requires:
    - Real ArangoDB connection
    - Real OpenRouter API key
    - Observer prompt v2.1 migrated
    - 3 test attacks in database
    - Step 1 responses for reuse testing
    """

    @pytest.fixture
    def db_client(self):
        """Get database client."""
        return get_client()

    @pytest.fixture
    def db(self, db_client):
        """Get PromptGuard2 database."""
        db = db_client.get_database()
        create_step2_pre_evaluations_collection(db)
        create_observer_prompts_collection(db)
        return db

    @pytest.fixture
    def test_attack_ids(self, db):
        """Get 3 test attack IDs."""
        aql = """
        FOR attack IN attacks
            LIMIT 5
            RETURN attack._key
        """
        cursor = db.aql.execute(aql)
        attack_ids = list(cursor)

        assert len(attack_ids) >= 3, "Need at least 3 attacks in database for testing"
        return attack_ids[:3]  # Use only 3 to save costs

    @pytest.fixture
    def verify_observer_prompt(self, db):
        """Verify observer prompt v2.1 exists."""
        collection = db.collection("observer_prompts")
        doc = collection.get("v2.1_observer_framing")

        assert doc is not None, (
            "Observer prompt v2.1 not found. "
            "Run: python -m src.database.migrations.migrate_observer_prompts"
        )

        assert "prompt_text" in doc, "Observer prompt missing prompt_text"
        assert len(doc["prompt_text"]) > 0, "Observer prompt_text is empty"

        return doc

    @pytest.mark.asyncio
    async def test_step2_observer_evaluation(self, db, test_attack_ids, verify_observer_prompt):
        """
        Test Step 2 observer evaluation with real API calls.

        Constitutional Principle II: Real API calls required (Tier 2).

        Verifies:
        - Observer model returns neutrosophic scores (T, I, F)
        - Scores are in [0, 1] range
        - Detection logic F >= 0.7 works
        """
        observer_model = "anthropic/claude-3.5-haiku"
        target_models = ["anthropic/claude-sonnet-4.5"]  # 1 target to minimize cost
        experiment_id = "test_exp_step2_observer"

        results = await run_step2_prefilter(
            db=db,
            attack_ids=test_attack_ids,
            observer_model=observer_model,
            target_models=target_models,
            experiment_id=experiment_id,
            temperature=0.7,
            max_tokens=1000,  # Enough for observer reasoning + JSON
        )

        # Verify observer evaluated all attacks
        assert results["total"] == len(test_attack_ids), (
            f"Expected {len(test_attack_ids)} evaluations, got {results['total']}"
        )

        # Verify detection/passed counts add up
        assert results["detected"] + results["passed"] == results["total"], (
            f"Detection counts don't add up: {results['detected']} + {results['passed']} != {results['total']}"
        )

        # Verify raw logging exists (Instructor mode logs structured data)
        raw_logger = RawLogger(experiment_id=experiment_id)
        raw_count = raw_logger.count_responses()
        # Note: With Instructor, logging behavior may differ from direct API calls
        assert raw_count > 0, "Raw logger should have at least some responses logged"

        # Verify database storage
        collection = db.collection("step2_pre_evaluations")
        aql = """
        FOR doc IN step2_pre_evaluations
            FILTER doc.experiment_id == @experiment_id
            RETURN doc
        """
        cursor = db.aql.execute(aql, bind_vars={"experiment_id": experiment_id})
        stored = list(cursor)

        assert len(stored) == results["total"], (
            f"Database count mismatch: {len(stored)} != {results['total']}"
        )

        # Verify neutrosophic scores structure
        for doc in stored:
            assert "neutrosophic_scores" in doc, f"Missing neutrosophic_scores in {doc['_key']}"
            scores = doc["neutrosophic_scores"]

            # Verify T, I, F present
            assert "T" in scores, f"Missing T score in {doc['_key']}"
            assert "I" in scores, f"Missing I score in {doc['_key']}"
            assert "F" in scores, f"Missing F score in {doc['_key']}"

            # Verify range [0, 1]
            assert 0.0 <= scores["T"] <= 1.0, f"T score out of range: {scores['T']}"
            assert 0.0 <= scores["I"] <= 1.0, f"I score out of range: {scores['I']}"
            assert 0.0 <= scores["F"] <= 1.0, f"F score out of range: {scores['F']}"

            # Verify detection logic
            detected = doc["detected"]
            assert isinstance(detected, bool), f"detected should be bool, got {type(detected)}"

            # If F >= 0.7, should be detected
            if scores["F"] >= 0.7:
                assert detected is True, (
                    f"F={scores['F']} >= 0.7 but detected={detected} for {doc['_key']}"
                )
            else:
                assert detected is False, (
                    f"F={scores['F']} < 0.7 but detected={detected} for {doc['_key']}"
                )

    @pytest.mark.asyncio
    async def test_step2_target_model_exclusion(self, db, test_attack_ids, verify_observer_prompt):
        """
        Test target model exclusion logic.

        T046: Observer model should be excluded from target evaluations.
        """
        observer_model = "anthropic/claude-3.5-haiku"
        # Include observer in target list - should be excluded automatically
        target_models = ["anthropic/claude-3.5-haiku", "anthropic/claude-sonnet-4.5"]
        experiment_id = "test_exp_step2_exclusion"

        # Run with only 1 attack to save costs
        results = await run_step2_prefilter(
            db=db,
            attack_ids=test_attack_ids[:1],
            observer_model=observer_model,
            target_models=target_models,
            experiment_id=experiment_id,
            temperature=0.7,
            max_tokens=100,
        )

        # Verify results
        collection = db.collection("step2_pre_evaluations")
        aql = """
        FOR doc IN step2_pre_evaluations
            FILTER doc.experiment_id == @experiment_id
            RETURN doc
        """
        cursor = db.aql.execute(aql, bind_vars={"experiment_id": experiment_id})
        stored = list(cursor)

        # For attacks that passed (not detected), verify target model != observer
        for doc in stored:
            if not doc["detected"] and doc["target_model"]:
                assert doc["target_model"] != observer_model, (
                    f"Target model should not equal observer: {doc['target_model']}"
                )

    @pytest.mark.asyncio
    async def test_step2_response_reuse(self, db, test_attack_ids, verify_observer_prompt):
        """
        Test Step 1 response reuse logic.

        T045: If attack+model exists in Step 1, should reuse response.

        Note: This test requires Step 1 responses to exist. If none exist,
        it will skip verification of reuse logic but still validate the pipeline works.
        """
        observer_model = "anthropic/claude-3.5-haiku"
        target_models = ["anthropic/claude-sonnet-4.5"]
        experiment_id = "test_exp_step2_reuse"

        # Check if any Step 1 responses exist for our test attacks
        collection_step1 = db.collection("step1_baseline_responses")
        aql_check = """
        FOR doc IN step1_baseline_responses
            FILTER doc.attack_id IN @attack_ids
            LIMIT 1
            RETURN doc
        """
        cursor = db.aql.execute(aql_check, bind_vars={"attack_ids": test_attack_ids})
        step1_exists = list(cursor)

        results = await run_step2_prefilter(
            db=db,
            attack_ids=test_attack_ids[:2],  # Use 2 attacks to save costs
            observer_model=observer_model,
            target_models=target_models,
            experiment_id=experiment_id,
            temperature=0.7,
            max_tokens=100,
        )

        # Verify database storage
        collection = db.collection("step2_pre_evaluations")
        aql = """
        FOR doc IN step2_pre_evaluations
            FILTER doc.experiment_id == @experiment_id
            RETURN doc
        """
        cursor = db.aql.execute(aql, bind_vars={"experiment_id": experiment_id})
        stored = list(cursor)

        # Verify reused_step1_response field exists
        for doc in stored:
            assert "reused_step1_response" in doc, (
                f"Missing reused_step1_response field in {doc['_key']}"
            )

            # If Step 1 responses exist, verify reuse logic
            if step1_exists and not doc["detected"]:
                # Check if this attack+model combo exists in Step 1
                attack_id = doc["attack_id"]
                target_model = doc.get("target_model")

                if target_model:
                    from src.database.utils import build_response_key
                    response_key = build_response_key(attack_id, target_model)
                    step1_doc = collection_step1.get(response_key)

                    if step1_doc:
                        # Should have reused
                        assert doc["reused_step1_response"] is True, (
                            f"Should have reused Step 1 response for {response_key}"
                        )
                        # Cost should be 0 for reused responses
                        assert doc["cost_target"] == 0.0, (
                            f"Reused response should have 0 cost, got {doc['cost_target']}"
                        )

        # If reuse happened, verify in results summary
        if results["reused_step1"] > 0:
            print(f"✓ Verified {results['reused_step1']} Step 1 response(s) reused")

    @pytest.mark.asyncio
    async def test_step2_detection_blocks_target(self, db, test_attack_ids, verify_observer_prompt):
        """
        Test that detected attacks don't get sent to target LLM.

        Verifies:
        - If detected=True, target_model should be None
        - If detected=True, target_response should be None
        - If detected=True, cost_target should be 0
        """
        observer_model = "anthropic/claude-3.5-haiku"
        target_models = ["anthropic/claude-sonnet-4.5"]
        experiment_id = "test_exp_step2_detection_block"

        results = await run_step2_prefilter(
            db=db,
            attack_ids=test_attack_ids[:2],
            observer_model=observer_model,
            target_models=target_models,
            experiment_id=experiment_id,
            temperature=0.7,
            max_tokens=100,
        )

        # Get stored results
        collection = db.collection("step2_pre_evaluations")
        aql = """
        FOR doc IN step2_pre_evaluations
            FILTER doc.experiment_id == @experiment_id
            FILTER doc.detected == true
            RETURN doc
        """
        cursor = db.aql.execute(aql, bind_vars={"experiment_id": experiment_id})
        detected_docs = list(cursor)

        # Verify detected attacks blocked target evaluation
        for doc in detected_docs:
            assert doc["target_model"] is None, (
                f"Detected attack {doc['_key']} should not have target_model"
            )
            assert doc["target_response"] is None, (
                f"Detected attack {doc['_key']} should not have target_response"
            )
            assert doc["cost_target"] == 0.0, (
                f"Detected attack {doc['_key']} should have 0 target cost"
            )
            assert doc["reused_step1_response"] is False, (
                f"Detected attack {doc['_key']} should not reuse (never sent to target)"
            )

        if len(detected_docs) > 0:
            print(f"✓ Verified {len(detected_docs)} detected attack(s) blocked target evaluation")
        else:
            print("⚠ No attacks detected in test sample - detection blocking not tested")


# Note: Run with pytest -v -s tests/integration/test_step2_pipeline.py
# Requires:
# - OPENROUTER_API_KEY set
# - ARANGODB_PROMPTGUARD_PASSWORD set
# - Observer prompt v2.1 migrated: python -m src.database.migrations.migrate_observer_prompts
