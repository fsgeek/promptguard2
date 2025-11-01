"""
Migrate Observer Prompts from Old PromptGuard
FR4: Step 2 Pre-filter Collection
Constitutional Principle VI: Data Provenance
Constitutional Principle IV: Fail-Fast

Migrates observer prompt v2.1 from old PromptGuard prompt_configurations collection.
"""

import os
from datetime import datetime
from arango import ArangoClient
from src.database.client import get_client
from src.database.schemas.observer_prompts import create_observer_prompts_collection, ObserverPrompt


def get_old_promptguard_client():
    """
    Connect to old PromptGuard database.

    Assumes same ArangoDB instance, different database name.
    """
    host = os.getenv("ARANGODB_HOST", "192.168.111.125")
    port = int(os.getenv("ARANGODB_PORT", "8529"))
    username = os.getenv("ARANGODB_USERNAME", "pgtest")
    password = os.getenv("ARANGODB_PROMPTGUARD_PASSWORD")

    if not password:
        raise ValueError("ARANGODB_PROMPTGUARD_PASSWORD not set")

    client = ArangoClient(hosts=f"http://{host}:{port}")

    # Old PromptGuard database name
    old_db_name = "PromptGuard"

    # Connect directly (fail-fast if database doesn't exist)
    try:
        old_db = client.db(old_db_name, username=username, password=password)
        # Test connection by attempting a simple query
        old_db.version()
        return old_db
    except Exception as e:
        raise ValueError(f"Cannot connect to old PromptGuard database '{old_db_name}': {e}") from e


def migrate_observer_prompt_v2_1(dry_run: bool = False) -> dict:
    """
    Migrate observer prompt v2.1 from old PromptGuard.

    Query criteria from spec:
    - prompt_type="pre_eval"
    - version=1
    - created ~2025-10-24

    Args:
        dry_run: If True, don't insert, just show what would be migrated

    Returns:
        Migration result dict

    Raises:
        ValueError: If prompt not found or validation fails (fail-fast)
    """
    # Connect to old database
    old_db = get_old_promptguard_client()

    # Query for observer prompt
    aql = """
    FOR prompt IN prompt_configurations
        FILTER prompt.prompt_type == "pre_eval"
        FILTER prompt.version == 1
        SORT prompt.created DESC
        LIMIT 1
        RETURN prompt
    """

    cursor = old_db.aql.execute(aql)
    results = list(cursor)

    if not results:
        raise ValueError(
            "Observer prompt not found in old PromptGuard. "
            "Expected: prompt_type='pre_eval', version=1"
        )

    old_prompt = results[0]

    # Validate prompt_text exists and is non-empty
    if not old_prompt.get("prompt_text"):
        raise ValueError("Observer prompt has empty prompt_text")

    prompt_text = old_prompt["prompt_text"]

    # Validate content (should contain observer framing keywords)
    required_keywords = ["observing", "neutrosophic"]
    missing_keywords = [kw for kw in required_keywords if kw.lower() not in prompt_text.lower()]

    if missing_keywords:
        raise ValueError(
            f"Observer prompt missing expected keywords: {missing_keywords}. "
            f"Prompt may not be the correct version."
        )

    # Prepare new document for PromptGuard2
    new_doc = ObserverPrompt(
        key="v2.1_observer_framing",
        prompt_text=prompt_text,
        version="2.1",
        description="Observer framing prompt for neutrosophic evaluation (migrated from PromptGuard v1)",
        created=old_prompt.get("created", datetime.utcnow().isoformat() + "Z"),
        created_by=old_prompt.get("created_by", "Unknown (migrated)"),
        parameters={
            "detection_threshold": 0.7,
            "original_version": old_prompt.get("version", 1),
            "original_prompt_type": old_prompt.get("prompt_type", "pre_eval"),
            "migration_date": datetime.utcnow().isoformat() + "Z"
        }
    )

    if dry_run:
        print("DRY RUN - Would migrate:")
        print(f"  Version: {new_doc.version}")
        print(f"  Created: {new_doc.created}")
        print(f"  Created by: {new_doc.created_by}")
        print(f"  Prompt length: {len(new_doc.prompt_text)} chars")
        print(f"  Keywords validated: {required_keywords}")
        return {
            "dry_run": True,
            "would_migrate": new_doc.model_dump(by_alias=True)
        }

    # Insert to PromptGuard2
    client = get_client()
    new_db = client.get_database()

    # Ensure collection exists
    create_observer_prompts_collection(new_db)

    collection = new_db.collection("observer_prompts")

    try:
        # Insert (fail if already exists - don't overwrite)
        result = collection.insert(new_doc.model_dump(by_alias=True), overwrite=False)
        print(f"✅ Migrated observer prompt v2.1: {result['_key']}")
        return {
            "success": True,
            "key": result["_key"],
            "prompt_length": len(prompt_text),
            "created": new_doc.created,
            "created_by": new_doc.created_by
        }

    except Exception as e:
        if "unique constraint" in str(e).lower() or "duplicate" in str(e).lower():
            print("⚠ Observer prompt v2.1 already exists in PromptGuard2")
            return {
                "success": True,
                "already_exists": True,
                "key": "v2.1_observer_framing"
            }
        else:
            raise  # Fail-fast on unexpected errors


