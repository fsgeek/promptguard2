"""
Gold Standard Annotation CLI
FR3: Compliance Classification
Constitutional Principle VII: Immutable reference dataset

Creates 50-sample stratified gold standard dataset for classifier validation.

Usage:
    uv run python -m src.cli.annotate_gold_standard --create
    uv run python -m src.cli.annotate_gold_standard --export-csv
    uv run python -m src.cli.annotate_gold_standard --import-csv path/to/reviewed.csv
"""

import sys
import csv
import asyncio
import os
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import random

from src.database.client import get_client
from src.database.schemas.gold_standard_classifications import (
    create_gold_standard_classifications_collection,
    GoldStandardClassification
)
from src.evaluation.classifiers.compliance import ComplianceClassifier
from src.logging.raw_logger import RawLogger


async def create_stratified_sample(db, sample_size: int = 50) -> List[Dict]:
    """
    Create stratified sample proportional to ground_truth distribution.

    Args:
        db: ArangoDB database connection
        sample_size: Total sample size (default 50)

    Returns:
        List of attack documents with associated baseline responses
    """
    # Get ground truth distribution
    aql_distribution = """
    FOR attack IN attacks
        COLLECT ground_truth = attack.ground_truth WITH COUNT INTO count
        RETURN {ground_truth: ground_truth, count: count}
    """
    cursor = db.aql.execute(aql_distribution)
    distribution = {item["ground_truth"]: item["count"] for item in cursor}

    total_attacks = sum(distribution.values())
    print(f"\n📊 Ground Truth Distribution (Total: {total_attacks}):")
    for gt, count in distribution.items():
        pct = (count / total_attacks) * 100
        print(f"  {gt}: {count} ({pct:.1f}%)")

    # Calculate stratified sample sizes
    samples_per_category = {}
    for gt, count in distribution.items():
        proportion = count / total_attacks
        samples_per_category[gt] = max(1, round(sample_size * proportion))

    print(f"\n🎯 Stratified Sample Sizes (Total target: {sample_size}):")
    actual_total = 0
    for gt, sample_count in samples_per_category.items():
        actual_total += sample_count
        print(f"  {gt}: {sample_count}")

    print(f"\nActual total: {actual_total} (adjusting if needed...)")

    # Adjust if total doesn't match exactly
    if actual_total != sample_size:
        diff = sample_size - actual_total
        # Add/remove from largest category
        largest_category = max(samples_per_category, key=samples_per_category.get)
        samples_per_category[largest_category] += diff
        print(f"Adjusted {largest_category}: {samples_per_category[largest_category]}")

    # Sample attacks from each category
    sampled_attacks = []

    for ground_truth, sample_count in samples_per_category.items():
        # Get all attacks for this category
        aql_attacks = f"""
        FOR attack IN attacks
            FILTER attack.ground_truth == @ground_truth
            RETURN attack
        """
        cursor = db.aql.execute(aql_attacks, bind_vars={"ground_truth": ground_truth})
        attacks_in_category = list(cursor)

        # Random sample
        if len(attacks_in_category) <= sample_count:
            sampled = attacks_in_category
        else:
            sampled = random.sample(attacks_in_category, sample_count)

        sampled_attacks.extend(sampled)

    print(f"\n✅ Sampled {len(sampled_attacks)} attacks")

    # For each attack, get one baseline response (prefer first available model)
    items = []
    for attack in sampled_attacks:
        attack_id = attack["_key"]

        # Get first available baseline response
        aql_response = """
        FOR response IN step1_baseline_responses
            FILTER response.attack_id == @attack_id
            LIMIT 1
            RETURN response
        """
        cursor = db.aql.execute(aql_response, bind_vars={"attack_id": attack_id})
        responses = list(cursor)

        if not responses:
            print(f"⚠ Warning: No baseline response for attack {attack_id}, skipping")
            continue

        response = responses[0]

        items.append({
            "attack_id": attack_id,
            "attack": attack,
            "response": response
        })

    print(f"✅ Found baseline responses for {len(items)} attacks\n")
    return items


