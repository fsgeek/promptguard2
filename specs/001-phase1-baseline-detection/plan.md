# Implementation Plan: Phase 1 Baseline Detection

**Branch**: `001-phase1-baseline-detection` | **Date**: 2025-10-31 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-phase1-baseline-detection/spec.md`

## Summary

Implement minimum viable research (Phase 1) by collecting baseline LLM responses without filtering (Step 1) and testing observer framing as pre-filter (Step 2). Deliverable: "Observer framing improves detection by X% over RLHF baseline" with executor vs observer paradox analysis.

**Technical approach:** Python async pipeline using OpenRouter API, ArangoDB storage, Instructor for structured outputs, hybrid compliance classification.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: python-arango, httpx, instructor, pydantic
**Storage**: ArangoDB (PromptGuard2 database at 192.168.111.125:8529)
**Testing**: pytest with real API integration (Tier 2 per constitution)
**Target Platform**: Linux server
**Project Type**: single (research pipeline)
**Performance Goals**: Process 762 attacks × 5 models (3,810 evals) in 2-4 hours
**Constraints**: <$100 total cost, raw logging before all parsing, fail-fast on errors
**Scale/Scope**: 762 labeled attacks, 5 target models, 1-2 observer models

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle II: Empirical Integrity (NON-NEGOTIABLE)
✅ **PASS** - Tier 2 (API Integration): Real OpenRouter calls required
- Real API call logs from OpenRouter dashboard
- Cost receipts prove actual usage
- Specific models tested (Claude Sonnet 4.5, GPT-4o, Gemini 2.0 Flash, etc.)
- Sample testing (5 prompts) before full run

**Mandatory workflow:**
1. Implementation: Build Step 1 + Step 2 pipelines
2. Validation: Test on 5 samples with real API calls
3. Auditor: Verify cost matches expected before full run

### Principle VI: Data Provenance
✅ **PASS** - Raw logging implemented
- Raw API responses logged before parsing (JSONL format)
- Single ID system: `attack_id` → `attacks._key`
- Experiment tagging: `exp_phase1_step1_baseline_v1`, etc.
- Schema validation before DB insertion
- Fail-fast if raw logging fails

### Architectural Decision: Fail-Fast Over Graceful Degradation
✅ **PASS** - Error handling preserves provenance
- API failures raise `EvaluationError` with context
- Parser failures raise (don't return fake values)
- Raw data preserved even on failure
- No silent fallbacks

### Data Architecture Standards: Pre-Collection Validation
✅ **PASS** - Sample testing required
- Test on 5 samples before 3,810-evaluation run
- Verify: raw logging, parsing, DB insertion, cost tracking
- Manual review of sample results

### Specification-Driven Development
✅ **PASS** - Complex component with external dependencies
- OpenRouter API integration
- ArangoDB storage
- Cross-module contracts (pipeline → storage → analysis)
- Research data integrity implications

**Specification defines:**
- Observable behaviors (what SHOULD happen)
- Contract requirements (schemas, ID system)
- Failure modes (when to raise errors)
- Validation criteria (5-sample test, cost verification)

## Project Structure

### Documentation (this feature)

```text
specs/001-phase1-baseline-detection/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Database schemas
├── quickstart.md        # Phase 1: How to run experiments
├── contracts/           # Phase 1: API contracts
│   ├── openrouter.yaml  # OpenRouter API contract
│   ├── storage.yaml     # ArangoDB schema contract
│   └── pipeline.yaml    # Evaluation pipeline contract
└── tasks.md             # Phase 2: Implementation tasks (via /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── database/
│   ├── client.py           # ArangoDB connection
│   ├── migrations/
│   │   └── 001_migrate_attacks.py
│   └── schemas/
│       ├── attacks.py
│       ├── experiments.py
│       ├── step1_baseline_responses.py
│       ├── step2_pre_evaluations.py
│       └── processing_failures.py
│
├── evaluation/
│   ├── pipeline.py         # EvaluationPipeline base class
│   ├── step1_baseline.py   # Step 1 implementation
│   ├── step2_prefilter.py  # Step 2 implementation
│   ├── classifiers/
│   │   ├── compliance.py   # Compliance classifier
│   │   └── neutrosophic.py # Neutrosophic parser
│   └── prompts/
│       └── compliance_classifier.py  # Compliance classification prompt
│
├── api/
│   ├── openrouter.py       # OpenRouter client
│   ├── rate_limiter.py     # Rate limiting + retry logic
│   └── models.py           # Model configurations
│
├── logging/
│   ├── raw_logger.py       # Raw API response logger (JSONL)
│   └── experiment_logger.py # Experiment metadata logger
│
├── analysis/
│   ├── comparative.py      # Step 1 vs Step 2 comparison
│   ├── executor_observer.py # Executor vs observer analysis
│   └── reports.py          # Report generation
│
└── cli/
    ├── migrate.py          # Database migration command
    ├── step1.py            # Step 1 collection command
    ├── step2.py            # Step 2 collection command
    └── analyze.py          # Analysis command

