# Suggested Commands

## Development Workflow

### Setup
```bash
# Install dependencies
uv pip install python-arango httpx instructor pydantic pytest pyyaml

# Configure environment
export OPENROUTER_API_KEY=your_key_here
export ARANGODB_PROMPTGUARD_PASSWORD=your_password
```

### Testing
```bash
# Run all tests
uv run pytest tests/

# Run integration tests only (requires API keys)
uv run pytest tests/integration/

# Run unit tests only
uv run pytest tests/unit/

# Run with coverage
uv run pytest --cov=src tests/
```

### Code Quality
```bash
# Format code (if black installed)
black src/ tests/

# Lint code (if ruff installed)
ruff check src/ tests/

# Fix auto-fixable issues
ruff check --fix src/ tests/
```

### Database Operations
```bash
# Migrate attacks from old PromptGuard (762 attacks)
uv run python -m src.cli.migrate

# Verify migration
uv run python -m src.cli.migrate --verify

# Test database connection
uv run python -c "from src.database.client import get_client; client = get_client(); print('Connected')"
```

### Experiments

#### Step 1: Baseline Collection
```bash
# Test on 5 samples first (recommended before full run)
uv run python -m src.cli.step1 --test-mode --samples 5

# Review test results
cat data/experiments/exp_phase1_step1_baseline_v1/raw_responses.jsonl | head -25

# Run full collection (3,810 evaluations, ~2-4 hours, ~$50-75)
uv run python -m src.cli.step1 --full

# Resume from checkpoint if interrupted
uv run python -m src.cli.step1 --resume
```

#### Step 2: Observer Pre-filter Collection
```bash
# Test on 5 samples first
uv run python -m src.cli.step2 --test-mode --samples 5

# Run full collection (762 evaluations + target responses, ~1-2 hours, ~$20-40)
uv run python -m src.cli.step2 --full

# Specify observer model
uv run python -m src.cli.step2 --observer-model <model>
```

#### Step 3: Compliance Classification
```bash
# Annotate gold standard (50 stratified samples)
uv run python -m src.cli.annotate_gold_standard

# Review annotations
cat data/experiments/gold_standard_annotations.csv

# Validate classifier against gold standard
uv run python -m src.cli.classify_step1_responses --validate-only

# Classify all Step 1 responses
uv run python -m src.cli.classify_step1_responses --full
```

### Analysis & Reporting
```bash
# Generate comparative analysis report
uv run python -m src.cli.analyze --phase1 \
  --step1-experiment exp_phase1_step1_baseline_v1 \
  --step2-experiment exp_phase1_step2_pre_filter_v1 \
  --output reports/phase1_comparative_analysis.md

# View report
cat reports/phase1_comparative_analysis.md

# Execute decision gate
uv run python -m src.cli.analyze --decision-gate \
  --step1-experiment exp_phase1_step1_baseline_v1 \
  --step2-experiment exp_phase1_step2_pre_filter_v1 \
  --output reports/phase1_decision_gate.md

# View decision
cat reports/phase1_decision_gate.md
```

### Version Control
```bash
# Standard git operations
git status
git add .
git commit -m "message"
git push
git pull
```

### Quick Checks
```bash
# Check model configs
jq '.models | keys' config/model_configs.json

# Dataset stats
jq 'length' datasets/*.json

# Find errors in logs
grep -c ERROR validation_output.log
```
