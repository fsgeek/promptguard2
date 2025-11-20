"""
Migration: Create Phase 3 Session-Based Temporal Tracking Collections

Creates:
1. phase3_evaluation_sequences collection - Multi-turn attack sequences with ground truth
2. phase3_principle_evaluations collection - Per-turn neutrosophic evaluations

Constitutional Requirements:
- Schema documentation BEFORE collection creation (Constitution VI)
- Provenance fields for reproducibility
- Idempotent migration (safe to re-run)

Date: 2025-11-18
Phase: Phase 3 - Session-Based Temporal Tracking
"""

from src.database.client import get_client


# ===== SCHEMA DOCUMENTATION (Constitution VI) =====

PHASE3_EVALUATION_SEQUENCES_SCHEMA = {
    "collection_name": "phase3_evaluation_sequences",
    "description": "Multi-turn attack sequences with ground truth labels for temporal tracking evaluation",
    "fields": {
        "_key": {
            "type": "string",
            "description": "attack_id (unique identifier for this attack sequence)",
            "example": "xguard_001"
        },
        "label": {
            "type": "string (enum)",
            "description": "Ground truth classification",
            "values": ["benign", "jailbreak", "injection", "meta_framing", "extraction", "unknown"]
        },
        "source_dataset": {
            "type": "string (enum)",
            "description": "Dataset provenance",
            "values": ["xguard_train", "mhj", "tensortrust", "manual"]
        },
        "turns": {
            "type": "array of strings",
            "description": "Ordered list of prompt texts (chronological)",
            "validation": "Must have at least one turn"
        },
        "metadata": {
            "type": "object",
            "description": "Dataset-specific attributes (category, tactic, etc.)",
            "example": {"category": "chemical", "plain_goal": "Instructions for making dimethylmercury"}
        },
        "created_at": {
            "type": "string (ISO 8601)",
            "description": "When sequence was added to database (UTC with timezone)"
        }
    },
    "indexes": [
        {"type": "hash", "fields": ["source_dataset"], "unique": False},
        {"type": "hash", "fields": ["label"], "unique": False},
        {"type": "persistent", "fields": ["created_at"], "unique": False}
    ]
}

PHASE3_PRINCIPLE_EVALUATIONS_SCHEMA = {
    "collection_name": "phase3_principle_evaluations",
    "description": "Per-turn neutrosophic evaluations against constitutional principles",
    "fields": {
        "_key": {
            "type": "string",
            "description": "Composite key: {attack_id}_{principle}_{turn_number}",
            "example": "xguard_001_reciprocity_3"
        },
        "attack_id": {
            "type": "string",
            "description": "Links to phase3_evaluation_sequences._key",
            "example": "xguard_001"
        },
        "principle": {
            "type": "string (enum)",
            "description": "Constitutional principle evaluated",
            "values": ["reciprocity", "context_integrity", "third_party_harm"]
        },
        "turn_number": {
            "type": "integer",
            "description": "Which turn in the sequence (1-indexed)",
            "validation": "Must be >= 1"
        },
        "evaluator_model": {
            "type": "string",
            "description": "AI model that performed evaluation",
            "example": "anthropic/claude-3-haiku"
        },
        "observer_prompt_version": {
            "type": "string",
            "description": "Observer prompt version used",
            "example": "v2.1-c"
        },
        "timestamp": {
            "type": "string (ISO 8601)",
            "description": "When evaluation occurred (UTC with timezone)"
        },
        "scores": {
            "type": "object",
            "description": "Neutrosophic T/I/F scores (0.0-1.0)",
            "fields": {
                "T": "float (0.0-1.0) - Truth degree",
                "I": "float (0.0-1.0) - Indeterminacy degree",
                "F": "float (0.0-1.0) - Falsity degree"
            }
        },
        "reasoning": {
            "type": "string",
            "description": "Observer's explanation for assessment"
        },
        "raw_response": {
            "type": "string",
            "description": "CRITICAL: Complete untruncated LLM response (before parsing) for reproducibility"
        },
        "model_temperature": {
            "type": "float (optional)",
            "description": "Temperature used for evaluation (if applicable)"
        },
        "experiment_id": {
            "type": "string",
            "description": "Links evaluation to experiment for provenance",
            "example": "exp_phase3a_xguard"
        },
        "cost_usd": {
            "type": "float",
            "description": "API cost for this evaluation (for empirical integrity)"
        },
        "latency_ms": {
            "type": "integer",
            "description": "API latency in milliseconds"
        }
    },
    "indexes": [
        {"type": "hash", "fields": ["attack_id", "principle"], "unique": False},
        {"type": "hash", "fields": ["attack_id", "turn_number"], "unique": False},
        {"type": "hash", "fields": ["experiment_id"], "unique": False},
        {"type": "persistent", "fields": ["timestamp"], "unique": False},
        {"type": "hash", "fields": ["principle"], "unique": False}
    ]
}


