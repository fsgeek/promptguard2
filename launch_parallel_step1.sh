#!/bin/bash
# Launch 5 parallel Step 1 processes, one per model

DATASET="phase1b"
MODELS=(
    "moonshotai/kimi-k2-0905"
    "openai/gpt-5-chat"
    "google/gemini-2.5-flash"
    "deepcogito/cogito-v2-preview-llama-405b"
    "x-ai/grok-4"
)

echo "Starting parallel Phase 1B Step 1 collection..."
echo "Dataset: $DATASET"
echo "Models: ${#MODELS[@]}"
echo ""

for MODEL in "${MODELS[@]}"; do
    SAFE_MODEL=$(echo "$MODEL" | tr '/' '_' | tr ':' '_')
    LOG_FILE="phase1b_step1_${SAFE_MODEL}.log"
    
    echo "Launching: $MODEL -> $LOG_FILE"
    nohup uv run python -m src.cli.step1 \
        --dataset "$DATASET" \
        --full \
        --model "$MODEL" \
        --resume \
        > "$LOG_FILE" 2>&1 &
    
    PID=$!
    echo "  PID: $PID"
    
    # Brief delay to avoid startup contention
    sleep 2
done

echo ""
echo "All processes launched. Monitor with:"
echo "  tail -f phase1b_step1_*.log"
echo "  ps aux | grep step1"
