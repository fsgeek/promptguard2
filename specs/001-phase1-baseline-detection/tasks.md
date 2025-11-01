# Tasks: Phase 1 Baseline Detection

**Input**: Design documents from `/specs/001-phase1-baseline-detection/`
**Prerequisites**: plan.md, spec.md

**Tests**: Integration tests with real API calls required per constitution (Tier 2 empirical integrity)

**Organization**: Tasks organized by functional requirement (FR1-FR6) to enable independent implementation and validation.

## Format: `[ID] [P?] [FR] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[FR]**: Which functional requirement this task belongs to (e.g., FR1, FR2, FR3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/`, `config/`, `data/` at repository root
- Python 3.11+ with async/await
- ArangoDB for storage, OpenRouter for API calls

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure per plan.md
- [X] T002 Initialize Python project with pyproject.toml (dependencies: python-arango, httpx, instructor, pydantic, pytest)
- [X] T003 [P] Create config/database.yaml for ArangoDB connection settings (host, port, database name, credentials placeholder)
- [X] T004 [P] Create config/experiments.yaml with Phase 1 experiment definitions (exp_phase1_step1_baseline_v1, exp_phase1_step2_pre_filter_v1)
- [X] T005 [P] Create .env.example with OPENROUTER_API_KEY and ARANGODB_PROMPTGUARD_PASSWORD placeholders
- [X] T006 [P] Create data/experiments/ directory structure
- [X] T007 [P] Create reports/ directory for output

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY functional requirement can be implemented

**⚠️ CRITICAL**: No FR work can begin until this phase is complete

- [X] T009 [NFR1] Create ArangoDB client in src/database/client.py with connection pooling
- [X] T010 [P] [NFR1] [NFR4] Create OpenRouter API client in src/api/openrouter.py with metadata tagging support
- [X] T011 [P] [NFR2] Create rate limiter in src/api/rate_limiter.py (10 concurrent, exponential backoff, max 3 retries)
- [X] T012 [P] [NFR1] Create raw response logger in src/logging/raw_logger.py (JSONL format, atomic writes)
- [X] T013 [P] [NFR1] Create experiment logger in src/logging/experiment_logger.py
- [X] T014 [P] [NFR2] Create base evaluation pipeline in src/evaluation/pipeline.py (async, fail-fast error handling - halt on data-spoiling errors, capture diagnostics and continue on recoverable errors like JSON parsing)
- [X] T015 [P] [NFR1] Create model slug normalization utility (replace / and . with _)
- [X] T016 [P] [NFR5] Create checkpoint manager with atomic rename (write .tmp, rename to .json)

**Checkpoint**: Foundation ready - functional requirement implementation can now begin in parallel

---

## Phase 3: FR1 - Database Migration (Priority: P1) 🎯

**Goal**: Migrate 762 labeled attacks from old PromptGuard to PromptGuard2

**Independent Test**: Query PromptGuard2 database shows 762 attacks with valid labels

### Database Schema for FR1

- [X] T017 [P] [FR1] Create attacks schema in src/database/schemas/attacks.py
- [X] T018 [P] [FR1] Create experiments schema in src/database/schemas/experiments.py
- [X] T019 [P] [FR1] Create observer_prompts schema in src/database/schemas/observer_prompts.py
- [X] T020 [P] [FR1] Create models schema in src/database/schemas/models.py
- [X] T020a [FR1] Populate models collection from old PromptGuard models collection (depends on T009 DB client; migrate 7 models with metadata: frontier, testing, observer_framing_compatible, rlhf, cost_per_1m_tokens; if insufficient models configured, halt with error message requiring manual validation)
- [X] T021 [P] [FR1] Create processing_failures schema in src/database/schemas/processing_failures.py

### Migration Implementation for FR1

- [X] T022 [FR1] Implement migration script in src/database/migrations/001_migrate_attacks.py (connect to old DB, extract 762 attacks, insert to PromptGuard2)
- [X] T023 [FR1] Add migration CLI command in src/cli/migrate.py with --verify flag
- [X] T024 [FR1] Create test fixture with 5 sample attacks in tests/fixtures/sample_attacks.json

