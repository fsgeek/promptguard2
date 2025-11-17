#!/usr/bin/env python3
"""Read observer prompt from ArangoDB."""
import sys
import os

# Set working directory
os.chdir('/home/tony/projects/promptguard/promptguard2')
sys.path.insert(0, '/home/tony/projects/promptguard/promptguard2/src')

from storage.arango_storage import ArangoStorage
import json

if len(sys.argv) < 2:
    print("Usage: get_observer_prompt.py <prompt_key>")
    sys.exit(1)

storage = ArangoStorage()
prompt_doc = storage.get_observer_prompt(sys.argv[1])

if prompt_doc:
    print(json.dumps(prompt_doc, indent=2))
else:
    print(f"ERROR: Prompt '{sys.argv[1]}' not found", file=sys.stderr)
    sys.exit(1)