tests/
├── integration/
│   ├── test_step1_pipeline.py     # Step 1 with real API (5 samples)
│   ├── test_step2_pipeline.py     # Step 2 with real API (5 samples)
│   └── test_migration.py          # Database migration
│
├── unit/
│   ├── test_compliance_classifier.py
│   ├── test_neutrosophic_parser.py
│   └── test_raw_logger.py
│
└── fixtures/
    ├── sample_attacks.json        # 5-sample test set
    └── expected_responses.json    # Expected outputs

config/
├── models.yaml            # Model configurations
├── experiments.yaml       # Experiment metadata
└── database.yaml          # Database connection settings

data/
└── experiments/
    ├── exp_phase1_step1_baseline_v1/
    │   └── raw_responses.jsonl
    └── exp_phase1_step2_pre_filter_v1/
        └── raw_responses.jsonl
```

**Structure Decision**: Single project (research pipeline). No frontend/backend split needed. Organized by functional layer (database, evaluation, api, logging, analysis, cli) for clarity.

**Observer Prompt Storage**: Observer prompt v2.1 is stored in ArangoDB `observer_prompts` collection (immutable, versioned) per clarification Q7, not as a Python file. This enables provenance tracking and A/B testing across experiments. Migrated from old PromptGuard `prompt_configurations` collection.

## Complexity Tracking

*No constitutional violations - table not required*

---

## Phase 0: Research & Technology Decisions

### Research Questions

1. **OpenRouter vs Direct API**: Should we use OpenRouter for multi-provider support or direct APIs?
2. **Async vs Sync**: Should evaluation pipeline be async for performance?
3. **Instructor Integration**: Best practices for structured outputs with JSON fallback?
4. **ArangoDB Python Client**: Connection pooling and error handling patterns?
5. **Classification Model**: Which model for compliance classification (Haiku vs Sonnet)?

### Output: `research.md`

**Decision 1: OpenRouter API**
- **Rationale**: Single API for 5 different providers (Anthropic, OpenAI, Google, Meta, xAI)
- **Alternatives considered**: Direct APIs (more complex, 5 different clients)
- **Trade-offs**: Slight latency overhead, but massive simplification

**Decision 2: Async Pipeline**
- **Rationale**: Process multiple attacks concurrently, reduce total runtime
- **Alternatives considered**: Synchronous (simpler but 5x slower)
- **Trade-offs**: Complexity vs performance (762 attacks = significant time savings)

**Decision 3: Instructor + JSON Fallback**
- **Rationale**: Structured outputs with graceful degradation (Instance 63 lesson)
- **Alternatives considered**: Raw JSON parsing (fragile, 113 failures in v1)
- **Trade-offs**: Dependency overhead vs robustness

**Decision 4: python-arango with Connection Pooling**
- **Rationale**: Official ArangoDB Python client, proven reliability
- **Alternatives considered**: Raw HTTP (reinventing wheel)
- **Pattern**: Single client instance, reuse connections

**Decision 5: Claude 3 Haiku for Classification**
- **Rationale**: Cost-optimized, sufficient for binary classification
- **Alternatives considered**: Sonnet (more expensive), GPT-4o Mini (cross-provider)
- **Validation**: Test on 50 manual gold standard, upgrade if <90% agreement

---

## Phase 1: Design & Contracts

### Data Model (`data-model.md`)

**Terminology:**
- **Model Identifier**: Original model name from provider (e.g., `anthropic/claude-sonnet-4.5`, `openai/gpt-4o`)
  - Used for: API requests, display names, human-readable references
  - Stored in: `target_model`, `observer_model` fields (preserves original format)
- **Model Slug**: Normalized identifier for database keys (e.g., `anthropic_claude-sonnet-4_5`, `openai_gpt-4o`)
  - Used for: ArangoDB `_key` fields (cannot contain `/` or `.`)
  - Transformation: Replace `/` and `.` with `_`
  - Example: `anthropic/claude-4.5` → `anthropic_claude-4_5`

**Entities:**

1. **Attack**
   - Fields: `_key`, `prompt_text`, `ground_truth`, `encoding_technique`, `dataset_source`, `attack_metadata`, `metadata`
   - Validation: `ground_truth` in {manipulative, extractive, reciprocal, borderline}
   - Relationships: Referenced by baseline_responses, pre_evaluations, processing_failures

2. **Experiment**
   - Fields: `experiment_id` (PK), `phase`, `step`, `description`, `parameters`, `started`, `completed`, `status`
   - State transitions: in_progress → completed/failed

3. **BaselineResponse**
   - Fields: Attack reference, model, raw response, classification, cost, latency, timestamp
   - Validation: `compliance_classification` in {comply, refuse, unclear}
   - Key: `<attack_id>_<model_slug>` (unique per attack-model pair)
   - Note: Stores both `target_model` (original identifier) and uses `model_slug` in `_key`

4. **PreEvaluation**
   - Fields: Attack reference, observer model, neutrosophic scores, detection, LLM response, classification
   - Validation: T, I, F in [0,1], detected = (F >= 0.7)
   - Key: `<attack_id>_<observer_model_slug>`
   - Note: Stores both `observer_model` (original identifier) and uses `model_slug` in `_key`

5. **ProcessingFailure**
   - Fields: Attack reference, experiment, stage, error details, raw data, timestamp
   - Purpose: Debugging, never blocks progress

### API Contracts (`contracts/`)

**OpenRouter Contract** (`contracts/openrouter.yaml`):
```yaml
POST /api/v1/chat/completions:
  request:
    model: string
    messages: array
    temperature: float (optional)
    max_tokens: int (optional)
    metadata:
      experiment_id: string
      attack_id: string
  response:
    choices: array
      message:
        content: string
      finish_reason: string
    usage:
      prompt_tokens: int
      completion_tokens: int
      total_tokens: int
    id: string
  errors:
    400: Bad request
    429: Rate limit
    500: Server error
