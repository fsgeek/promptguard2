"""
Step 2 Pre-filter Collection CLI
FR4: Command-line interface for observer framing pre-filter collection

Supports:
- --test-mode --samples 5: Test on 5 samples
- --observer-model: Specify observer model (default: Claude 3.5 Haiku)
- --full: Run full collection (762 evaluations)
"""

import sys
import asyncio
import yaml
from pathlib import Path

from src.database.client import get_client
from src.database.schemas.step2_pre_evaluations import create_step2_pre_evaluations_collection
from src.evaluation.step2_prefilter import run_step2_prefilter
from src.logging.experiment_logger import ExperimentLogger


async def main_async():
    """Async main function."""
    # Parse arguments
    test_mode = "--test-mode" in sys.argv
    samples = 5  # Default for test mode
    full = "--full" in sys.argv
    observer_model = "anthropic/claude-3.5-haiku"  # Default

    # Parse --samples N
    if "--samples" in sys.argv:
        idx = sys.argv.index("--samples")
        if idx + 1 < len(sys.argv):
            samples = int(sys.argv[idx + 1])

    # Parse --observer-model MODEL
    if "--observer-model" in sys.argv:
        idx = sys.argv.index("--observer-model")
        if idx + 1 < len(sys.argv):
            observer_model = sys.argv[idx + 1]

    # Load configuration
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "config" / "experiments.yaml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    experiment_config = config["experiments"]["exp_phase1_step2_pre_filter_v1"]
    experiment_id = "exp_phase1_step2_pre_filter_v1"
    target_models = experiment_config["parameters"]["target_models"]
    temperature = experiment_config["parameters"]["temperature"]
    max_tokens = experiment_config["parameters"]["max_tokens"]

    # Get database client
    client = get_client()
    db = client.get_database()

    # Ensure collection exists
    create_step2_pre_evaluations_collection(db)

    # Get attacks to evaluate
    if test_mode:
        print(f"\n🧪 TEST MODE: Evaluating {samples} samples")
        # Get random sample
        aql = f"""
        FOR attack IN attacks
            LIMIT {samples}
            RETURN attack._key
        """
        cursor = db.aql.execute(aql)
        attack_ids = list(cursor)
    else:
        # Full collection
        aql = """
        FOR attack IN attacks
            RETURN attack._key
        """
        cursor = db.aql.execute(aql)
        attack_ids = list(cursor)

    # Get target models excluding observer
    from src.database.utils import normalize_model_slug
    observer_slug = normalize_model_slug(observer_model)
    filtered_targets = [
        m for m in target_models
        if normalize_model_slug(m) != observer_slug
    ]

    if len(filtered_targets) < len(target_models):
        excluded = len(target_models) - len(filtered_targets)
        print(f"⚠ Excluded {excluded} target model(s) matching observer")

    total_observer_evals = len(attack_ids)  # One observer eval per attack
    max_target_evals = len(attack_ids) * len(filtered_targets)  # If no attacks detected

    print(f"\n{'='*60}")
    print(f"STEP 2 PRE-FILTER COLLECTION")
    print(f"{'='*60}")
    print(f"Experiment: {experiment_id}")
    print(f"Observer model: {observer_model}")
    print(f"Target models: {', '.join(filtered_targets)}")
    print(f"Total attacks: {len(attack_ids)}")
    print(f"Observer evaluations: {total_observer_evals}")
    print(f"Max target evaluations: {max_target_evals} (if 0% detected)")
    print(f"Temperature: {temperature}, Max tokens: {max_tokens}\n")

    # Create or update experiment
    exp_logger = ExperimentLogger(db)
    existing = exp_logger.get_experiment(experiment_id)
    if not existing:
        exp_logger.start_experiment(
            experiment_id=experiment_id,
            phase=experiment_config["phase"],
            step=experiment_config["step"],
            description=experiment_config["description"],
            parameters={
                **experiment_config["parameters"],
                "observer_model": observer_model
            },
        )

    # Confirmation for full run
    if full and not test_mode:
        print(f"⚠ Full collection will run {total_observer_evals} observer evaluations")
        print(f"  + up to {max_target_evals} target evaluations")
        print(f"\nProceed? [y/N]: ", end="")
        response = input().strip().lower()
        if response != "y":
            print("Aborted.")
            return

    # Run collection
    print("\n" + "="*60)
    print("Starting Step 2 collection...")
    print("="*60 + "\n")

    results = await run_step2_prefilter(
        db=db,
        attack_ids=attack_ids,
        observer_model=observer_model,
        target_models=filtered_targets,
        experiment_id=experiment_id,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    print("\n" + "="*60)
    print("COLLECTION COMPLETE")
    print("="*60)
    print(f"Total attacks: {results['total']}")
    print(f"Detected by observer: {results['detected']} ({(results['detected']/results['total'])*100:.1f}%)")
    print(f"Passed to targets: {results['passed']} ({(results['passed']/results['total'])*100:.1f}%)")
    print(f"Reused Step 1 responses: {results['reused_step1']}")
    print(f"Errors: {results['errors']}")

    if results['errors'] > 0:
        print(f"\n⚠ {results['errors']} errors occurred:")
        for error in results['error_details'][:5]:  # Show first 5
            print(f"  {error['attack_id']}: {error['error']}")
        if len(results['error_details']) > 5:
            print(f"  ... and {len(results['error_details']) - 5} more")

    # Update experiment status
    exp_logger.complete_experiment(
        experiment_id=experiment_id,
        results={
            "total_attacks": results["total"],
            "detected": results["detected"],
            "passed": results["passed"],
            "detection_rate": (results["detected"] / results["total"]) * 100 if results["total"] > 0 else 0,
            "reused_step1": results["reused_step1"],
            "errors": results["errors"]
        }
    )

    print(f"\n✅ Experiment {experiment_id} complete")


def main():
    """Entry point."""
    if len(sys.argv) == 1 or "--help" in sys.argv:
        print("Step 2 Pre-filter Collection CLI")
        print("\nUsage:")
        print("  Test mode (5 samples):  uv run python -m src.cli.step2 --test-mode")
        print("  Test mode (N samples):  uv run python -m src.cli.step2 --test-mode --samples N")
        print("  Full collection:        uv run python -m src.cli.step2 --full")
        print("\nOptions:")
        print("  --observer-model MODEL  Specify observer model (default: anthropic/claude-3.5-haiku)")
        print("  --test-mode             Run on sample of attacks")
        print("  --samples N             Number of samples for test mode (default: 5)")
        print("  --full                  Run on all 762 attacks")
        return

    asyncio.run(main_async())


if __name__ == "__main__":
    main()