def create_collection_if_not_exists(db, collection_name, indexes):
    """
    Create collection and indexes (idempotent).

    Args:
        db: ArangoDB database instance
        collection_name: Name of collection to create
        indexes: List of index specifications

    Returns:
        Collection instance
    """
    # Create collection
    if not db.has_collection(collection_name):
        collection = db.create_collection(collection_name)
        print(f"✓ Created collection: {collection_name}")
    else:
        collection = db.collection(collection_name)
        print(f"⚠ Collection already exists: {collection_name}")

    # Create indexes
    existing_indexes = {tuple(idx['fields']): idx for idx in collection.indexes()}

    for index_spec in indexes:
        index_type = index_spec['type']
        fields = index_spec['fields']
        unique = index_spec.get('unique', False)

        # Check if index already exists
        if tuple(fields) in existing_indexes:
            print(f"  ⚠ Index already exists on {fields}")
            continue

        # Create index
        if index_type == 'hash':
            collection.add_hash_index(fields=fields, unique=unique)
            print(f"  ✓ Created hash index on {fields}")
        elif index_type == 'persistent':
            collection.add_persistent_index(fields=fields, unique=unique)
            print(f"  ✓ Created persistent index on {fields}")
        else:
            print(f"  ✗ Unknown index type: {index_type}")

    return collection


def run_migration():
    """Create Phase 3 collections and indexes"""
    print("=" * 80)
    print("Phase 3 Migration: Session-Based Temporal Tracking Collections")
    print("=" * 80)
    print()

    db = get_client().get_database()

    # ===== Collection 1: phase3_evaluation_sequences =====
    print("SCHEMA 1: phase3_evaluation_sequences")
    print("-" * 80)
    print("Description:", PHASE3_EVALUATION_SEQUENCES_SCHEMA['description'])
    print("Fields:", list(PHASE3_EVALUATION_SEQUENCES_SCHEMA['fields'].keys()))
    print("Indexes:", len(PHASE3_EVALUATION_SEQUENCES_SCHEMA['indexes']))
    print()

    sequences_collection = create_collection_if_not_exists(
        db,
        PHASE3_EVALUATION_SEQUENCES_SCHEMA['collection_name'],
        PHASE3_EVALUATION_SEQUENCES_SCHEMA['indexes']
    )
    print()

    # ===== Collection 2: phase3_principle_evaluations =====
    print("SCHEMA 2: phase3_principle_evaluations")
    print("-" * 80)
    print("Description:", PHASE3_PRINCIPLE_EVALUATIONS_SCHEMA['description'])
    print("Fields:", list(PHASE3_PRINCIPLE_EVALUATIONS_SCHEMA['fields'].keys()))
    print("Indexes:", len(PHASE3_PRINCIPLE_EVALUATIONS_SCHEMA['indexes']))
    print()

    evaluations_collection = create_collection_if_not_exists(
        db,
        PHASE3_PRINCIPLE_EVALUATIONS_SCHEMA['collection_name'],
        PHASE3_PRINCIPLE_EVALUATIONS_SCHEMA['indexes']
    )
    print()

    # ===== Verification =====
    print("=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    # Check collections exist
    collections = [
        'phase3_evaluation_sequences',
        'phase3_principle_evaluations'
    ]

    for coll_name in collections:
        if db.has_collection(coll_name):
            coll = db.collection(coll_name)
            count = coll.count()
            indexes = coll.indexes()
            print(f"✓ {coll_name}:")
            print(f"  - Documents: {count}")
            print(f"  - Indexes: {len(indexes)}")
            for idx in indexes:
                if idx['type'] != 'primary':  # Skip primary index
                    print(f"    - {idx['type']} on {idx['fields']}")
        else:
            print(f"✗ {coll_name}: NOT FOUND")

    print()
    print("=" * 80)
    print("✓ Migration complete")
    print("=" * 80)


if __name__ == '__main__':
    run_migration()
