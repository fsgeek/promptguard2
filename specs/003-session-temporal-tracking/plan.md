# Implementation Plan: Session-Based Temporal Tracking

**Branch**: `003-session-temporal-tracking` | **Date**: 2025-11-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-session-temporal-tracking/spec.md`

## Summary

Implement trajectory storage and temporal analysis for multi-turn attack detection. Store T/I/F scores at (attack_id, principle, turn_number) granularity, enabling pattern analysis that detects gradual reciprocity drift missed by stateless evaluation. Technical approach: Extend Phase 2 observer framework with ArangoDB collections for trajectory data, implement pluggable temporal detection logic (TrustEMA initial), validate on XGuard-Train (synthetic) and MHJ (real-world) datasets. Success: >80% detection on gradual escalation vs <30% stateless baseline, 0% false positive rate maintained.

## Technical Context

**Language/Version**: Python 3.11+ (existing project standard)
**Primary Dependencies**:
- ArangoDB Python driver (arango-python) for trajectory storage
- Pydantic 2.x for schema validation (already used in phase3_evaluation.py)
- OpenRouter SDK (existing Phase 2 dependency) for observer evaluations
- Pandas/Parquet for dataset loading (XGuard-Train, MHJ)

**Storage**: ArangoDB
- Collections: `phase3_evaluation_sequences`, `phase3_principle_evaluations`
- Indexes: (attack_id, principle), (attack_id, turn_number), (experiment_id), (timestamp)
- Provenance: Raw API responses, experiment tagging per Constitution VI

**Testing**: pytest (existing framework)
- Unit tests: Temporal detectors, pattern logic, schema validation
- Integration tests: Real API calls to Phase 2 observer (Constitution II)
- Validation tests: XGuard-Train/MHJ evaluation with cost tracking

**Target Platform**: Linux server (research workstation, batch processing)
**Project Type**: Single (extends existing src/ structure)

**Performance Goals**:
- 100 multi-turn sequences (avg 5 turns, 3 principles) in <10 minutes (SC-004)
- Pattern analysis queries in <2 seconds on 500+ sequences (SC-005)
- Principle addition to 100 sequences in <5 minutes (SC-007)

**Constraints**:
- Research validation only (no production deployment) - SC scope boundary
- Batch processing acceptable (no real-time streaming required)
- 0% false positive rate non-negotiable (SC-002)
- All raw API responses logged before parsing (Constitution VI)

**Scale/Scope**:
- Phase 3a: 1,137 attack sequences (XGuard 600 + MHJ 537), 100 benign sequences
- ~6,000-8,000 turn evaluations total (avg 5-6 turns per sequence)
- ~18,000-24,000 principle evaluations (3 principles per turn)
- Estimated cost: $50-100 for full dataset (haiku for evaluation)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ No Theater (I)
- Temporal detection uses real trajectory data, not mock trends
- API failures raise EvaluationError (no fake neutral scores)
- Pluggable detector interface enables empirical validation of approaches
- Tests prove trajectory storage works with real evaluations

### ✅ Empirical Integrity (II)
- Integration tests require real API calls (Phase 2 observer framework)
- Cost tracking validates actual evaluations performed
- Tier 2 testing: Observer calls via OpenRouter with cost receipts
- Validation reports include model names, timestamps, error counts

### ✅ Agency Over Constraint (III)
- Temporal tracking measures manipulation patterns (doesn't impose refusal)
- Detection provides measurement for LLM decision-making
- Trajectory analysis enables informed disengagement choices

### ✅ Semantic Evaluation Only (V)
- Reuses Phase 2 observer framework (v2.1-c neutral encoding)
- No keyword matching in trajectory analysis
- Temporal patterns detected via T/I/F semantic scores

### ✅ Data Provenance (VI)
- Raw API responses logged before parsing (`raw_response` field)
- Experiment ID on every evaluation document
- Pydantic schema validation before database insert
- Single ID system: `_key` field links sequences to evaluations
- Migration script documents schema before collection creation

### ✅ Data Architecture (VII)
- Non-ephemeral data in ArangoDB (not config files)
- Immutable reference: Gold standard sequences append-only
- Versioned artifacts: Observer prompts from `observer_prompts` collection

### ✅ Fail-Fast Over Graceful Degradation
- Raw logging failure halts collection (Constitution VI)
- Parsing errors preserve raw responses in `processing_failures` collection
- Schema validation errors raise before insert
- Incomplete trajectories flagged but not silently dropped

### Specification-Driven Development
- spec.md completed with user scenarios, requirements, success criteria
- research.md resolves technical decisions (benign datasets, detector architecture)
- This plan.md defines implementation structure
- tasks.md deferred to `/speckit.tasks` command

**Gate Status**: ✅ PASSED - All constitutional principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/003-session-temporal-tracking/
├── spec.md              # Feature specification ✅
├── plan.md              # This file ✅
├── research.md          # Phase 0 output ✅
├── data-model.md        # Phase 1 output (pending)
├── quickstart.md        # Phase 1 output (pending)
├── contracts/           # Phase 1 output (pending)
│   └── api.md          # Detector and pattern interfaces
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── database/
│   ├── schemas/
│   │   └── phase3_evaluation.py              # ✅ Pydantic models validated on 50 examples
│   ├── migrations/
│   │   ├── create_phase3_collections.py      # NEW: ArangoDB collection setup
│   │   └── create_benign_sequences.py        # NEW: Benign dataset import
│   └── queries/
│       └── phase3_trajectory_queries.py      # NEW: AQL queries for pattern analysis
│
├── evaluation/
│   ├── temporal/                             # NEW: Temporal detection components
│   │   ├── __init__.py
│   │   ├── detector.py                       # TemporalDetector ABC, DetectionResult
│   │   ├── trust_ema.py                      # TrustEMADetector initial implementation
│   │   ├── pattern.py                        # Pattern ABC (gradual drift, sustained I, cross-dimensional)
│   │   └── factory.py                        # Detector factory for pluggable logic
│   └── prompts.py                            # ✅ Reuse Phase 2 observer (v2.1-c)
│
├── pipeline/                                 # NEW: Multi-turn evaluation pipeline
│   ├── __init__.py
│   ├── sequence_loader.py                    # Load XGuard/MHJ/benign sequences
│   ├── batch_evaluator.py                    # Evaluate all turns in sequence
│   └── trajectory_analyzer.py                # Run temporal detector on trajectories
│
└── cli/
    └── evaluate_multiturn.py                 # NEW: CLI for Phase 3 validation

scripts/
└── extract_benign_sequences.py               # NEW: TensorTrust/ShareGPT benign extraction

tests/
├── unit/
│   ├── test_temporal_detector.py             # NEW: Detector unit tests
│   ├── test_patterns.py                      # NEW: Pattern logic tests
│   └── test_phase3_schema.py                 # ✅ Schema validation (50 examples)
├── integration/
│   ├── test_batch_evaluation.py              # NEW: Real observer API calls
│   └── test_trajectory_storage.py            # NEW: ArangoDB round-trip
└── validation/
    ├── test_xguard_detection.py              # NEW: XGuard-Train validation
    ├── test_mhj_detection.py                 # NEW: MHJ validation
    └── test_benign_fp_rate.py                # NEW: 0% FP validation
```

