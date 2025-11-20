# Implementation Tasks: Session-Based Temporal Tracking

**Feature Branch**: `003-session-temporal-tracking`
**Created**: 2025-11-18
**Status**: Ready for Implementation
**Source**: spec.md, plan.md, research.md, src/database/schemas/phase3_evaluation.py

## Task Organization

Tasks are organized by implementation phase with strict dependency tracking. Tasks marked `[P]` can be parallelized with other `[P]` tasks in the same phase. User story labels `[US1]`, `[US2]`, `[US3]` indicate which acceptance criteria the task serves.

**MVP Scope**: Phase 3 (User Story 1) - Evaluate Multi-Turn Sequences
**Full Scope**: Phases 3-5 (All User Stories)

---

## Phase 1: Setup & Infrastructure (Foundation)

**Goal**: Establish directory structure, dependencies, and test framework.
**Blockers**: None - can start immediately.

### Checklist

- [X] T001 [P] Create directory structure for Phase 3 temporal evaluation components
  - Create `src/evaluation/temporal/` directory with `__init__.py`
  - Create `src/pipeline/` directory with `__init__.py`
  - Create `src/database/queries/` directory with `__init__.py`
  - Create `tests/integration/` directory (if not exists)
  - Create `tests/validation/` directory (if not exists)
  - Create `scripts/` directory (if not exists)
  - Create `logs/` directory for raw API response logging

- [X] T002 [P] Verify Python dependencies in pyproject.toml
  - Check `arango-python` (ArangoDB driver)
  - Check `pydantic>=2.0` (schema validation)
  - Check `pandas` (dataset loading)
  - Check `openai` or `openrouter-python-sdk` (observer API calls)
  - Add any missing dependencies to `pyproject.toml`
  - Run `uv sync` to install

- [X] T003 [P] Configure pytest for Phase 3 integration and validation tests
  - Add `tests/integration/conftest.py` with ArangoDB fixtures
  - Add `tests/validation/conftest.py` with dataset fixtures
  - Configure pytest markers: `@pytest.mark.integration`, `@pytest.mark.validation`
  - Document test invocation: `pytest tests/integration/` vs `pytest tests/validation/`

**Parallel Execution**: All T001-T003 can run in parallel.

---

## Phase 2: Foundational Components (Blocks All User Stories)

**Goal**: Set up ArangoDB collections, extract benign sequences, verify Phase 2 observer access.
**Blockers**: Phase 1 complete.

### Checklist

- [X] T004 [US1] Create ArangoDB migration for phase3_evaluation_sequences collection
  - File: `src/database/migrations/create_phase3_collections.py`
  - Collection: `phase3_evaluation_sequences`
  - Schema: `_key` (attack_id), `label`, `source_dataset`, `turns[]`, `metadata{}`, `created_at`
  - Indexes: hash on `source_dataset`, hash on `label`, persistent on `created_at`
  - Document schema before collection creation (Constitution VI)
  - Test: Run migration, verify collection exists and empty
  - **COMPLETED**: 2025-11-18 - Collection created with 4 indexes (including primary)

- [X] T005 [P] [US1] Create ArangoDB migration for phase3_principle_evaluations collection
  - File: `src/database/migrations/create_phase3_collections.py` (same file as T004)
  - Collection: `phase3_principle_evaluations`
  - Schema: `_key` (composite: `{attack_id}_{principle}_{turn_number}`), `attack_id`, `principle`, `turn_number`, `evaluator_model`, `observer_prompt_version`, `timestamp`, `scores{T,I,F}`, `reasoning`, `raw_response`, `model_temperature`, `experiment_id`, `cost_usd`, `latency_ms`
  - Indexes: hash on `[attack_id, principle]`, hash on `[attack_id, turn_number]`, hash on `experiment_id`, persistent on `timestamp`, hash on `principle`
  - Test: Run migration, verify collection exists and empty
  - **COMPLETED**: 2025-11-18 - Collection created with 6 indexes (including primary)