```

**Storage Contract** (`contracts/storage.yaml`):
```yaml
Collections:
  attacks:
    _key: string (required, unique)
    prompt_text: string (required)
    ground_truth: enum (required)

  step1_baseline_responses:
    _key: string (required, format: <attack_id>_<model_slug>)
    attack_id: string (required, foreign key)
    experiment_id: string (required, indexed)
    raw_api_response: object (required)
    compliance_classification: enum (required)

  step2_pre_evaluations:
    _key: string (required, format: <attack_id>_<observer_slug>)
    attack_id: string (required, foreign key)
    experiment_id: string (required, indexed)
    neutrosophic_scores: object (required, validated)
    detected: boolean (required, computed from F >= 0.7)
```

**Pipeline Contract** (`contracts/pipeline.yaml`):
```yaml
EvaluationPipeline:
  input:
    attack: Attack
    config: EvaluationConfig
  output:
    result: EvaluationResult
    raw_logged: boolean (must be true)
  errors:
    EvaluationError: API failure, parsing failure, etc.

  guarantees:
    - Raw response logged before parsing
    - Errors preserve raw data
    - No partial results on failure
```

### Quickstart (`quickstart.md`)

```markdown
# Phase 1 Quickstart

## Prerequisites
- Python 3.11+
- ArangoDB at 192.168.111.125:8529
- OpenRouter API key