### Integration Test for FR1

- [X] T025 [FR1] Create migration integration test in tests/integration/test_migration.py (verify 762 count, label distribution, metadata integrity)

**Checkpoint**: FR1 complete - 762 attacks available in PromptGuard2 for Step 1

---

## Phase 4: FR2 - Step 1 Baseline Collection (Priority: P1) 🎯 MVP Core

**Goal**: Collect 3,810 baseline responses (762 attacks × 5 models) without filtering

**Independent Test**: Run with --test-mode --samples 5, verify 25 responses (5 attacks × 5 models) logged

### Database Schema for FR2

- [X] T026 [FR2] Create step1_baseline_responses schema in src/database/schemas/step1_baseline_responses.py
- [X] T026a [P] [FR3] Create gold_standard_classifications schema in src/database/schemas/gold_standard_classifications.py

### Step 1 Implementation

- [X] T027 [P] [FR2] Create Step 1 baseline pipeline in src/evaluation/step1_baseline.py (async, 10 concurrent, checkpoint recovery)
- [X] T028 [P] [FR2] Create Step 1 CLI command in src/cli/step1.py with --test-mode, --samples, --resume, --full flags
- [X] T029 [FR2] Add interactive confirmation prompt after test-mode succeeds ("Proceed with full collection (3,810 evals)? [y/N]")
- [X] T030 [FR2] Implement checkpoint persistence per spec schema (data/experiments/{experiment_id}/checkpoint.json: {completed_attacks: [], failed_attempts: {}, started: ISO8601, last_updated: ISO8601}, atomic rename)
- [X] T031 [FR2] Implement progress logging (console output every 50 evaluations, ETA calculation)
- [X] T032 [FR2] Add OpenRouter metadata tagging (experiment_id, attack_id, step, evaluation_type)

### Integration Test for FR2

- [X] T033 [FR2] Create Step 1 integration test in tests/integration/test_step1_pipeline.py (real API calls on 5 samples, verify raw logging, cost tracking, checkpoint, fail-fast on data-spoiling errors - test with invalid API key expects EvaluationError, test with malformed response captures diagnostics and continues)

**Checkpoint**: FR2 complete - Step 1 baseline data collection functional

---

## Phase 5: FR3 - Compliance Classification (Priority: P1) 🎯 MVP Core

**Goal**: Classify 3,810 responses as comply/refuse/unclear with hybrid approach

**Independent Test**: Classify 5 sample responses, verify >90% agreement with manual gold standard

### Classification Implementation

- [X] T034 [P] [FR3] Create compliance classifier in src/evaluation/classifiers/compliance.py (uses Claude 4.5 Haiku, logs reasoning)
- [X] T035 [P] [FR3] Create compliance classifier prompt in src/evaluation/prompts/compliance_classifier.py
- [X] T036 [FR3] Implement gold standard annotation workflow (stratified sample: 50 attacks proportional to ground_truth distribution from 762 total, Claude annotates with reasoning, output CSV for Tony review, store in gold_standard_classifications collection as immutable data)
- [X] T037 [FR3] Implement automated classification with >90% agreement validation
- [X] T038 [FR3] Add reciprocal prompt auto-classification logic (ground_truth == "reciprocal" → "comply")

### Unit Test for FR3

- [X] T039 [FR3] Create compliance classifier unit test in tests/unit/test_compliance_classifier.py

**Checkpoint**: FR3 complete - Compliance classification functional

---

## Phase 6: FR4 - Step 2 Pre-filter Collection (Priority: P2)

**Goal**: Evaluate 762 attacks with observer framing, send passed attacks to target LLMs

**Independent Test**: Run with --test-mode --samples 5, verify observer evaluation + target LLM responses for passed attacks

### Database Schema for FR4

- [X] T040 [FR4] Create step2_pre_evaluations schema in src/database/schemas/step2_pre_evaluations.py

### Observer Framing Implementation