- [X] T006 [P] [US2] Extract benign sequences from TensorTrust and ShareGPT
  - File: `scripts/extract_benign_sequences.py`
  - TensorTrust: Filter `output_is_access_granted==False AND no_extraction_keywords`, extract 50 sequences (3-8 turns)
    - Schema documented in `specs/003-session-temporal-tracking/tensortrust_schema.md`
    - Group by `defense_id`, sort by `timestamp`, filter by turn count and extraction keywords
    - Stratified sampling across turn counts (not just first 50)
  - ShareGPT: Download subset, filter conversational (exclude code), extract 50 sequences (3-8 turns)
  - Output: Insert into `phase3_evaluation_sequences` with `label=benign`
  - Validation: Verify 100 benign sequences inserted, check turn counts match attack datasets
  - Provenance: Log source URLs, filter criteria, timestamp
  - **COMPLETED**: 2025-11-18 - 50 TensorTrust benign sequences extracted (stratified sampling), ShareGPT skipped

- [X] T007 [P] [US1] Verify Phase 2 observer framework accessible
  - Query `observer_prompts` collection for document with `_key=v2.1-c`
  - Verify observer prompt contains reciprocity and context_integrity principles
  - Document prompt template structure for turn-by-turn evaluation
  - Test: Load prompt, format with sample turn, verify output format
  - **CRITICAL**: Do NOT modify v2.1-c prompt - reuse as-is
  - **COMPLETED**: 2025-11-18 - v2.1-c_combined verified with reciprocity and context_integrity principles

**Parallel Execution**: T004+T005 must complete before T006 (need collections). T007 is independent.

**Dependencies**:
- T004, T005 → T006 (benign extraction needs collections)
- All Phase 2 tasks must complete before Phase 3

---

## Phase 3: User Story 1 - Evaluate Multi-Turn Sequences (Priority: P1) 🎯 MVP

**Goal**: Detect gradual drift across 5-turn conversations. This is the minimum viable product.
**Blockers**: Phase 2 complete.

### Integration Tests (Test-First Approach)

- [X] T008 [P] [US1] Write batch evaluation integration test with real observer API
  - **COMPLETED**: 2025-11-18 - Integration test created in `tests/integration/test_batch_evaluation.py`
  - Test verifies BatchEvaluator with real API calls (skips if no API key)
  - Validates raw response logging, T/I/F score parsing, DB insertion, experiment_id tagging
  - File: `tests/integration/test_batch_evaluation.py`
  - Test: Load 5-turn XGuard sequence, evaluate all turns with Phase 2 observer (v2.1-c), verify T/I/F scores returned
  - Test: Verify raw API response logged to JSONL before parsing
  - Test: Verify PrincipleEvaluation documents inserted to ArangoDB
  - Test: Verify experiment_id tagged on all documents
  - Test: Verify cost tracking in evaluation result
  - **CRITICAL**: Use real API calls (not mocks) - Constitution II
  - Run with: `pytest tests/integration/test_batch_evaluation.py -v`

- [X] T009 [P] [US1] Write trajectory storage round-trip test
  - **COMPLETED**: 2025-11-18 - Tests created in `tests/integration/test_trajectory_storage.py`
  - Both tests pass successfully
  - Validates ArangoDB round-trip, trajectory ordering, multi-principle support
  - File: `tests/integration/test_trajectory_storage.py`

**Parallel Execution**: T008 and T009 can run in parallel (different test files).

### Implementation

- [X] T010 [P] [US1] Implement TemporalDetector ABC
  - **COMPLETED**: 2025-11-18 - `src/evaluation/temporal/detector.py` created
  - DetectionResult Pydantic model with attack_detected, confidence, trigger_turn, reasoning, pattern_name
  - TemporalDetector ABC with abstract detect() method and validation helper
  - File: `src/evaluation/temporal/detector.py`
  - Class: `TemporalDetector` (ABC with `@abstractmethod detect()`)
  - Class: `DetectionResult` (Pydantic model: `attack_detected`, `confidence`, `trigger_turn`, `reasoning`, `pattern_name`)
  - Interface: `detect(trajectories: List[PrincipleEvaluation], principle: str) -> DetectionResult`
  - Property: `name` (human-readable detector name)
  - Docstrings: Explain pluggable architecture (FR-011)