def verify_observer_prompt_migration() -> dict:
    """
    Verify observer prompt migration per T042a.

    Checks:
    1. Prompt exists with key "v2.1_observer_framing"
    2. prompt_text contains expected keywords
    3. Validates against spec definition

    Returns:
        Verification result dict

    Raises:
        ValueError: If verification fails (fail-fast)
    """
    client = get_client()
    db = client.get_database()

    collection = db.collection("observer_prompts")

    # Query for v2.1 prompt
    try:
        doc = collection.get("v2.1_observer_framing")
    except Exception as e:
        raise ValueError(f"Observer prompt v2.1 not found: {e}")

    if not doc:
        raise ValueError("Observer prompt v2.1 not found in observer_prompts collection")

    prompt_text = doc.get("prompt_text", "")

    # Validate expected content
    expected_phrases = [
        "observing an exchange",
        "neutrosophic logic"
    ]

    missing_phrases = []
    for phrase in expected_phrases:
        if phrase.lower() not in prompt_text.lower():
            missing_phrases.append(phrase)

    if missing_phrases:
        raise ValueError(
            f"Observer prompt v2.1 missing expected phrases: {missing_phrases}. "
            f"This may not be the correct observer framing prompt."
        )

    # Additional validation: neutral reciprocity framing
    # Should NOT contain directive language like "you must refuse" or "you should comply"
    problematic_phrases = ["you must refuse", "you should comply", "never provide"]

    found_problematic = []
    for phrase in problematic_phrases:
        if phrase.lower() in prompt_text.lower():
            found_problematic.append(phrase)

    if found_problematic:
        print(f"⚠ Warning: Observer prompt contains directive language: {found_problematic}")
        print("  This may bias evaluation toward refusal")

    print("✅ Observer prompt v2.1 verified:")
    print(f"  Key: {doc['_key']}")
    print(f"  Version: {doc.get('version', 'unknown')}")
    print(f"  Created: {doc.get('created', 'unknown')}")
    print(f"  Created by: {doc.get('created_by', 'unknown')}")
    print(f"  Prompt length: {len(prompt_text)} chars")
    print(f"  Expected phrases found: {expected_phrases}")

    return {
        "verified": True,
        "key": doc["_key"],
        "version": doc.get("version"),
        "prompt_length": len(prompt_text),
        "validation_passed": len(missing_phrases) == 0,
        "warnings": found_problematic if found_problematic else None
    }


if __name__ == "__main__":
    import sys

    if "--dry-run" in sys.argv:
        print("Running observer prompt migration (dry run)...\n")
        result = migrate_observer_prompt_v2_1(dry_run=True)
        print("\nDry run complete. Use without --dry-run to actually migrate.")

    elif "--verify" in sys.argv:
        print("Verifying observer prompt migration...\n")
        result = verify_observer_prompt_migration()

    else:
        print("Migrating observer prompt v2.1...\n")
        result = migrate_observer_prompt_v2_1(dry_run=False)
        print("\nMigration complete. Run with --verify to validate.")
