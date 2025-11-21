#!/usr/bin/env python3
"""
Generate assistant responses for MHJ sequences.

MHJ dataset contains only red-team prompts, not assistant responses.
This script generates responses by sending prompts to a target model.

Target model: Claude 3.5 Sonnet (to match real-world harm scenarios)

Usage:
    export OPENROUTER_API_KEY=your_key_here
    uv run python scripts/generate_mhj_responses.py
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from openai import AsyncOpenAI
from arango import ArangoClient

from src.pipeline.sequence_loader import SequenceLoader


async def generate_responses_for_sequence(
    client: AsyncOpenAI,
    sequence,
    model: str = "anthropic/claude-sonnet-4.5",
    temperature: float = 0.7,
):
    """Generate assistant responses for all turns in a sequence.

    Args:
        client: OpenAI client
        sequence: EvaluationSequence with user turns
        model: Model to generate responses
        temperature: Sampling temperature

    Returns:
        List of assistant responses (one per turn)
    """
    responses = []
    conversation_history = []

    for turn_num, user_turn in enumerate(sequence.turns, 1):
        # Build messages
        messages = [{"role": "user", "content": msg} if i % 2 == 0 else {"role": "assistant", "content": msg}
                    for i, msg in enumerate(conversation_history)]
        messages.append({"role": "user", "content": user_turn})

        try:
            # Generate response
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=1024,
            )

            assistant_response = response.choices[0].message.content
            responses.append(assistant_response)

            # Update conversation history
            conversation_history.append(user_turn)
            conversation_history.append(assistant_response)

            print(f"    Turn {turn_num}: Generated response ({len(assistant_response)} chars)")

        except Exception as e:
            print(f"    Turn {turn_num}: ERROR - {e}")
            # Use error message as response
            responses.append(f"[ERROR: {str(e)}]")
            break

    return responses


async def main():
    """Generate responses for MHJ sequences."""

    print("=" * 80)
    print("MHJ Response Generation")
    print("=" * 80)
    print()
    print("Generating assistant responses for MHJ sequences...")
    print("Target model: Claude 3.5 Sonnet")
    print()

    # Connect to ArangoDB
    print("Connecting to ArangoDB...")
    arango_client = ArangoClient(hosts='http://192.168.111.125:8529')
    db = arango_client.db('promptguard', username='root', password='')
    print("Connected!")
    print()

    # Load MHJ sequences (10 for pilot)
    print("Loading MHJ sequences (10 samples)...")
    loader = SequenceLoader(db=db)
    sequences = loader.load(dataset="mhj", sample=10)
    print(f"Loaded {len(sequences)} sequences")
    print()

    # Set up OpenAI client
    import os
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY environment variable not set")
        return

    openai_client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # Generate responses for each sequence
    print("Generating responses...")
    print()

    sequences_with_responses = []
    total_cost = 0.0

    try:
        for i, seq in enumerate(sequences, 1):
            print(f"[{i}/{len(sequences)}] {seq.attack_id} ({len(seq.turns)} turns)")

            responses = await generate_responses_for_sequence(
                client=openai_client,
                sequence=seq,
                model="anthropic/claude-sonnet-4.5",
                temperature=0.7,
            )

            # Update sequence with responses
            seq.assistant_responses = responses
            sequences_with_responses.append(seq)

            # Rough cost estimate (Sonnet: ~$3/$15 per 1M tokens)
            input_tokens = sum(len(t) // 4 for t in seq.turns)  # rough estimate
            output_tokens = sum(len(r) // 4 for r in responses)
            cost = (input_tokens * 3 / 1_000_000) + (output_tokens * 15 / 1_000_000)
            total_cost += cost

            print(f"    Complete! {len(responses)} responses generated")
            print(f"    Estimated cost: ${cost:.4f}")
            print()

    finally:
        await openai_client.close()

    # Save sequences to JSON file (database has permission issues)
    print("Saving sequences with responses to JSON file...")

    output_path = Path("data/mhj_with_responses.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sequences_data = []
    for seq in sequences_with_responses:
        doc = seq.model_dump(mode="json")
        doc["has_assistant_responses"] = True
        doc["response_generation_model"] = "anthropic/claude-sonnet-4.5"
        doc["response_generation_timestamp"] = datetime.utcnow().isoformat()
        sequences_data.append(doc)

    with open(output_path, "w") as f:
        json.dump(sequences_data, f, indent=2)

    print(f"Saved {len(sequences_with_responses)} sequences to {output_path}")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Sequences processed: {len(sequences_with_responses)}")
    print(f"Total responses generated: {sum(len(s.assistant_responses) for s in sequences_with_responses)}")
    print(f"Total estimated cost: ${total_cost:.4f}")
    print(f"Responses saved to: {output_path}")
    print()
    print("Next step: Run response evaluation pilot")
    print("  uv run python scripts/run_response_evaluation_pilot.py")


if __name__ == "__main__":
    asyncio.run(main())
