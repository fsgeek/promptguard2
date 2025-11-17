"""
Create v2.1-e observer prompt with JSON output format instruction.

Fixes the bug in v2.1-d where the prompt lacks JSON format instruction,
causing markdown analysis instead of parseable JSON.
"""

import sys
import os
from src.database.client import get_client


def main():
    db_client = get_client()
    db = db_client.get_database()

    # Read v2.1-d prompt
    print("Reading v2.1-d prompt from database...")
    query = """
    FOR prompt IN observer_prompts
      FILTER prompt.version == 'v2.1-d'
      RETURN prompt
    """
    results = list(db.aql.execute(query))

    if not results:
        print("ERROR: v2.1-d prompt not found")
        return 1

    v2_1_d = results[0]
    print(f"Found v2.1-d: {v2_1_d['_key']}")
    print(f"Prompt length: {len(v2_1_d['prompt_text'])} chars")

    # Create v2.1-e with JSON format instruction
    json_format = """
Provide your assessment in the following JSON format:
{
  "T": <float 0.0-1.0>,
  "I": <float 0.0-1.0>,
  "F": <float 0.0-1.0>,
  "reasoning": "<detailed explanation>"
}
"""

    v2_1_e_prompt = v2_1_d['prompt_text'].rstrip() + "\n" + json_format

    # Store v2.1-e
    print("\nCreating v2.1-e with JSON format instruction...")
    v2_1_e_doc = {
        '_key': 'v2.1-e_composition_json_fixed',
        'version': 'v2.1-e',
        'prompt_text': v2_1_e_prompt,
        'metadata': {
            'parent': 'v2.1-d',
            'phase': 'phase2b',
            'description': 'v2.1-d with JSON output format instruction added',
            'changes': 'Added explicit JSON format requirement at end of prompt'
        }
    }

    observer_prompts = db.collection('observer_prompts')
    observer_prompts.insert(v2_1_e_doc, overwrite=True)

    print("✓ Created v2.1-e_composition_json_fixed")
    print(f"  Prompt length: {len(v2_1_e_prompt)} chars")

    # Verify storage
    verify_query = """
    FOR prompt IN observer_prompts
      FILTER prompt.version == 'v2.1-e'
      RETURN prompt
    """
    verify = list(db.aql.execute(verify_query))

    if verify:
        print("✓ Verified v2.1-e in database")
        return 0
    else:
        print("ERROR: Failed to verify v2.1-e")
        return 1


if __name__ == '__main__':
    sys.exit(main())
