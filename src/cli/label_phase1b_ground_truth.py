"""
Add ground_truth labels to Phase 1B curated prompts collection.

Maps (is_adversarial, attack_type, source_dataset) → ground_truth taxonomy:
- "manipulative": Prompts that attempt to manipulate system behavior
- "extractive": Prompts that attempt to extract sensitive information
- "reciprocal": Normal, benign prompts
- "borderline": Ambiguous cases requiring manual review

Usage:
    # Test on sample
    uv run python -m src.cli.label_phase1b_ground_truth --test-mode --samples 50

    # Label all prompts
    uv run python -m src.cli.label_phase1b_ground_truth --label-all

    # Show distribution only (no changes)
    uv run python -m src.cli.label_phase1b_ground_truth --show-distribution
"""

import sys
from typing import Dict, List, Tuple
from datetime import datetime, UTC

from src.database.client import get_client


def determine_ground_truth(is_adversarial: bool, attack_type: str, source_dataset: str) -> Tuple[str, str]:
    """
    Determine ground_truth label based on existing metadata.

    Returns:
        Tuple of (ground_truth_label, reasoning)
    """
    # Non-adversarial prompts are reciprocal
    if not is_adversarial:
        return "reciprocal", f"is_adversarial=false"

    # Adversarial prompts - map by attack_type
    if attack_type == "prompt_injection":
        # Prompt injection = manipulative (trying to override instructions)
        return "manipulative", f"attack_type=prompt_injection"

    elif attack_type == "jailbreak":
        # Jailbreaks try to manipulate safety constraints
        return "manipulative", f"attack_type=jailbreak"

    elif attack_type == "ignore_instruction":
        # Extraction attempts (e.g., Gandalf password extraction)
        return "extractive", f"attack_type=ignore_instruction from {source_dataset}"

    elif attack_type == "harmful_behavior":
        # Harmful behavior requests are manipulative
        # (trying to get system to produce harmful content)
        return "manipulative", f"attack_type=harmful_behavior from {source_dataset}"

    else:
        # Unknown attack type - flag for manual review
        return "borderline", f"Unknown attack_type: {attack_type}"


def label_prompts(db, test_mode: bool = False, samples: int = 50, dry_run: bool = False):
    """
    Label Phase 1B prompts with ground_truth field.

    Args:
        db: ArangoDB database connection
        test_mode: If True, only label a sample
        samples: Number of samples for test mode
        dry_run: If True, show what would be done without making changes
    """
    collection = db.collection('phase1b_curated_prompts')

    # Get prompts to label
    if test_mode:
        aql = f"""
        FOR doc IN phase1b_curated_prompts
            LIMIT {samples}
            RETURN doc
        """
    else:
        aql = """
        FOR doc IN phase1b_curated_prompts
            RETURN doc
        """

    cursor = db.aql.execute(aql)
    prompts = list(cursor)

    print(f"\n{'='*60}")
    print(f"PHASE 1B GROUND TRUTH LABELING")
    print(f"{'='*60}")
    print(f"Total prompts to label: {len(prompts)}")
    print(f"Mode: {'TEST (sample)' if test_mode else 'FULL'}")
    print(f"Dry run: {dry_run}")
    print(f"{'='*60}\n")

    # Track statistics
    label_counts = {
        "manipulative": 0,
        "extractive": 0,
        "reciprocal": 0,
        "borderline": 0
    }

    examples_by_label = {
        "manipulative": [],
        "extractive": [],
        "reciprocal": [],
        "borderline": []
    }

    labeled_count = 0

    for i, doc in enumerate(prompts, 1):
        # Determine ground_truth label
        ground_truth, reasoning = determine_ground_truth(
            doc.get('is_adversarial', False),
            doc.get('attack_type', 'unknown'),
            doc.get('source_dataset', 'unknown')
        )

        label_counts[ground_truth] += 1

        # Collect examples (up to 3 per label)
        if len(examples_by_label[ground_truth]) < 3:
            examples_by_label[ground_truth].append({
                "_key": doc['_key'],
                "source": doc.get('source_dataset'),
                "attack_type": doc.get('attack_type'),
                "is_adversarial": doc.get('is_adversarial'),
                "ground_truth": ground_truth,
                "reasoning": reasoning,
                "prompt_preview": doc.get('prompt', '')[:150]
            })

        # Update document
        if not dry_run:
            collection.update({
                "_key": doc['_key'],
                "ground_truth": ground_truth,
                "ground_truth_reasoning": reasoning,
                "ground_truth_labeled_at": datetime.now(UTC).isoformat()
            })
            labeled_count += 1

        # Progress indicator
        if i % 50 == 0 or i == len(prompts):
            print(f"[{i}/{len(prompts)}] Processed...")

    # Print summary
    print(f"\n{'='*60}")
    print(f"LABELING SUMMARY")
    print(f"{'='*60}")
    print(f"Total prompts: {len(prompts)}")

    if not dry_run:
        print(f"Successfully labeled: {labeled_count}")
    else:
        print(f"Would label: {len(prompts)} (dry run)")

    print(f"\nGround Truth Distribution:")
    for label in ["manipulative", "extractive", "reciprocal", "borderline"]:
        count = label_counts[label]
        percentage = (count / len(prompts) * 100) if len(prompts) > 0 else 0
        print(f"  {label:15s}: {count:4d} ({percentage:5.1f}%)")

    # Show examples
    print(f"\n{'='*60}")
    print(f"EXAMPLES BY LABEL")
    print(f"{'='*60}")

    for label in ["manipulative", "extractive", "reciprocal", "borderline"]:
        examples = examples_by_label[label]
        if not examples:
            continue

        print(f"\n{label.upper()}:")
        for ex in examples:
            print(f"\n  {ex['_key']} ({ex['source']} / {ex['attack_type']} / is_adv={ex['is_adversarial']})")
            print(f"    Reasoning: {ex['reasoning']}")
            print(f"    Prompt: {ex['prompt_preview']}...")

    # Flag borderline cases
    if label_counts["borderline"] > 0:
        print(f"\n{'='*60}")
        print(f"⚠️  WARNING: {label_counts['borderline']} prompts flagged as BORDERLINE")
        print(f"{'='*60}")
        print("These prompts need manual review. Check examples above.")

    print(f"\n{'='*60}")
    if dry_run:
        print("✓ Dry run complete - no changes made")
    else:
        print("✓ Labeling complete")
    print(f"{'='*60}\n")

    return {
        "total_prompts": len(prompts),
        "labeled_count": labeled_count if not dry_run else 0,
        "distribution": label_counts,
        "examples": examples_by_label
    }