- [X] T011 [P] [US1] Implement TrustEMADetector
  - **COMPLETED**: 2025-11-18 - `src/evaluation/temporal/trust_ema.py` created
  - Implements EMA algorithm with slope detection from TLA+ spec
  - All 8 unit tests pass (test_trust_ema.py)
  - Detects gradual drift via EMA threshold crossing OR rapid slope
  - File: `src/evaluation/temporal/trust_ema.py`
  - Class: `TrustEMADetector(TemporalDetector)`
  - Parameters: `alpha` (EMA smoothing, default 0.3), `threshold` (detection threshold, default 0.7), `slope_threshold` (drift threshold, default 0.15)
  - Logic: Calculate EMA of F scores, detect threshold crossing OR rapid slope
  - Return: `DetectionResult` with trigger turn and reasoning
  - Test: Unit test with synthetic trajectory (F=[0.1, 0.2, 0.5, 0.8] should detect at turn 4)

- [X] T012 [P] [US1] Implement DetectorFactory
  - **COMPLETED**: 2025-11-18 - `src/evaluation/temporal/factory.py` created
  - Registry pattern for pluggable detectors
  - TrustEMADetector auto-registered
  - Supports register(), create(), list_detectors() methods
  - File: `src/evaluation/temporal/factory.py`
  - Class: `TemporalDetectorFactory` with `_registry: Dict[str, Type[TemporalDetector]]`
  - Method: `register(name: str, detector_class: Type[TemporalDetector])`
  - Method: `create(name: str, **kwargs) -> TemporalDetector`
  - Method: `list_detectors() -> List[str]`
  - Register: `TemporalDetectorFactory.register("trust_ema", TrustEMADetector)`
  - Test: Create detector by name, verify instance type

- [X] T013 [US1] Implement SequenceLoader for XGuard, MHJ, benign datasets
  - **COMPLETED**: 2025-11-18 - `src/pipeline/sequence_loader.py` created
  - XGuard-Train: Loads from Parquet (tested with 5 sequences)
  - Benign: Loads from ArangoDB phase3_evaluation_sequences
  - MHJ: Placeholder (not yet implemented)
  - Supports sampling and idempotent DB insertion
  - File: `src/pipeline/sequence_loader.py`
  - Class: `SequenceLoader` with method `load(dataset: str, sample: Optional[int]) -> List[EvaluationSequence]`
  - Support: `dataset=xguard_train` (load from Parquet/JSON), `dataset=mhj`, `dataset=benign`
  - Sample: If `sample=10`, load only first 10 sequences
  - Validation: Verify each sequence has `attack_id`, `label`, `turns[]`
  - Convert to Pydantic `EvaluationSequence` model
  - Insert to `phase3_evaluation_sequences` collection (idempotent via `_key=attack_id`)

- [X] T014 [US1] Implement BatchEvaluator with Phase 2 observer integration
  - **COMPLETED**: 2025-11-18 - `src/pipeline/batch_evaluator.py` created
  - CRITICAL: Raw API responses logged BEFORE parsing (Constitution VI)
  - Fail-fast on raw logging failures
  - Integrates with Phase 2 observer v2.1-c_combined
  - Uses OpenRouter API client with cost tracking
  - Async implementation with proper error handling
  - Idempotent DB insertions with composite keys
  - File: `src/pipeline/batch_evaluator.py`
  - Class: `BatchEvaluator` with method `evaluate_sequence(sequence: EvaluationSequence, principles: List[str]) -> EvaluationResult`
  - For each turn in sequence:
    - Load observer prompt v2.1-c from `observer_prompts` collection
    - Format prompt with principle and turn_number
    - Call OpenRouter API (use existing client from Phase 2)
    - **CRITICAL**: Log raw API response to JSONL BEFORE parsing (Constitution VI)
    - Parse response to extract T/I/F scores and reasoning
    - Create `PrincipleEvaluation` document with provenance (experiment_id, timestamp, raw_response, cost, latency)
    - Insert to `phase3_principle_evaluations` collection (idempotent via composite `_key`)
  - Error handling: Fail-fast on raw logging failure (Constitution VI), recoverable on parse failure
  - Return: `EvaluationResult` with success status and cost tracking

