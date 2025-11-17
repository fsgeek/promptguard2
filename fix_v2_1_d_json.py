#!/usr/bin/env python3
"""Fix v2.1-d prompt to add JSON output format and create v2.1-e."""

import sys
sys.path.insert(0, 'src')

from storage.arango_storage import ArangoStorage
import json

def main():
    storage = ArangoStorage()

    # Read v2.1-d prompt
    print("Reading v2.1-d prompt from database...")
    v2_1_d = storage.get_observer_prompt('v2.1-d_composition_aware')

    if not v2_1_d:
        print("ERROR: v2.1-d prompt not found")
        return 1

    print(f"Found v2.1-d prompt: {v2_1_d['_key']}")
    print(f"Prompt length: {len(v2_1_d['prompt'])} chars")

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

    v2_1_e_prompt = v2_1_d['prompt'].rstrip() + "\n" + json_format

    # Store v2.1-e
    print("\nCreating v2.1-e with JSON format instruction...")
    storage.store_observer_prompt(
        key='v2.1-e_composition_json_fixed',
        prompt=v2_1_e_prompt,
        metadata={
            'version': 'v2.1-e',
            'parent': 'v2.1-d',
            'phase': 'phase2b',
            'description': 'v2.1-d with JSON output format instruction added',
            'changes': 'Added explicit JSON format requirement at end of prompt'
        }
    )

    print("✓ Created v2.1-e_composition_json_fixed")
    print(f"  Prompt length: {len(v2_1_e_prompt)} chars")

    # Verify storage
    verify = storage.get_observer_prompt('v2.1-e_composition_json_fixed')
    if verify:
        print("✓ Verified v2.1-e in database")
        return 0
    else:
        print("ERROR: Failed to verify v2.1-e")
        return 1

if __name__ == '__main__':
    sys.exit(main())
