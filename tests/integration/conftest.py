"""Pytest configuration for Phase 3 integration tests.

Provides fixtures for:
- ArangoDB connection and cleanup
- Phase 2 observer framework access
- Cost tracking utilities
"""

import pytest
from arango import ArangoClient
from typing import Generator
import os


@pytest.fixture(scope="session")
def arango_client() -> Generator:
    """Provide ArangoDB client for integration tests."""
    # Connection details from environment or config
    host = os.getenv("ARANGO_HOST", "http://192.168.111.125:8529")

    client = ArangoClient(hosts=host)
    yield client


@pytest.fixture(scope="session")
def arango_db(arango_client):
    """Provide database connection for Phase 3 tests."""
    db_name = os.getenv("ARANGO_DB", "PromptGuard2")
    username = os.getenv("ARANGO_USER", "pgtest")
    password = os.getenv("ARANGODB_PROMPTGUARD_PASSWORD", "")

    db = arango_client.db(db_name, username=username, password=password)
    yield db


@pytest.fixture
def phase3_collections(arango_db):
    """Ensure Phase 3 collections exist for testing."""
    collections = {
        "phase3_evaluation_sequences": {
            "edge": False,
            "indexes": [
                {"type": "hash", "fields": ["source_dataset"]},
                {"type": "hash", "fields": ["label"]},
            ]
        },
        "phase3_principle_evaluations": {
            "edge": False,
            "indexes": [
                {"type": "hash", "fields": ["attack_id", "principle"]},
                {"type": "hash", "fields": ["attack_id", "turn_number"]},
                {"type": "hash", "fields": ["experiment_id"]},
            ]
        }
    }

    created = []
    for coll_name, config in collections.items():
        if not arango_db.has_collection(coll_name):
            coll = arango_db.create_collection(coll_name, edge=config["edge"])
            for index_def in config.get("indexes", []):
                coll.add_hash_index(fields=index_def["fields"])
            created.append(coll_name)

    yield created

    # Cleanup: Remove test documents but keep collections
    # (Full cleanup handled by teardown scripts if needed)


@pytest.fixture
def cost_tracker():
    """Track API costs during integration tests."""
    costs = {"total": 0.0, "calls": 0}

    def track(cost_usd: float):
        costs["total"] += cost_usd
        costs["calls"] += 1

    def get_summary():
        return costs.copy()

    tracker = type('CostTracker', (), {
        'track': track,
        'get_summary': get_summary,
        'costs': costs
    })()

    yield tracker

    # Print summary after test
    summary = tracker.get_summary()
    if summary["calls"] > 0:
        print(f"\n💰 Integration test cost: ${summary['total']:.4f} ({summary['calls']} API calls)")