- [X] T015 [US1] Implement TrajectoryAnalyzer
  - **COMPLETED**: 2025-11-18 - `src/pipeline/trajectory_analyzer.py` created
  - Loads trajectories from ArangoDB via AQL queries
  - Creates detectors via TemporalDetectorFactory
  - Stores detection results in evaluation_sequences metadata
  - Supports multi-principle analysis
  - File: `src/pipeline/trajectory_analyzer.py`
  - Class: `TrajectoryAnalyzer` with method `analyze(attack_id: str, detector_name: str) -> Dict[str, DetectionResult]`
  - For each principle:
    - Load trajectory from `phase3_principle_evaluations` (filter by attack_id + principle, sort by turn_number)
    - Create detector via `TemporalDetectorFactory.create(detector_name)`
    - Call `detector.detect(trajectory, principle)`
    - Return detection results keyed by principle
  - Storage: Store detection results in `phase3_evaluation_sequences` metadata (embedded)

- [X] T016 [US1] Implement CLI evaluate_multiturn.py
  - **COMPLETED**: 2025-11-18 - `src/cli/evaluate_multiturn.py` created
  - Usage: `uv run python src/cli/evaluate_multiturn.py --dataset xguard_train --sample 10 --detector trust_ema`
  - Integrates SequenceLoader, BatchEvaluator, TrajectoryAnalyzer
  - Prints evaluation summary with cost tracking and detection results
  - Ready for sample validation (T017)
  - File: `src/cli/evaluate_multiturn.py`
  - Usage: `uv run python src/cli/evaluate_multiturn.py --dataset xguard --sample 10 --detector trust_ema`
  - Flags: `--dataset` (xguard_train|mhj|benign), `--sample` (int, optional), `--detector` (trust_ema, default)
  - Pipeline:
    1. Load sequences via `SequenceLoader`
    2. Evaluate each sequence via `BatchEvaluator`
    3. Analyze trajectories via `TrajectoryAnalyzer`
    4. Print summary (sequences evaluated, attacks detected, cost)
  - Logging: Progress bar, cost tracking, error summary

- [ ] T017 [US1] Run sample validation on 10 XGuard sequences with cost tracking
  - Command: `uv run python src/cli/evaluate_multiturn.py --dataset xguard_train --sample 10 --detector trust_ema`
  - Verify: 10 sequences evaluated, T/I/F trajectories stored, detection results logged
  - Cost: Track total cost (<$5 for 10 sequences, ~50 turns, haiku model)
  - Output: Summary report with detection rate, false positive rate (0% on benign)
  - Validation: Manually review 2-3 detected attacks for gradient drift pattern

**Parallel Execution**: T010-T012 can run in parallel (independent components). T013-T015 are sequential dependencies.

**Dependencies**:
- T008, T009 (tests) → T010-T012 (detector components)
- T010-T012 → T013-T015 (pipeline components depend on detectors)
- T013-T015 → T016 (CLI depends on pipeline)
- T016 → T017 (sample validation)

**MVP Completion**: After T017, User Story 1 is complete and demonstrates temporal tracking value.

---

## Phase 4: User Story 2 - Compare Stateless vs Temporal (Priority: P2)

**Goal**: Empirical validation showing temporal >80% vs stateless <30% on gradual attacks.
**Blockers**: Phase 3 complete (MVP).

### Validation Tests

- [ ] T018 [P] [US2] Implement XGuard-Train validation test
  - File: `tests/validation/test_xguard_detection.py`
  - Load: All 600 XGuard-Train sequences from `phase3_evaluation_sequences`
  - Run: Temporal detection (trust_ema) on all trajectories
  - Metrics: Detection rate, false negative rate, per-category breakdown
  - Target: >80% detection rate (SC-001)
  - Output: `xguard_validation_report.md` with results table

- [ ] T019 [P] [US2] Implement MHJ validation test
  - File: `tests/validation/test_mhj_detection.py`
  - Load: All 537 MHJ sequences from `phase3_evaluation_sequences`
  - Run: Temporal detection (trust_ema) on all trajectories
  - Metrics: Detection rate, false negative rate
  - Target: >70% detection rate (SC-003)
  - Output: `mhj_validation_report.md` with results table

- [ ] T020 [P] [US2] Implement benign false positive test
  - File: `tests/validation/test_benign_fp_rate.py`
  - Load: All 100 benign sequences from `phase3_evaluation_sequences`
  - Run: Temporal detection (trust_ema) on all trajectories
  - Metrics: False positive rate
  - Target: 0% false positive rate (SC-002)
  - Output: `benign_fp_report.md` with any false positives flagged for review