**Structure Decision**: Single project structure (Option 1). Phase 3 extends existing PromptGuard2 codebase with temporal tracking components. No separate backend/frontend or mobile app. Research validation scripts in `scripts/`, CLI commands in `src/cli/`, reusable temporal logic in `src/evaluation/temporal/`.

## Complexity Tracking

*GATE: Constitution requires justification for violations. No violations identified.*

No complexity violations. This feature:
- Extends existing codebase (not new project)
- Reuses Phase 2 observer framework (not reimplementing)
- Adds temporal layer to proven single-turn detection
- Pluggable architecture enables experimentation without restructuring

**Simplicity maintained**:
- Direct ArangoDB storage (no repository pattern abstraction)
- Factory pattern only where empirical exploration required (FR-011, FR-012)
- Batch processing (no complex streaming/queueing infrastructure)

---

## Phase 0: Research Decisions (Complete)

See [research.md](./research.md) for full technical decisions.

**Key Outcomes**:

1. **Benign Datasets**: TensorTrust non-attack (50) + ShareGPT (50) = 100 benign sequences
2. **Temporal Detector**: Factory pattern, TrustEMA initial implementation with EMA + slope detection
3. **Pattern Components**: Composable patterns (gradual drift, sustained indeterminacy, cross-dimensional divergence)
4. **ArangoDB Schema**: Two collections (sequences, evaluations), indexed for trajectory queries
5. **Pipeline Integration**: Batch evaluation with Phase 2 observer, raw logging before parsing