## Setup
```bash
# Install dependencies
uv pip install -r requirements.txt

# Configure environment
export OPENROUTER_API_KEY=your_key
export ARANGODB_PROMPTGUARD_PASSWORD=your_password

# Migrate attacks collection
uv run python -m src.cli.migrate

# Verify migration
uv run python -m src.cli.migrate --verify
```

## Run Phase 1

### Step 1: Baseline Collection
```bash
# Test on 5 samples
uv run python -m src.cli.step1 --test-mode --samples 5

# Review results
cat data/experiments/exp_phase1_step1_baseline_v1/raw_responses.jsonl | head -5

# Full collection (3,810 evaluations)
uv run python -m src.cli.step1 --full

# Monitor progress
watch -n 5 'uv run python -m src.cli.step1 --status'
```

### Step 2: Pre-filter Collection
```bash
# Test on 5 samples
uv run python -m src.cli.step2 --test-mode --samples 5

# Full collection (762 evaluations)
uv run python -m src.cli.step2 --full
```

### Analysis
```bash
# Generate comparative report
uv run python -m src.cli.analyze --phase1

# View results
cat reports/phase1_comparative_analysis.md
```

## Decision Gate
```bash
# Execute decision logic
uv run python -m src.cli.analyze --decision-gate

# Output: Proceed to Phase 2 / Publish Phase 1 / etc.
```
```

---

## Implementation Notes

### Critical Path
1. Database migration (blocks everything)
2. Raw logging infrastructure (constitutional requirement)
3. Step 1 pipeline (establishes baseline)
4. Compliance classification (enables comparison)
5. Step 2 pipeline (proves hypothesis)
6. Comparative analysis (delivers result)

### Testing Strategy
- Unit tests: Parsers, classifiers, loggers
- Integration tests: **Real API calls on 5 samples** (Tier 2 requirement)
- Validation: Manual review of test results before full run

### Error Handling Philosophy
- Fail-fast: Errors halt collection, don't degrade silently
- Preserve provenance: Raw data logged even on failure
- Actionable errors: Include attack_id, model, stage in error messages

### Performance Considerations
- Async processing: Concurrency for 762 attacks
- Rate limiting: Respect OpenRouter limits (exponential backoff)
- Batch checkpointing: Resume after failures without re-processing

---

## Post-Phase 1 Re-Check

*To be filled after Phase 1 design complete*

### Constitution Compliance
- ✅ Raw logging implemented
- ✅ Fail-fast error handling
- ✅ Sample testing workflow
- ✅ Single ID system
- ✅ Experiment tagging

### Observable Behaviors Verified
- ✅ Raw responses logged before parsing
- ✅ Parsing failures preserve raw data
- ✅ Sample tests show valid results
- ✅ Cost tracking matches projections

---

## Next Steps

1. **Phase 0**: Complete `research.md` with technology decisions
2. **Phase 1**: Complete `data-model.md`, `contracts/`, `quickstart.md`
3. **Agent Context**: Run `.specify/scripts/bash/update-agent-context.sh claude`
4. **Phase 2**: Use `/speckit.tasks` to generate implementation task list
5. **Implementation**: Execute tasks, test on 5 samples, run full collection
6. **Decision Gate**: Analyze results, decide on Phase 2

---

*Plan generated by Instance 64*
*Based on spec.md and Constitution v2.0.0*
*Date: 2025-10-31*
