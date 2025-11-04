"""
Step 1 Baseline Pipeline Integration Test
Constitutional Principle II: Empirical Integrity (Tier 2 - Real API Calls)

Tests Step 1 pipeline with real OpenRouter API calls on 5 samples.
"""

import pytest
import asyncio
from pathlib import Path

from src.database.client import get_client
from src.database.schemas.step1_baseline_responses import create_step1_baseline_responses_collection
from src.evaluation.step1_baseline import run_step1_baseline
from src.logging.raw_logger import RawLogger
from src.evaluation.checkpoint import CheckpointManager


class TestStep1Pipeline:
    """
    Integration tests for Step 1 baseline collection.

    Requires:
    - Real ArangoDB connection
    - Real OpenRouter API key
    - 5 test attacks in database
    """

    @pytest.fixture
    def db_client(self):
        """Get database client."""
        return get_client()

    @pytest.fixture
    def db(self, db_client):
        """Get PromptGuard2 database."""
        db = db_client.get_database()
        create_step1_baseline_responses_collection(db)
        return db

    @pytest.fixture
    def test_attack_ids(self, db):
        """Get 5 test attack IDs."""
        aql = """
        FOR attack IN attacks
            LIMIT 5
            RETURN attack._key
        """
        cursor = db.aql.execute(aql)
        attack_ids = list(cursor)

        assert len(attack_ids) >= 3, "Need at least 3 attacks in database for testing"
        return attack_ids[:3]  # Use only 3 to save costs

    @pytest.mark.asyncio
    async def test_step1_real_api_calls(self, db, test_attack_ids):
        """
        Test Step 1 with real API calls.

        Constitutional Principle II: Real API calls required (Tier 2).
        """
        # Use only 1 model for testing to minimize costs
        target_models = ["anthropic/claude-haiku-4.5"]

        experiment_id = "test_exp_step1"

        results = await run_step1_baseline(
            db=db,
            attack_ids=test_attack_ids,
            target_models=target_models,
            experiment_id=experiment_id,
            temperature=0.7,
            max_tokens=100,  # Reduced for testing
            max_concurrent=2,
        )

        # Verify results
        expected_total = len(test_attack_ids) * len(target_models)
        assert results["total"] == expected_total, (
            f"Expected {expected_total} evaluations, got {results['total']}"
        )
        assert results["completed"] > 0, "No evaluations completed"

        # Verify raw logging
        raw_logger = RawLogger(experiment_id=experiment_id)
        raw_count = raw_logger.count_responses()
        assert raw_count == results["completed"], (
            f"Raw response count mismatch: {raw_count} != {results['completed']}"
        )

        # Verify database storage
        collection = db.collection("step1_baseline_responses")
        aql = """
        FOR doc IN step1_baseline_responses
            FILTER doc.experiment_id == @experiment_id
            RETURN doc
        """
        cursor = db.aql.execute(aql, bind_vars={"experiment_id": experiment_id})
        stored = list(cursor)

        assert len(stored) == results["completed"], (
            f"Database count mismatch: {len(stored)} != {results['completed']}"
        )

        # Verify response structure
        for doc in stored:
            assert "attack_id" in doc
            assert "response_text" in doc
            assert "raw_api_response" in doc
            assert doc["raw_api_response"], "Raw API response is empty"

    @pytest.mark.asyncio
    async def test_checkpoint_recovery(self, db, test_attack_ids):
        """Test checkpoint creation and recovery."""
        experiment_id = "test_exp_checkpoint"
        checkpoint_mgr = CheckpointManager(experiment_id=experiment_id)

        # Clean up existing checkpoint
        try:
            checkpoint_mgr.delete()
        except:
            pass

        # Create checkpoint
        checkpoint_mgr.create()
        assert checkpoint_mgr.checkpoint_file.exists(), "Checkpoint not created"

        # Mark attack-model pairs as completed
        test_model = "test/model-a"
        for attack_id in test_attack_ids[:2]:
            checkpoint_mgr.mark_completed(attack_id, test_model)

        # Load checkpoint
        checkpoint = checkpoint_mgr.load()
        assert len(checkpoint["completed_pairs"]) == 2
        assert f"{test_attack_ids[0]}_{test_model}" in checkpoint["completed_pairs"]

        # Verify atomic rename (tmp file should not exist after write)
        assert not checkpoint_mgr.temp_file.exists(), "Temp file not cleaned up"

        # Clean up
        checkpoint_mgr.delete()

    def test_fail_fast_on_invalid_api_key(self):
        """
        Test fail-fast behavior with invalid API key.

        Constitutional Principle IV: Fail-Fast on data-spoiling errors.
        """
        # This would require mocking the API client or using invalid key
        # Skipped for now - would be implemented as:
        # 1. Set invalid OPENROUTER_API_KEY
        # 2. Attempt evaluation
        # 3. Verify EvaluationError raised (recoverable=False for auth errors)
        pytest.skip("Fail-fast test requires API key mocking")

    def test_recoverable_error_continues(self):
        """
        Test that recoverable errors (e.g., JSON parsing) capture diagnostics and continue.

        Constitutional Principle IV: Distinguish data-spoiling vs recoverable errors.
        """
        # This would require simulating a malformed API response
        # Skipped for now - would be implemented as:
        # 1. Mock API to return malformed JSON
        # 2. Verify error logged to processing_failures
        # 3. Verify pipeline continues (doesn't halt)
        pytest.skip("Recoverable error test requires response mocking")


# Note: Run with pytest -v -s tests/integration/test_step1_pipeline.py
# Requires OPENROUTER_API_KEY and ARANGODB_PROMPTGUARD_PASSWORD set
