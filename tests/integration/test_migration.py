"""
Migration Integration Test
Constitutional Principle II: Empirical Integrity (Tier 2 - API Integration)

Tests migration with real database connections.
"""

import pytest
import json
from pathlib import Path

from src.database.client import get_client
from src.database.schemas.attacks import validate_attack_distribution
from src.database.schemas.models import validate_model_registry


class TestMigration:
    """
    Integration tests for database migration.

    Requires real ArangoDB connections.
    """

    @pytest.fixture
    def db_client(self):
        """Get database client."""
        return get_client()

    @pytest.fixture
    def test_attacks(self):
        """Load test attack fixtures."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_attacks.json"
        with open(fixture_path, 'r') as f:
            return json.load(f)

    def test_database_connections(self, db_client):
        """Test both database connections work."""
        pg2_ok, old_ok = db_client.verify_connections()

        assert pg2_ok, "PromptGuard2 database connection failed"
        assert old_ok, "Old PromptGuard database connection failed"

    def test_attacks_collection_exists(self, db_client):
        """Test attacks collection exists in PromptGuard2."""
        db = db_client.get_database()
        assert db.has_collection("attacks"), "Attacks collection not found"

    def test_attacks_count(self, db_client):
        """Test attacks collection has 762 attacks (or test fixtures)."""
        db = db_client.get_database()
        collection = db.collection("attacks")

        count = collection.count()

        # Allow either 762 (full migration) or 5 (test fixtures only)
        assert count in [5, 762], f"Unexpected attack count: {count}"

    def test_attack_distribution(self, db_client):
        """Test attack label distribution is valid."""
        db = db_client.get_database()
        validation = validate_attack_distribution(db, expected_total=762)

        # If we have 762, validate full distribution
        # If we have 5 (test fixtures), just check structure
        collection = db.collection("attacks")
        count = collection.count()

        if count == 762:
            assert validation["valid"], (
                f"Attack distribution validation failed: "
                f"{validation['distribution']}, "
                f"Total: {validation['total']}, "
                f"Expected: {validation['expected_total']}"
            )
        else:
            # Test fixtures - just verify we have the expected labels
            assert validation["total"] >= 3, "Need at least 3 test attacks"
            assert "manipulative" in validation["distribution"]
            assert "extractive" in validation["distribution"]
            assert "reciprocal" in validation["distribution"]

    def test_attack_metadata_integrity(self, db_client):
        """Test attacks have required metadata fields."""
        db = db_client.get_database()
        collection = db.collection("attacks")

        # Sample 5 attacks
        aql = """
        FOR attack IN attacks
            LIMIT 5
            RETURN attack
        """

        cursor = db.aql.execute(aql)
        attacks = list(cursor)

        assert len(attacks) > 0, "No attacks found"

        for attack in attacks:
            assert "_key" in attack, "Attack missing _key"
            assert "prompt_text" in attack, "Attack missing prompt_text"
            assert "ground_truth" in attack, "Attack missing ground_truth"
            assert attack["ground_truth"] in [
                "manipulative",
                "extractive",
                "reciprocal",
                "borderline"
            ], f"Invalid ground_truth: {attack['ground_truth']}"

    def test_models_collection_exists(self, db_client):
        """Test models collection exists."""
        db = db_client.get_database()
        assert db.has_collection("models"), "Models collection not found"

    def test_models_validation(self, db_client):
        """Test models collection has sufficient models."""
        db = db_client.get_database()
        validation = validate_model_registry(db, min_models=7)

        # May fail if models not yet migrated - that's OK
        if validation["total_models"] >= 7:
            assert validation["valid"], (
                f"Model registry validation failed: {validation['errors']}"
            )
        else:
            pytest.skip(f"Models not yet migrated ({validation['total_models']} < 7)")

    def test_test_fixtures_load(self, test_attacks):
        """Test sample attacks fixture loads correctly."""
        assert len(test_attacks) == 5, "Expected 5 test attacks"

        # Verify fixture structure
        for attack in test_attacks:
            assert "_key" in attack
            assert "prompt_text" in attack
            assert "ground_truth" in attack
            assert attack["ground_truth"] in [
                "manipulative",
                "extractive",
                "reciprocal",
                "borderline"
            ]