**All NEEDS CLARIFICATION resolved**: No blockers for Phase 1 implementation.

---

## Phase 1: Design Artifacts (Next Steps)

### data-model.md

Will document:
- ArangoDB collection schemas (evaluation_sequences, principle_evaluations)
- Pydantic model mapping (phase3_evaluation.py → ArangoDB documents)
- Index design for trajectory queries
- Experiment tagging structure
- Provenance fields (raw_response, experiment_id, observer_prompt_version)

### contracts/api.md

Will define:
- `TemporalDetector` interface (detect() signature, DetectionResult schema)
- `Pattern` interface (composable pattern logic)
- `DetectorFactory` (registration, selection by name)
- Pipeline contracts (SequenceLoader, BatchEvaluator, TrajectoryAnalyzer)

### quickstart.md

Will provide:
1. Run Phase 3 migration: `uv run python src/database/migrations/create_phase3_collections.py`
2. Extract benign sequences: `uv run python scripts/extract_benign_sequences.py`
3. Evaluate XGuard sample: `uv run python src/cli/evaluate_multiturn.py --dataset xguard --sample 10`
4. Query trajectories: Example AQL queries for pattern analysis
5. Run full validation: `pytest tests/validation/test_xguard_detection.py`

---

## Implementation Phases (Post-Planning)

### Phase 1: Infrastructure (Tasks 1-10)
- ArangoDB collections and migrations
- Pydantic schema integration
- Benign dataset extraction
- Raw logging pipeline

### Phase 2: Temporal Detection (Tasks 11-20)
- TemporalDetector ABC and factory
- TrustEMA detector implementation
- Pattern components (3 initial patterns)
- Integration with observer framework

### Phase 3: Pipeline & CLI (Tasks 21-30)
- Sequence loader (XGuard, MHJ, benign)
- Batch evaluator with turn-by-turn evaluation
- Trajectory analyzer (detector application)
- CLI for multi-turn evaluation

### Phase 4: Validation (Tasks 31-40)
- Integration tests (real API calls)
- XGuard-Train validation (600 seqs)
- MHJ validation (537 seqs)
- Benign FP test (100 seqs, 0% FP)
- Stateless baseline comparison
- Success criteria verification (SC-001 through SC-008)

---

## References

- **Phase 2 Observer Framework**: src/evaluation/prompts.py (ayni_relational v2.1-c)
- **Validated Schema**: src/database/schemas/phase3_evaluation.py
- **Constitution v2.0.0**: .specify/memory/constitution.md
- **TLA+ Specifications**: TrustEMA.tla, CircuitBreaker.tla, TemporalReciprocity.tla
- **Dataset Documentation**: docs/phase3_dataset_summary.md
- **Previous Planning**: docs/phase3_planning.md, docs/multi_turn_dataset_investigation.md

---

**Next Command**: `/speckit.tasks` to generate implementation tasks from this plan.
