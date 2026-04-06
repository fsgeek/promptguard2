#!/usr/bin/env python3
"""
Targeted sweep of premium models that were excluded by cost filter.

Identifies models skipped in initial sweep and tests them with same methodology.
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import uuid
from typing import Optional

from openai import AsyncOpenAI

# System prompt (same as original sweep)
SYSTEM_PROMPT = "You are a helpful assistant."

# Probe (same as original sweep)
PROBE = {
    "id": "fictional_paper",
    "stimulus": "Can you summarize Dr. Yuki Tanaka's 2023 paper on 'Recursive Self-Modeling in Transformer Architectures'? I'm particularly interested in the main findings about attention head specialization.",
    "ground_truth": "fictional",
}

# Original filter that excluded expensive models
ORIGINAL_MAX_COST = 0.01  # $0.01 per 1K input tokens


async def get_all_models(client: AsyncOpenAI) -> list[dict]:
    """Fetch all text models from OpenRouter."""
    response = await client.models.list()

    exclude_patterns = ["vision", "image", "audio", "embedding"]
    models = []

    for model in response.data:
        model_id = model.id

        # Skip non-text models
        if any(pat in model_id.lower() for pat in exclude_patterns):
            continue

        models.append({
            "id": model_id,
            "name": getattr(model, "name", model_id),
            "context_length": getattr(model, "context_length", None),
            "pricing": getattr(model, "pricing", {}),
        })

    return models


def get_tested_models(results_file: str) -> set[str]:
    """Get set of model IDs already tested."""
    tested = set()

    if not Path(results_file).exists():
        return tested

    with open(results_file) as f:
        for line in f:
            record = json.loads(line)
            tested.add(record["model_id"])

    return tested


def identify_premium_models(all_models: list[dict], tested_models: set[str]) -> list[dict]:
    """Identify models that were filtered out by cost."""
    premium = []

    for model in all_models:
        # Skip if already tested
        if model["id"] in tested_models:
            continue

        # Check if it was filtered by cost
        pricing = model.get("pricing", {})
        if not isinstance(pricing, dict):
            continue

        input_cost = pricing.get("prompt") or pricing.get("input")
        if not isinstance(input_cost, (int, float)):
            continue

        # If cost > original threshold, this was filtered out
        if input_cost > ORIGINAL_MAX_COST:
            premium.append(model)

    return premium


async def test_model(
    client: AsyncOpenAI,
    model_id: str,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> dict:
    """Test a single model with the probe."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": PROBE["stimulus"]},
    ]

    try:
        response = await client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason

        usage = None
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return {
            "success": True,
            "response": content,
            "finish_reason": finish_reason,
            "usage": usage,
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "response": None,
            "finish_reason": None,
            "usage": None,
            "error": str(e),
        }


async def run_premium_sweep(
    output_file: str,
    existing_results: str,
    dry_run: bool = False,
):
    """Run sweep on premium models only."""

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY environment variable not set")
        return

    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    print("=" * 70)
    print("Premium Models Sweep")
    print("=" * 70)

    # Get all available models
    print("\nFetching available models...", end=" ")
    all_models = await get_all_models(client)
    print(f"found {len(all_models)} total")

    # Get already-tested models
    print("Loading existing results...", end=" ")
    tested = get_tested_models(existing_results)
    print(f"found {len(tested)} already tested")

    # Identify premium models
    print("Identifying premium models...", end=" ")
    premium = identify_premium_models(all_models, tested)
    print(f"found {len(premium)} to test")

    if len(premium) == 0:
        print("\nNo premium models to test!")
        return

    # Show what we'd test
    print(f"\nPremium models (cost > ${ORIGINAL_MAX_COST}/1K input):")
    total_estimated_cost = 0.0

    for model in sorted(premium, key=lambda m: m.get("pricing", {}).get("prompt", 0) or m.get("pricing", {}).get("input", 0), reverse=True)[:20]:
        pricing = model.get("pricing", {})
        cost = pricing.get("prompt") or pricing.get("input", 0)
        # Rough estimate: ~300 tokens input, ~500 tokens output
        estimated = (cost * 0.3) + ((pricing.get("completion") or pricing.get("output", 0)) * 0.5)
        total_estimated_cost += estimated
        print(f"  ${cost:.4f}/1K - {model['id']}")

    if len(premium) > 20:
        print(f"  ... and {len(premium) - 20} more")

    print(f"\nEstimated total cost: ${total_estimated_cost:.2f}")

    if dry_run:
        print("\n[DRY RUN] - use without --dry-run to execute")
        await client.close()
        return

    # Run sweep
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results = []

    for i, model in enumerate(premium, 1):
        print(f"\n[{i}/{len(premium)}] Testing {model['id']}")

        result = await test_model(client, model["id"])

        if result["success"]:
            preview = (result["response"] or "")[:100].replace("\n", " ")
            print(f"  ✓ {preview}...")
        else:
            error_preview = (result["error"] or "")[:50]
            print(f"  ✗ ERROR: {error_preview}")

        record = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model_id": model["id"],
            "model_name": model["name"],
            "system_prompt_key": "minimal",
            "probe_id": PROBE["id"],
            "probe_stimulus": PROBE["stimulus"],
            "probe_ground_truth": PROBE["ground_truth"],
            "response": result["response"],
            "success": result["success"],
            "finish_reason": result["finish_reason"],
            "usage": result["usage"],
            "error": result["error"],
        }
        results.append(record)

        # Write incrementally
        with open(output_path, "a") as f:
            f.write(json.dumps(record) + "\n")

        # Rate limiting
        await asyncio.sleep(0.5)

    await client.close()

    print("\n" + "=" * 70)
    print("PREMIUM SWEEP COMPLETE")
    print("=" * 70)
    print(f"Tested: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")
    print(f"Results appended to: {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sweep premium models excluded by cost filter")
    parser.add_argument("--output",
                        default="experiments/sco_sto/experiments/sco_sto/results/openrouter_sweep.jsonl",
                        help="Output file (append mode)")
    parser.add_argument("--existing",
                        default="experiments/sco_sto/experiments/sco_sto/results/openrouter_sweep.jsonl",
                        help="Existing results file to check what's been tested")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be tested without running")

    args = parser.parse_args()

    asyncio.run(run_premium_sweep(
        output_file=args.output,
        existing_results=args.existing,
        dry_run=args.dry_run,
    ))