- [X] T041 [P] [FR4] Create neutrosophic parser in src/evaluation/classifiers/neutrosophic.py (parse T, I, F scores, validate [0,1] range)
- [X] T042 [P] [FR4] Migrate observer prompt v2.1 from old PromptGuard prompt_configurations collection (query for prompt_type="pre_eval", version=1, created ~2025-10-24, validate non-empty prompt_text, insert to observer_prompts with _key="v2.1_observer_framing", created=ISO8601, created_by from old record, verify retrieval)
- [X] T042a [FR4] Verify observer prompt migration (query observer_prompts collection _key="v2.1_observer_framing", confirm prompt_text contains "You are observing an exchange" and "neutrosophic logic" keywords, validate against spec definition of neutral reciprocity framing)
- [X] T043 [P] [FR4] Create Step 2 pre-filter pipeline in src/evaluation/step2_prefilter.py (observer eval, detection threshold F >= 0.7, target model exclusion)
- [X] T044 [FR4] Create Step 2 CLI command in src/cli/step2.py with --test-mode, --samples, --full flags, --observer-model option
- [X] T045 [FR4] Implement Step 1 response reuse logic (match attack_id + model, skip API call if exists)
- [X] T046 [FR4] Add target model exclusion logic (if observer = Haiku, exclude Haiku from targets)

### Integration Test for FR4

- [X] T047 [FR4] Create Step 2 integration test in tests/integration/test_step2_pipeline.py (real API calls, verify observer scores, detection logic, response reuse)

### Unit Test for FR4

- [X] T048 [FR4] Create neutrosophic parser unit test in tests/unit/test_neutrosophic_parser.py

**Checkpoint**: FR4 complete - Step 2 pre-filter collection functional

---

## Phase 7: FR5 - Comparative Analysis (Priority: P2)

**Goal**: Generate publishable Markdown report comparing Step 1 vs Step 2

**Independent Test**: Run analysis command, verify reports/phase1_comparative_analysis.md exists with all required metrics

### Analysis Implementation

- [X] T049 [P] [FR5] Create comparative analysis in src/analysis/comparative.py (detection rates by category, false positives, improvement metrics)
- [X] T050 [P] [FR5] Create executor vs observer analysis in src/analysis/executor_observer.py (models complying in Step 1 but detecting in Step 2)
- [X] T051 [FR5] Create report generator in src/analysis/reports.py (Markdown output at reports/phase1_comparative_analysis.md)
- [X] T052 [FR5] Create analysis CLI command in src/cli/analyze.py with --phase1 flag

**Checkpoint**: FR5 complete - Comparative analysis report generation functional

---

## Phase 8: FR6 - Decision Gate (Priority: P3)

**Goal**: Execute data-driven decision logic for Phase 2 progression

**Independent Test**: Run decision gate command, verify decision output with rationale

### Decision Gate Implementation

- [X] T053 [FR6] Implement decision gate logic in src/cli/analyze.py with --decision-gate flag (calculate miss rate, output recommendation)
- [X] T054 [FR6] Add decision documentation to reports/phase1_decision_gate.md

**Checkpoint**: FR6 complete - Decision gate functional, Phase 1 research complete

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple functional requirements

- [X] T055 [P] Add README.md with quickstart instructions
- [ ] T056 [P] Add requirements.txt or pyproject.toml finalization
- [X] T057 [P] Add .gitignore for data/, .env, __pycache__
- [X] T058 Code cleanup and type hints validation
- [X] T059 Security audit (API key handling, rate limiting verification)
- [ ] T060 Performance validation (verify 2-4 hour runtime on full dataset)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all FRs
- **FR1 (Phase 3)**: Depends on Foundational - BLOCKS FR2, FR4
- **FR2 (Phase 4)**: Depends on FR1 (needs attacks) - BLOCKS FR3, FR4, FR5
- **FR3 (Phase 5)**: Depends on FR2 (needs responses) - BLOCKS FR5
- **FR4 (Phase 6)**: Depends on FR1 (needs attacks) and FR2 (can reuse responses) - BLOCKS FR5
- **FR5 (Phase 7)**: Depends on FR2, FR3, FR4 (needs all data) - BLOCKS FR6
- **FR6 (Phase 8)**: Depends on FR5 (needs analysis)
- **Polish (Phase 9)**: Depends on all desired FRs being complete

