#!/usr/bin/env python3
"""
Generate assistant responses and evaluate them.

Strategy:
1. Load MHJ sequences (user prompts only)
2. For each sequence, generate assistant responses using Sonnet 4.5
3. Immediately evaluate each response using Haiku 4.5 observer
4. Store both response and evaluation to database

This avoids intermediate files and ensures data persistence.
"""

import asyncio
import os
from pathlib import Path
from datetime import datetime
from arango import ArangoClient
from openai import AsyncOpenAI

from src.pipeline.sequence_loader import SequenceLoader
from src.pipeline.batch_evaluator import BatchEvaluator, NeutrosophicEvaluation
from src.database.schemas.phase3_evaluation import (
    EvaluationPrinciple,
    PrincipleEvaluation,
    NeutrosophicScore,
)
import instructor
import uuid

async def generate_response(client: AsyncOpenAI, conversation_history: list, model: str = "anthropic/claude-sonnet-4.5"):
    """Generate single assistant response."""
    response = await client.chat.completions.create(
        model=model,
        messages=conversation_history,
        temperature=0.7,
        max_tokens=2048,
    )
    return response.choices[0].message.content

async def evaluate_response(
    client: AsyncOpenAI,
    assistant_response: str,
    conversation_context: list,
    observer_prompt_template: str,
) -> NeutrosophicEvaluation:
    """Evaluate assistant response for third-party harm."""
    # Build evaluation prompt
    context_str = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in conversation_context
    ])

    eval_prompt = observer_prompt_template.replace(
        "{CONVERSATION_CONTEXT}", context_str
    ).replace(
        "{MESSAGE_TO_EVALUATE}", assistant_response
    )

    # Call observer with structured output
    instructor_client = instructor.from_openai(client)
    result = await instructor_client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=[{"role": "user", "content": eval_prompt}],
        response_model=NeutrosophicEvaluation,
        temperature=0.0,
    )

    return result

async def main():
    # Connect to database
    db_client = ArangoClient(hosts=os.getenv("ARANGO_HOST", "http://192.168.111.125:8529"))
    db = db_client.db(
        os.getenv("ARANGO_DB", "PromptGuard2"),
        username=os.getenv("ARANGO_USER", "pgtest"),
        password=os.getenv("ARANGODB_PROMPTGUARD_PASSWORD"),
    )

    # Initialize OpenAI client (for both generation and evaluation)
    openai_client = AsyncOpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )

    # Load observer prompt from database
    observer_coll = db.collection("observer_prompts")
    prompt_doc = observer_coll.get("v2.1-c_combined")
    if not prompt_doc:
        raise ValueError("Observer prompt v2.1-c_combined not found in database")

    observer_prompt_template = prompt_doc["prompt_text"]

    # Load MHJ sequences (limit to 5 for pilot)
    loader = SequenceLoader()
    sequences = loader.load(dataset="mhj", sample=5)

    print(f"Loaded {len(sequences)} MHJ sequences")
    print(f"Generating responses with: anthropic/claude-sonnet-4.5")
    print(f"Evaluating with: anthropic/claude-haiku-4.5")
    print(f"Observer prompt: v2.1-c_combined")

    # Evaluation collection
    eval_coll = db.collection("phase3_principle_evaluations")

    total_responses = 0
    total_evaluations = 0

    for seq_idx, sequence in enumerate(sequences, 1):
        print(f"\n[{seq_idx}/{len(sequences)}] {sequence.attack_id} ({len(sequence.turns)} turns)")

        conversation = []

        for turn_num, user_prompt in enumerate(sequence.turns, 1):
            # Add user message to conversation
            conversation.append({"role": "user", "content": user_prompt})

            # Generate assistant response
            try:
                assistant_response = await generate_response(openai_client, conversation)
                conversation.append({"role": "assistant", "content": assistant_response})
                total_responses += 1

                print(f"  Turn {turn_num}: Generated response ({len(assistant_response)} chars)", end="")

                # Evaluate the response
                evaluation = await evaluate_response(
                    openai_client,
                    assistant_response,
                    conversation[:-1],  # Context before this response
                    observer_prompt_template,
                )

                # Store evaluation to database
                eval_doc = {
                    "_key": str(uuid.uuid4()),
                    "experiment_id": "exp_phase4_response_eval_pilot",
                    "attack_id": sequence.attack_id,
                    "principle": "RECIPROCITY",
                    "turn_number": turn_num,
                    "evaluator_model": "anthropic/claude-haiku-4.5",
                    "observer_prompt_version": "v2.1-c_combined",
                    "evaluation_target": "assistant_response",  # NEW: mark as response eval
                    "dyadic_state": {"t": evaluation.T, "i": evaluation.I, "f": 1.0 - evaluation.T},
                    "empty_chair_state": {"t": evaluation.T, "i": evaluation.I, "f": evaluation.F},
                    "reasoning": evaluation.reasoning,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                eval_coll.insert(eval_doc, overwrite=False)
                total_evaluations += 1

                print(f" → F={evaluation.F:.2f}")

            except Exception as e:
                print(f"  Turn {turn_num}: ERROR - {e}")
                break

    print(f"\n=== Summary ===")
    print(f"Sequences: {len(sequences)}")
    print(f"Responses generated: {total_responses}")
    print(f"Evaluations: {total_evaluations}")

    await openai_client.close()

if __name__ == "__main__":
    asyncio.run(main())