def show_distribution(db):
    """Show current distribution of ground_truth labels."""
    aql = """
    FOR doc IN phase1b_curated_prompts
        COLLECT ground_truth = doc.ground_truth WITH COUNT INTO count
        SORT count DESC
        RETURN {
            ground_truth: ground_truth,
            count: count
        }
    """

    results = list(db.aql.execute(aql))

    print(f"\n{'='*60}")
    print(f"CURRENT GROUND TRUTH DISTRIBUTION")
    print(f"{'='*60}")

    if not results or (len(results) == 1 and results[0]['ground_truth'] is None):
        print("No ground_truth labels found in collection.")
    else:
        total = sum(r['count'] for r in results)
        for r in results:
            label = r['ground_truth'] if r['ground_truth'] else "(unlabeled)"
            count = r['count']
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {label:15s}: {count:4d} ({percentage:5.1f}%)")

    print(f"{'='*60}\n")


def main():
    """Entry point."""
    # Parse arguments
    test_mode = "--test-mode" in sys.argv
    label_all = "--label-all" in sys.argv
    show_dist = "--show-distribution" in sys.argv
    dry_run = "--dry-run" in sys.argv

    samples = 50
    if "--samples" in sys.argv:
        idx = sys.argv.index("--samples")
        if idx + 1 < len(sys.argv):
            samples = int(sys.argv[idx + 1])

    # Get database connection
    client = get_client()
    db = client.get_database()

    if show_dist:
        show_distribution(db)
    elif test_mode:
        print(f"\n🧪 TEST MODE: Labeling {samples} sample prompts")
        if dry_run:
            print("   (DRY RUN - no changes will be made)")
        label_prompts(db, test_mode=True, samples=samples, dry_run=dry_run)
    elif label_all:
        print(f"\n🏷️  FULL LABELING: Labeling all Phase 1B prompts")
        if dry_run:
            print("   (DRY RUN - no changes will be made)")

        # Confirm unless dry run
        if not dry_run:
            response = input("\nThis will label all 950 prompts. Continue? (yes/no): ")
            if response.lower() != "yes":
                print("Aborted.")
                return

        label_prompts(db, test_mode=False, dry_run=dry_run)
    else:
        print("Usage:")
        print("  Show distribution:  uv run python -m src.cli.label_phase1b_ground_truth --show-distribution")
        print("  Test mode:          uv run python -m src.cli.label_phase1b_ground_truth --test-mode --samples 50 [--dry-run]")
        print("  Label all:          uv run python -m src.cli.label_phase1b_ground_truth --label-all [--dry-run]")
        print("\nOptions:")
        print("  --dry-run           Show what would be done without making changes")
        print("  --samples N         Number of samples for test mode (default: 50)")


if __name__ == "__main__":
    main()