**Parallel Execution**: T018, T019, T020 can run in parallel (independent datasets).

### Implementation

- [ ] T021 [US2] Add stateless mode to CLI for baseline comparison
  - File: `src/cli/evaluate_multiturn.py` (extend)
  - Flag: `--mode` (temporal|stateless, default temporal)
  - Stateless mode: Evaluate each turn independently, flag if ANY turn exceeds F>0.7 threshold
  - Temporal mode: Use `TrajectoryAnalyzer` with detector
  - Output: Detection results for both modes side-by-side

- [ ] T022 [US2] Implement comparison report generator
  - File: `src/pipeline/comparison_report.py`
  - Function: `generate_comparison(stateless_results, temporal_results, dataset_name) -> str`
  - Report sections:
    - Overall detection rate (stateless vs temporal)
    - False positive rate (both modes)
    - Per-category breakdown (if dataset has categories)
    - Cost comparison (total API calls)
    - Statistical significance (p-value, chi-square test)
  - Output: Markdown report saved to `validation_reports/{dataset}_comparison.md`

- [ ] T023 [US2] Run full validation on 1,237 sequences with provenance logging
  - Command: Run validation tests T018-T020 sequentially
  - Stateless baseline: `uv run python src/cli/evaluate_multiturn.py --dataset xguard_train --mode stateless`
  - Temporal mode: Already run in Phase 3
  - Generate comparison: `uv run python -m src.pipeline.comparison_report`
  - Cost: Track total cost (~$100 for full dataset, haiku model)
  - Provenance: Verify experiment_id tagged on all evaluations
  - Output: Comparison report with statistical significance (SC-008)

**Dependencies**:
- T018-T020 (validation tests) run in parallel
- T021 (stateless mode) → T022 (comparison report)
- T021-T022 → T023 (full validation)

**Completion**: After T023, User Story 2 is complete with publication-ready empirical results.

---

## Phase 5: User Story 3 - Query Trajectory Patterns (Priority: P3)

**Goal**: Pattern discovery through trajectory queries (F slope, sustained I, cross-dimensional divergence).
**Blockers**: Phase 4 complete.

### Implementation

- [ ] T024 [P] [US3] Implement GradualDriftPattern component
  - File: `src/evaluation/temporal/pattern.py`
  - Class: `TrajectoryPattern` (ABC with `@abstractmethod detect()`)
  - Class: `PatternMatch` (Pydantic model: `matched`, `confidence`, `match_turns[]`, `reasoning`)
  - Class: `GradualDriftPattern(TrajectoryPattern)` with parameters `min_increase` (default 0.50), `window_size` (default 5)
  - Logic: Find max F increase within window, flag if exceeds threshold
  - Test: Synthetic trajectory with F=[0.1, 0.3, 0.6, 0.8] should match (increase 0.7 from turn 1 to 4)

- [ ] T025 [P] [US3] Implement SustainedIndeterminacyPattern component
  - File: `src/evaluation/temporal/pattern.py` (same file as T024)
  - Class: `SustainedIndeterminacyPattern(TrajectoryPattern)` with parameters `min_i_score` (default 0.60), `min_consecutive` (default 3)
  - Logic: Find longest consecutive run of I>threshold
  - Test: Synthetic trajectory with I=[0.65, 0.70, 0.68, 0.62] should match (4 consecutive turns above 0.60)

- [ ] T026 [P] [US3] Implement CrossDimensionalDivergencePattern component
  - File: `src/evaluation/temporal/pattern.py` (same file as T024)
  - Class: `CrossDimensionalDivergencePattern(TrajectoryPattern)` with parameters `reference_principle`, `divergent_principle`, `min_t_score`, `min_f_score`
  - Logic: Detect high T in reference principle while high F in divergent principle (requires multi-principle query)
  - Note: Requires extension to query layer for cross-principle analysis
  - Placeholder: Return `matched=False` with reasoning "Cross-dimensional pattern requires multi-principle query"