### Critical Path

```
Setup → Foundational → FR1 → FR2 → FR3 → FR4 → FR5 → FR6
                         ↓     ↓            ↓
                      (attacks)(responses)(pre-eval)
```

### Parallel Opportunities

**Within Setup (Phase 1)**:
- T003-T007 can all run in parallel

**Within Foundational (Phase 2)**:
- T010-T016 can all run in parallel after T009 completes

**Within FR1 (Phase 3)**:
- T017-T021 (schemas) can all run in parallel
- T020a runs after T009 (requires DB client), sequential with schema creation
- T024-T025 (tests) can run in parallel after T022-T023

**Within FR2 (Phase 4)**:
- T027-T028 can run in parallel

**Within FR3 (Phase 5)**:
- T034-T035 can run in parallel
- T037-T038 can run in parallel after T036

**Within FR4 (Phase 6)**:
- T041-T042 can run in parallel

**Within FR5 (Phase 7)**:
- T049-T050 can run in parallel

---

## Parallel Example: FR2 (Step 1 Baseline)

```bash
# Launch schema and pipeline implementation together:
Task: "Create step1_baseline_responses schema in src/database/schemas/step1_baseline_responses.py"
Task: "Create Step 1 baseline pipeline in src/evaluation/step1_baseline.py"
Task: "Create Step 1 CLI command in src/cli/step1.py"
```

---

## Implementation Strategy

### MVP First (FR1 + FR2 + FR3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all FRs)
3. Complete Phase 3: FR1 (Database Migration)
4. Complete Phase 4: FR2 (Step 1 Baseline Collection)
5. Complete Phase 5: FR3 (Compliance Classification)
6. **STOP and VALIDATE**: Test Step 1 pipeline end-to-end with 5 samples
7. Run full collection (3,810 evaluations)
8. Classify all responses
9. **DECISION POINT**: MVP functional - can analyze baseline RLHF behavior

### Full Phase 1 Delivery

1. Complete MVP (FR1 + FR2 + FR3)
2. Complete Phase 6: FR4 (Step 2 Pre-filter Collection)
3. Complete Phase 7: FR5 (Comparative Analysis)
4. Complete Phase 8: FR6 (Decision Gate)
5. **STOP and VALIDATE**: Publishable result ready
6. Execute decision gate → Publish or proceed to Phase 2

### Incremental Validation Gates

- **After FR1**: Verify 762 attacks migrated correctly
- **After FR2 test mode**: Verify 5-sample collection works (25 responses)
- **After FR2 full run**: Verify 3,810 responses collected
- **After FR3**: Verify classification agreement >90%
- **After FR4 test mode**: Verify observer framing works on 5 samples
- **After FR4 full run**: Verify 762 pre-evaluations complete
- **After FR5**: Verify report generated with all metrics
- **After FR6**: Execute decision gate, document outcome

---

## Notes

- [P] tasks = different files, no dependencies
- [FR] label maps task to specific functional requirement for traceability
- Each FR should be independently completable and testable
- Verify integration tests pass with real API calls before full runs
- Use --test-mode --samples 5 for all validation gates
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
- Constitutional requirements: Raw logging before parsing, fail-fast errors, 5-sample pre-collection validation

---

## Task Summary

**Total Tasks**: 62
- Setup: 7 tasks (removed T004 config/models.yaml - models stored in DB per Constitutional Principle VII)
- Foundational: 8 tasks
- FR1 (Migration): 10 tasks (added T020a models population, T042a observer prompt verification)
- FR2 (Baseline): 8 tasks
- FR3 (Classification): 7 tasks (added T026a gold standard schema)
- FR4 (Pre-filter): 10 tasks (added T042a)
- FR5 (Analysis): 4 tasks
- FR6 (Decision Gate): 2 tasks
- Polish: 6 tasks

**Parallel Opportunities**: 30 tasks marked [P] (T020a now depends on T009)

**MVP Scope**: Phases 1-5 (37 tasks) → Baseline RLHF behavior analysis
**Full Delivery**: All phases (62 tasks) → Complete Phase 1 research with decision gate
