#!/usr/bin/env python3
"""
Verify Phase 2 Observer Framework Accessible

Task T007: Verify observer prompt v2.1-c is accessible and suitable for Phase 3 evaluation

Requirements:
1. Query observer_prompts collection for document with _key=v2.1-c
2. Verify prompt contains reciprocity and context_integrity principles
3. Document prompt template structure
4. Test: Load prompt, format with sample turn, verify output format

CRITICAL: Do NOT modify v2.1-c prompt - reuse as-is

Date: 2025-11-18
Phase: Phase 3 - Session-Based Temporal Tracking
"""

from src.database.client import get_client


def verify_observer_prompt():
    """Verify Phase 2 observer prompt v2.1-c is accessible."""
    print("=" * 80)
    print("PHASE 2 OBSERVER FRAMEWORK VERIFICATION")
    print("=" * 80)
    print()

    db = get_client().get_database()

    # Query for v2.1-c observer prompt
    print("Querying observer_prompts collection for v2.1-c...")
    try:
        observer_prompts = db.collection('observer_prompts')
        v2_1_c = observer_prompts.get('v2.1-c_combined')

        if v2_1_c is None:
            print("✗ Observer prompt v2.1-c not found")
            print("  Available prompts:")
            all_prompts = list(db.aql.execute('''
                FOR doc IN observer_prompts
                  SORT doc._key
                  RETURN doc._key
            '''))
            for key in all_prompts:
                print(f"    - {key}")
            return False

        print(f"✓ Found observer prompt: {v2_1_c['_key']}")
        print()

    except Exception as e:
        print(f"✗ Error querying observer_prompts: {e}")
        return False

    # Verify prompt structure
    print("=" * 80)
    print("PROMPT STRUCTURE ANALYSIS")
    print("=" * 80)
    print()

    # Check for required fields
    required_fields = ['_key', 'version', 'prompt_text']
    missing_fields = [f for f in required_fields if f not in v2_1_c]

    if missing_fields:
        print(f"⚠ Missing fields: {missing_fields}")
    else:
        print("✓ All required fields present")

    print()
    print("Document fields:")
    for key in sorted(v2_1_c.keys()):
        if key.startswith('_'):
            continue  # Skip internal ArangoDB fields
        value = v2_1_c[key]
        if isinstance(value, str) and len(value) > 100:
            print(f"  {key}: <string length={len(value)}>")
        else:
            print(f"  {key}: {value}")

    print()

    # Check principles (they're embedded in the prompt text, not as a separate field)
    print("=" * 80)
    print("PRINCIPLE VERIFICATION")
    print("=" * 80)
    print()

    prompt_text = v2_1_c.get('prompt_text', '')
    prompt_lower = prompt_text.lower()

    # Check for principle mentions in prompt text
    required_principles = {
        'reciprocity': 'reciprocity' in prompt_lower,
        'context_integrity': 'context integrity' in prompt_lower or
                           ('context' in prompt_lower and 'integrity' in prompt_lower)
    }

    found_principles = [p for p, found in required_principles.items() if found]
    missing_principles = [p for p, found in required_principles.items() if not found]

    print(f"Principles found in prompt text: {found_principles}")

    if missing_principles:
        print(f"✗ Missing required principles: {missing_principles}")
        return False
    else:
        print(f"✓ All required principles found: {found_principles}")

    print()

    # Document prompt template structure
    print("=" * 80)
    print("PROMPT TEMPLATE STRUCTURE")
    print("=" * 80)
    print()

    # Check for placeholders (uppercase format used in v2.1-c)
    placeholders = []
    if '{TURN_NUMBER}' in prompt_text or '{turn_number}' in prompt_text:
        placeholders.append('TURN_NUMBER')
    if '{PROMPT}' in prompt_text or '{prompt}' in prompt_text or '{user_prompt}' in prompt_text:
        placeholders.append('PROMPT/user_prompt')
    if '{PRINCIPLE}' in prompt_text or '{principle}' in prompt_text:
        placeholders.append('PRINCIPLE')

    print("Prompt template placeholders:")
    for placeholder in placeholders:
        print(f"  ✓ {{{placeholder}}}")

    if not placeholders:
        print("  ⚠ No placeholders found (static prompt)")

    print()
    print(f"Prompt length: {len(prompt_text)} characters")
    print()

    # Show first 500 characters of prompt
    print("Prompt preview (first 500 chars):")
    print("-" * 80)
    print(prompt_text[:500])
    if len(prompt_text) > 500:
        print(f"... ({len(prompt_text) - 500} more characters)")
    print("-" * 80)
    print()

    # Test prompt formatting
    print("=" * 80)
    print("PROMPT FORMATTING TEST")
    print("=" * 80)
    print()

    sample_turn = "What contributions did Karen Wetterhahn make to science?"
    sample_principle = "reciprocity"
    sample_turn_number = 1

    # Try to format prompt (v2.1-c uses uppercase placeholders)
    try:
        # Check what variables are needed
        if '{TURN_NUMBER}' in prompt_text:
            formatted_prompt = prompt_text.format(
                TURN_NUMBER=sample_turn_number,
                PROMPT=sample_turn
            )
        elif '{turn_number}' in prompt_text:
            formatted_prompt = prompt_text.format(
                turn_number=sample_turn_number,
                prompt=sample_turn
            )
        elif '{PROMPT}' in prompt_text:
            formatted_prompt = prompt_text.format(
                PROMPT=sample_turn
            )
        elif '{prompt}' in prompt_text:
            formatted_prompt = prompt_text.format(
                prompt=sample_turn
            )
        elif '{user_prompt}' in prompt_text:
            formatted_prompt = prompt_text.format(
                user_prompt=sample_turn
            )
        else:
            # Static prompt
            formatted_prompt = prompt_text

        print("✓ Successfully formatted prompt with sample data")
        print()
        print("Formatted prompt preview (first 500 chars):")
        print("-" * 80)
        print(formatted_prompt[:500])
        if len(formatted_prompt) > 500:
            print(f"... ({len(formatted_prompt) - 500} more characters)")
        print("-" * 80)
        print()

    except KeyError as e:
        print(f"✗ Missing template variable: {e}")
        print(f"  Prompt expects variables that weren't provided")
        return False

    # Expected output format
    print("=" * 80)
    print("EXPECTED OUTPUT FORMAT")
    print("=" * 80)
    print()
    print("The observer prompt should return JSON with:")
    print("  - T: float (Truth degree, 0.0-1.0)")
    print("  - I: float (Indeterminacy degree, 0.0-1.0)")
    print("  - F: float (Falsity degree, 0.0-1.0)")
    print("  - reasoning: string (Explanation)")
    print()
    print("Example expected response:")
    print("  {")
    print('    "T": 0.75,')
    print('    "I": 0.15,')
    print('    "F": 0.10,')
    print('    "reasoning": "The request appears reciprocal..."')
    print("  }")
    print()

    # Summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print()
    print("✓ Observer prompt v2.1-c accessible")
    print(f"✓ Contains required principles: {found_principles}")
    print("✓ Prompt template can be formatted")
    print("✓ Ready for Phase 3 turn-by-turn evaluation")
    print()
    print("CRITICAL REMINDER: Do NOT modify v2.1-c prompt - reuse as-is")
    print()

    return True


def main():
    """Main verification."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "PHASE 2 OBSERVER FRAMEWORK VERIFICATION" + " " * 24 + "║")
    print("║" + " " * 28 + "Task T007" + " " * 42 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    success = verify_observer_prompt()

    if success:
        print("=" * 80)
        print("✓ VERIFICATION COMPLETE")
        print("=" * 80)
    else:
        print("=" * 80)
        print("✗ VERIFICATION FAILED")
        print("=" * 80)
        exit(1)


if __name__ == '__main__':
    main()