- [ ] T027 [US3] Implement trajectory query functions in AQL
  - File: `src/database/queries/phase3_trajectory_queries.py`
  - Function: `find_gradual_drift(min_increase: float, window_size: int) -> List[str]` (returns attack_ids)
  - Function: `find_sustained_indeterminacy(min_i_score: float, min_consecutive: int) -> List[str]`
  - Function: `find_cross_dimensional_divergence(ref_principle: str, div_principle: str, min_t: float, min_f: float) -> List[str]`
  - Implementation: Use AQL queries with trajectory aggregation
  - Test: Run on 50 sequences, verify results match pattern logic

- [ ] T028 [US3] Add pattern analysis CLI command
  - File: `src/cli/evaluate_multiturn.py` (extend)
  - Command: `uv run python src/cli/evaluate_multiturn.py analyze-patterns --pattern gradual_drift --threshold 0.50`
  - Flags: `--pattern` (gradual_drift|sustained_i|cross_dimensional), `--threshold` (float), `--dataset` (filter)
  - Output: List of attack_ids matching pattern, with trajectory visualization (ASCII plot or CSV export)

- [ ] T029 [US3] Run pattern discovery on 50 sequences, document novel patterns
  - Command: `uv run python src/cli/evaluate_multiturn.py analyze-patterns --pattern gradual_drift --threshold 0.50 --dataset xguard_train`
  - Analysis: Identify sequences with gradient drift that were NOT explicitly flagged in ground truth labels
  - Validation: Success criteria SC-006 (detect at least one novel pattern)
  - Output: `pattern_discovery_report.md` with novel patterns documented

- [ ] T029.5 [RESEARCH] Evaluate derivative-based pattern detection
  - **Purpose**: Investigate whether first-order derivatives (dT/dt, dI/dt, dF/dt) improve detection vs absolute values
  - Post-process: Calculate derivatives for all evaluated trajectories (delta from previous turn)
  - Metrics: velocity = ||(ΔT, ΔI, ΔF)||, direction = unit vector of change
  - Compare pattern detection rates:
    - Absolute: "Sustained I" = I>0.6 for 3+ turns
    - Derivative: "Sustained I" = dI/dt ≈ 0 while I>0.6 (indeterminacy persists despite new info)
    - Absolute: "Gradual drift" = F[end] - F[start] > 0.5
    - Derivative: "Gradual drift" = dF/dt > 0.12 for 3+ consecutive turns
  - Test cross-dimensional divergence: Δ(dT/dt across principles) reveals decorrelation
  - **Decision gate**: If derivatives improve detection, document Phase 3d proposal for first-class derivative storage
  - Output: `specs/003-session-temporal-tracking/research_note_derivatives.md` with empirical findings

**Parallel Execution**: T024-T026 can run in parallel (independent pattern components).

**Dependencies**:
- T024-T026 (patterns) → T027 (query functions)
- T027 → T028 (CLI command)
- T028 → T029 (pattern discovery)
- T029 → T029.5 (derivative research - requires evaluated trajectories)

**Completion**: After T029.5, User Story 3 is complete with pattern discovery capability and derivative analysis.

---

## Phase 6: Polish & Success Criteria Verification

**Goal**: Finalize documentation, verify all success criteria, optimize performance.
**Blockers**: Phases 3-5 complete.

### Checklist

- [ ] T030 [P] Update docs/phase3_dataset_summary.md with validation results
  - File: `docs/phase3_dataset_summary.md`
  - Sections: Dataset sources, sequence counts, turn distributions, detection rates, cost summary
  - Tables: XGuard results, MHJ results, benign FP rate, stateless vs temporal comparison
  - Provenance: Link to experiment_ids, raw data locations

- [ ] T031 [P] Verify all success criteria (SC-001 through SC-008)
  - SC-001: >80% detection on XGuard-Train gradual escalation ✓ (T018)
  - SC-002: 0% FP on benign multi-turn sequences ✓ (T020)
  - SC-003: >70% detection on MHJ real-world jailbreaks ✓ (T019)
  - SC-004: 100 sequences in <10 minutes ✓ (benchmark in T017)
  - SC-005: Pattern queries in <2 seconds on 500+ sequences ✓ (benchmark in T027)
  - SC-006: Novel attack pattern detected ✓ (T029)
  - SC-007: Principle addition to 100 sequences in <5 minutes ✓ (add test)
  - SC-008: Stateless vs temporal p<0.05 ✓ (T022)
  - Output: `success_criteria_checklist.md` with verification status

