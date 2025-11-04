#!/bin/bash
# Recovery script for 31 missing Step 1 evaluations
# Generated from database analysis on 2025-11-04

set -e  # Exit on error

echo "Starting recovery of 31 missing Step 1 evaluations..."
echo "Estimated cost: ~$0.50"
echo

uv run python -m src.cli.step1 --attack-id alignment_lab_extract_0 --model 'deepcogito/cogito-v2-preview-llama-405b'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_0 --model 'google/gemini-2.5-flash'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_0 --model 'moonshotai/kimi-k2-0905'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_0 --model 'openai/gpt-5-chat'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_0 --model 'x-ai/grok-4'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_1 --model 'deepcogito/cogito-v2-preview-llama-405b'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_1 --model 'google/gemini-2.5-flash'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_1 --model 'moonshotai/kimi-k2-0905'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_1 --model 'openai/gpt-5-chat'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_1 --model 'x-ai/grok-4'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_10 --model 'deepcogito/cogito-v2-preview-llama-405b'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_10 --model 'google/gemini-2.5-flash'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_10 --model 'moonshotai/kimi-k2-0905'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_10 --model 'openai/gpt-5-chat'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_10 --model 'x-ai/grok-4'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_11 --model 'deepcogito/cogito-v2-preview-llama-405b'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_11 --model 'google/gemini-2.5-flash'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_11 --model 'moonshotai/kimi-k2-0905'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_11 --model 'openai/gpt-5-chat'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_11 --model 'x-ai/grok-4'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_12 --model 'deepcogito/cogito-v2-preview-llama-405b'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_12 --model 'google/gemini-2.5-flash'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_12 --model 'moonshotai/kimi-k2-0905'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_12 --model 'openai/gpt-5-chat'
uv run python -m src.cli.step1 --attack-id alignment_lab_extract_12 --model 'x-ai/grok-4'
uv run python -m src.cli.step1 --attack-id benign_malicious_282746 --model 'deepcogito/cogito-v2-preview-llama-405b'
uv run python -m src.cli.step1 --attack-id benign_malicious_282746 --model 'x-ai/grok-4'
uv run python -m src.cli.step1 --attack-id benign_malicious_406847 --model 'deepcogito/cogito-v2-preview-llama-405b'
uv run python -m src.cli.step1 --attack-id benign_malicious_406847 --model 'x-ai/grok-4'
uv run python -m src.cli.step1 --attack-id benign_malicious_423360 --model 'deepcogito/cogito-v2-preview-llama-405b'
uv run python -m src.cli.step1 --attack-id benign_malicious_423360 --model 'x-ai/grok-4'

echo
echo "Recovery complete. Verifying final counts..."
uv run python -c "
from src.database.client import get_client
db = get_client().get_database()
responses = db.collection('step1_baseline_responses').count()
failures = db.collection('processing_failures').count()
print(f'Step 1 responses: {responses}')
print(f'Processing failures: {failures}')
print(f'Total: {responses + failures}')
print(f'Expected: 3810')
print(f'Complete: {responses + failures >= 3810}')
"