async def annotate_gold_standard(db, items: List[Dict]):
    """
    Annotate gold standard samples using Claude.

    Args:
        db: ArangoDB database connection
        items: List of attack+response items
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")

    # Load classifier config
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "config" / "experiments.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    classifier_config = config["classifiers"]["compliance"]
    classifier = ComplianceClassifier(
        openrouter_api_key=api_key,
        model=classifier_config["model"],
        temperature=classifier_config.get("temperature", 0.0),
        max_tokens=classifier_config.get("max_tokens", 1000)
    )

    # Raw logger for provenance
    raw_logger = RawLogger(
        experiment_id="gold_standard_annotation",
        data_dir=project_root / "data" / "experiments"
    )

    print(f"🤖 Annotating with {classifier_config['model']}...")
    print(f"Total items: {len(items)}\n")

    annotations = []

    for i, item in enumerate(items, 1):
        attack = item["attack"]
        response = item["response"]

        print(f"[{i}/{len(items)}] {attack['_key']} ({attack['ground_truth']})...", end=" ")

        try:
            result = await classifier.classify_for_gold_standard(
                input_prompt=attack["prompt_text"],
                llm_response=response["response_text"],
                ground_truth=attack["ground_truth"],
                target_model=response["target_model"],
                raw_logger=None,  # Skip raw logging for gold standard (data is in DB)
                metadata={
                    "attack_id": attack["_key"],
                    "target_model": response["target_model"]
                }
            )

            annotation = GoldStandardClassification(
                key=attack["_key"],
                attack_id=attack["_key"],
                prompt_text=attack["prompt_text"],
                response_text=response["response_text"],
                ground_truth=attack["ground_truth"],
                target_model=response["target_model"],
                claude_classification=result.classification,
                claude_reasoning=result.reasoning,
                tony_review_status="pending",
                final_classification=result.classification,  # Will be overridden if Tony rejects
                created=datetime.utcnow().isoformat() + "Z"
            )

            annotations.append(annotation)
            print(f"✅ {result.classification}")

        except Exception as e:
            # Log error but continue - partial gold standard is useful
            error_msg = str(e)
            if len(error_msg) > 200:
                error_msg = error_msg[:200] + "..."
            print(f"❌ Error: {error_msg}")
            # Continue to next item instead of failing fast

    # Insert to database
    print(f"\n💾 Inserting {len(annotations)} annotations to database...")

    collection = db.collection("gold_standard_classifications")

    for annotation in annotations:
        doc = annotation.model_dump(by_alias=True)
        try:
            collection.insert(doc, overwrite=False)
        except Exception as e:
            if "unique constraint" in str(e).lower():
                print(f"⚠ {annotation.key} already exists, skipping")
            else:
                raise

    print("✅ Gold standard annotations created\n")


async def export_to_csv(db, output_path: str):
    """
    Export gold standard to CSV for Tony's review.

    Args:
        db: ArangoDB database connection
        output_path: Path to output CSV file
    """
    aql = """
    FOR doc IN gold_standard_classifications
        SORT doc.ground_truth, doc._key
        RETURN doc
    """
    cursor = db.aql.execute(aql)
    docs = list(cursor)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "attack_id",
            "ground_truth",
            "target_model",
            "prompt_text",
            "response_text",
            "claude_classification",
            "claude_reasoning",
            "tony_review_status",
            "tony_override",
        ])
        writer.writeheader()

        for doc in docs:
            writer.writerow({
                "attack_id": doc["_key"],
                "ground_truth": doc["ground_truth"],
                "target_model": doc["target_model"],
                "prompt_text": doc["prompt_text"],
                "response_text": doc["response_text"],
                "claude_classification": doc["claude_classification"],
                "claude_reasoning": doc["claude_reasoning"],
                "tony_review_status": doc.get("tony_review_status", "pending"),
                "tony_override": doc.get("tony_override", ""),
            })

    print(f"✅ Exported {len(docs)} gold standard annotations to {output_path}")
    print(f"\n📝 Review the CSV and update:")
    print(f"  - tony_review_status: 'approved' or 'rejected'")
    print(f"  - tony_override: classification if rejected (comply/refuse/unclear)")
    print(f"\nThen import with: uv run python -m src.cli.annotate_gold_standard --import-csv {output_path}\n")


async def import_from_csv(db, input_path: str):
    """
    Import Tony's reviewed gold standard from CSV.

    Args:
        db: ArangoDB database connection
        input_path: Path to reviewed CSV file
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    collection = db.collection("gold_standard_classifications")

    approved_count = 0
    rejected_count = 0

    for row in rows:
        attack_id = row["attack_id"]
        review_status = row["tony_review_status"]
        override = row.get("tony_override", "").strip()

        if review_status == "approved":
            approved_count += 1
            final_classification = row["claude_classification"]
        elif review_status == "rejected":
            if not override:
                print(f"⚠ {attack_id}: rejected but no override provided, skipping")
                continue
            rejected_count += 1
            final_classification = override
        else:
            print(f"⚠ {attack_id}: unknown status '{review_status}', skipping")
            continue

        # Update document
        collection.update(
            {"_key": attack_id},
            {
                "tony_review_status": review_status,
                "tony_override": override if override else None,
                "final_classification": final_classification,
                "reviewed": datetime.utcnow().isoformat() + "Z"
            }
        )

    print(f"\n✅ Imported reviews:")
    print(f"  Approved: {approved_count}")
    print(f"  Rejected with override: {rejected_count}")
    print(f"  Total: {approved_count + rejected_count}\n")


async def main_async():
    """Async main function."""
    create_flag = "--create" in sys.argv
    export_flag = "--export-csv" in sys.argv
    import_flag = "--import-csv" in sys.argv

    # Get database client
    client = get_client()
    db = client.get_database()

    # Ensure collection exists
    create_gold_standard_classifications_collection(db)

    if create_flag:
        # Create and annotate gold standard
        items = await create_stratified_sample(db, sample_size=50)
        await annotate_gold_standard(db, items)

    elif export_flag:
        # Export to CSV
        output_path = "gold_standard_review.csv"
        await export_to_csv(db, output_path)

    elif import_flag:
        # Import reviewed CSV
        idx = sys.argv.index("--import-csv")
        if idx + 1 >= len(sys.argv):
            print("❌ Error: --import-csv requires path argument")
            return

        input_path = sys.argv[idx + 1]
        await import_from_csv(db, input_path)

    else:
        print("Usage:")
        print("  Create gold standard: uv run python -m src.cli.annotate_gold_standard --create")
        print("  Export to CSV: uv run python -m src.cli.annotate_gold_standard --export-csv")
        print("  Import reviewed CSV: uv run python -m src.cli.annotate_gold_standard --import-csv path/to/reviewed.csv")


def main():
    """Entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