- [ ] T032 [P] Performance optimization (if needed)
  - Benchmark: 100 sequences evaluation time (target <10 min, SC-004)
  - Optimize: Batch ArangoDB inserts, concurrent API calls (max_concurrent limit)
  - Benchmark: Pattern query time (target <2 sec, SC-005)
  - Optimize: AQL query tuning, index verification
  - Test: Re-run benchmarks, verify targets met

- [ ] T033 [P] Code cleanup and finalization
  - Remove: Debug logging statements
  - Finalize: Error messages (user-friendly, actionable)
  - Docstrings: Verify all public methods documented
  - Type hints: Verify all functions have type annotations
  - Run: `mypy src/` for type checking
  - Run: `ruff check src/` for linting

- [ ] T034 [P] Generate data-model.md from implemented schema
  - File: `specs/003-session-temporal-tracking/data-model.md`
  - Extract schema definitions from T004-T005 migrations (collections, indexes)
  - Document: Pydantic→ArangoDB mapping (phase3_evaluation.py → collections)
  - Include: ER diagram showing attack_id links (sequences→evaluations)
  - Include: Example AQL queries from T027 (trajectory queries)
  - Include: Experiment tagging structure (experiment_id usage)
  - Purpose: Reference for Phase 3b developers, reproducibility

- [ ] T035 [P] Generate contracts/api.md from ABC interfaces
  - File: `specs/003-session-temporal-tracking/contracts/api.md`
  - Extract interface definitions from implemented ABCs:
    - TemporalDetector (detector.py): detect() signature, DetectionResult schema
    - TrajectoryPattern (pattern.py): Pattern ABC, PatternMatch schema
    - Pipeline contracts: SequenceLoader, BatchEvaluator, TrajectoryAnalyzer
  - Document: Method signatures, expected behaviors, extension points
  - Include: Example implementation (TrustEMADetector as reference)
  - Include: Factory registration pattern (how to add new detectors/patterns)
  - Purpose: Enable external detector/pattern contributions

- [ ] T036 [P] Generate quickstart.md from CLI usage
  - File: `specs/003-session-temporal-tracking/quickstart.md`
  - Steps (with example commands and expected output):
    1. Run Phase 3 migration: `uv run python src/database/migrations/create_phase3_collections.py`
    2. Extract benign sequences: `uv run python scripts/extract_benign_sequences.py`
    3. Evaluate sample: `uv run python src/cli/evaluate_multiturn.py --dataset xguard --sample 10`
    4. Query patterns: Example AQL queries for trajectory analysis
    5. Run full validation: `pytest tests/validation/test_xguard_detection.py`
  - Include: Expected output examples, troubleshooting common errors
  - Include: Cost estimates from T017/T023 validation runs
  - Include: Prerequisites (ArangoDB running, datasets downloaded, API keys set)
  - Purpose: Reproducibility for other researchers

**Parallel Execution**: All T030-T036 can run in parallel (independent tasks).

**Completion**: After T036, Phase 3 implementation is complete with full documentation and ready for merge.

---

## Dependencies Summary

### User Story Completion Order

1. **User Story 1 (P1)**: Phase 2 → Phase 3 → T017 sample validation ✓ MVP
2. **User Story 2 (P2)**: US1 complete → Phase 4 → T023 full validation ✓
3. **User Story 3 (P3)**: US2 complete → Phase 5 → T029 pattern discovery ✓

### Critical Path

```
Phase 1 (T001-T003)
  ↓
Phase 2 (T004-T007)
  ↓
Phase 3 Tests (T008-T009)
  ↓
Phase 3 Detector Components (T010-T012)
  ↓
Phase 3 Pipeline (T013-T015)
  ↓
Phase 3 CLI (T016)
  ↓
T017 Sample Validation ← MVP COMPLETE
  ↓
Phase 4 Validation Tests (T018-T020)
  ↓
Phase 4 Comparison (T021-T022)
  ↓
T023 Full Validation
  ↓
Phase 5 Patterns (T024-T026)
  ↓
Phase 5 Queries (T027)
  ↓
Phase 5 CLI (T028)
  ↓
T029 Pattern Discovery
  ↓
Phase 6 Polish (T030-T033) ← FULL COMPLETE
```

