"""
Step 1 Baseline Collection CLI
FR2: Command-line interface for baseline data collection

Supports:
- --test-mode --samples 5: Test on 5 samples
- --resume: Resume from checkpoint
- --full: Run full collection (3,810 evaluations)
"""

import sys
import asyncio
import yaml
from pathlib import Path

from src.database.client import get_client
from src.database.schemas.step1_baseline_responses import create_step1_baseline_responses_collection
from src.evaluation.step1_baseline import run_step1_baseline
from src.evaluation.checkpoint import CheckpointManager
from src.logging.experiment_logger import ExperimentLogger


async def main_async():
    """Async main function."""
    # Parse arguments
    test_mode = "--test-mode" in sys.argv
    samples = 5  # Default for test mode
    resume = "--resume" in sys.argv
    full = "--full" in sys.argv
    status = "--status" in sys.argv

    # Parse --samples N
    if "--samples" in sys.argv:
        idx = sys.argv.index("--samples")
        if idx + 1 < len(sys.argv):
            samples = int(sys.argv[idx + 1])

    # Load configuration
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "config" / "experiments.yaml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    experiment_config = config["experiments"]["exp_phase1_step1_baseline_v1"]
    experiment_id = "exp_phase1_step1_baseline_v1"
    target_models = experiment_config["parameters"]["target_models"]
    temperature = experiment_config["parameters"]["temperature"]
    max_tokens = experiment_config["parameters"]["max_tokens"]

    # Get database client
    client = get_client()
    db = client.get_database()

    # Ensure collection exists
    create_step1_baseline_responses_collection(db)

    # Checkpoint manager
    checkpoint_mgr = CheckpointManager(experiment_id=experiment_id)

    # Status command
    if status:
        stats = checkpoint_mgr.get_stats()
        print("="*60)
        print("STEP 1 BASELINE COLLECTION STATUS")
        print("="*60)
        print(f"Experiment: {experiment_id}")
        print(f"Completed attacks: {stats['completed_count']}")
        print(f"Failed attacks: {stats['failed_count']}")
        print(f"Started: {stats['started']}")
        print(f"Last updated: {stats['last_updated']}")
        return

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
    elif resume:
        # Get incomplete attacks from checkpoint
        checkpoint = checkpoint_mgr.load()
        completed = set(checkpoint["completed_attacks"])

        aql = """
        FOR attack IN attacks
            RETURN attack._key
        """
        cursor = db.aql.execute(aql)
        all_attacks = set(cursor)

        attack_ids = list(all_attacks - completed)
        print(f"\n🔄 RESUME MODE: {len(attack_ids)} attacks remaining")
    else:
        # Full collection
        aql = """
        FOR attack IN attacks
            RETURN attack._key
        """
        cursor = db.aql.execute(aql)
        attack_ids = list(cursor)

    total_evaluations = len(attack_ids) * len(target_models)

    print(f"Target models: {', '.join(target_models)}")
    print(f"Total attacks: {len(attack_ids)}")
    print(f"Total evaluations: {total_evaluations}")
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
            parameters=experiment_config["parameters"],
        )

    # Create checkpoint if not resuming
    if not resume:
        try:
            checkpoint_mgr.create()
        except FileExistsError:
            if not test_mode:
                print("⚠ Checkpoint exists. Use --resume to continue or delete checkpoint to restart.")
                return

    # Run collection
    print("Starting collection...")
    results = await run_step1_baseline(
        db=db,
        attack_ids=attack_ids,
        target_models=target_models,
        experiment_id=experiment_id,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    print("\n" + "="*60)
    print("COLLECTION COMPLETE")
    print("="*60)
    print(f"Completed: {results['completed']}")
    print(f"Failed: {results['failed']}")
    print(f"Total: {results['total']}")
    print(f"Success rate: {results['stats']['success_rate']:.1%}")

    # Interactive confirmation for full run (if test mode succeeded)
    if test_mode and not full:
        print("\n" + "="*60)
        response = input(f"Test mode successful. Proceed with full collection ({762 * len(target_models)} evals)? [y/N]: ")
        if response.lower() in ['y', 'yes']:
            print("\nRun: python -m src.cli.step1 --full")
        else:
            print("Aborting full collection.")

    # Mark experiment complete if full run
    if full or (not test_mode and not resume):
        exp_logger.complete_experiment(experiment_id, status="completed")


def main():
    """CLI entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