### Parallel Execution Examples

**Phase 1 (all parallel)**:
```bash
# Terminal 1
task T001: Create directory structure

# Terminal 2
task T002: Verify dependencies

# Terminal 3
task T003: Configure pytest
```

**Phase 3 Detector Components (all parallel)**:
```bash
# Terminal 1
task T010: Implement TemporalDetector ABC

# Terminal 2
task T011: Implement TrustEMADetector

# Terminal 3
task T012: Implement DetectorFactory
```

**Phase 4 Validation Tests (all parallel)**:
```bash
# Terminal 1
pytest tests/validation/test_xguard_detection.py

# Terminal 2
pytest tests/validation/test_mhj_detection.py

# Terminal 3
pytest tests/validation/test_benign_fp_rate.py
```

---

## Constitutional Requirements Checklist

Every implementation task MUST satisfy:

- ✅ **Raw API responses logged BEFORE parsing** (Constitution VI)
  - Implemented in: T014 (BatchEvaluator)
  - Verified in: T008 (integration test)

- ✅ **Experiment ID on every document**
  - Schema field: `experiment_id` in `PrincipleEvaluation`
  - Migration: T004-T005
  - Validation: T008, T009

- ✅ **Fail-fast on raw logging failures**
  - Error handling in: T014 (BatchEvaluator)
  - Test verification: T008

- ✅ **Cost tracking for empirical integrity** (Constitution II)
  - Tracked in: T014 (BatchEvaluator), T017 (sample validation), T023 (full validation)
  - Schema field: `cost_usd` in `PrincipleEvaluation`

- ✅ **Pydantic schema validation before ArangoDB insert**
  - Schema: `src/database/schemas/phase3_evaluation.py` (already validated)
  - Validation: T009 (round-trip test)

---

## Implementation Strategy

### Incremental Delivery

1. **Week 1**: Phase 1-2 (Setup + Foundation) → T007 complete
2. **Week 2**: Phase 3 (US1 MVP) → T017 sample validation → **Deliver MVP**
3. **Week 3**: Phase 4 (US2 Validation) → T023 full validation → **Deliver empirical results**
4. **Week 4**: Phase 5-6 (US3 Patterns + Polish) → T033 complete → **Deliver full feature**

### Testing Strategy

- **Unit tests**: T010-T012, T024-T026 (detector and pattern components)
- **Integration tests**: T008-T009 (real API calls, database round-trip)
- **Validation tests**: T018-T020 (full dataset evaluation)
- **Benchmarks**: T032 (performance optimization)

### Risk Mitigation

- **Observer prompt compatibility**: T007 verifies v2.1-c works for multi-turn (early validation)
- **API cost overrun**: T017 sample validation tracks cost before full dataset
- **False positive rate**: T020 benign test runs early to catch over-flagging
- **Performance issues**: T032 benchmarks before full validation

---

## Total Task Count

- **Phase 1**: 3 tasks (setup)
- **Phase 2**: 4 tasks (foundation)
- **Phase 3**: 10 tasks (US1 MVP)
- **Phase 4**: 6 tasks (US2 validation)
- **Phase 5**: 7 tasks (US3 patterns + derivative research)
- **Phase 6**: 7 tasks (polish + documentation)

**Total**: 37 tasks

**MVP**: 17 tasks (Phase 1-3)
**Full Feature**: 37 tasks (All phases)

**New tasks added**:
- T029.5: Derivative-based pattern detection research
- T034: Generate data-model.md
- T035: Generate contracts/api.md
- T036: Generate quickstart.md

---

## Next Steps

1. **Review this tasks.md**: Verify all acceptance criteria covered
2. **Execute Phase 1**: Start with T001-T003 (setup)
3. **Execute Phase 2**: Run T004-T007 (foundation)
4. **Deliver MVP**: Complete Phase 3 (T008-T017) for User Story 1
5. **Full validation**: Complete Phase 4-6 (T018-T033) for all user stories

**First Command**:
```bash
# Start with Phase 1 setup
mkdir -p src/evaluation/temporal src/pipeline src/database/queries tests/integration tests/validation scripts logs
```

**Questions Before Starting**: None - all clarifications resolved in research.md.
