# Implementation Tasks: Context Integrity Validation (Factorial Design)

**Feature**: Phase 2 Context Integrity Validation
**Branch**: `002-context-integrity-validation`
**Date**: 2025-11-11
**Design**: Factorial validation with three observer prompt variants (v2.1-a/b/c)

---

## Overview

This tasks.md implements a **factorial experimental design** for Phase 2 validation. Instead of testing a single combined observer prompt (v2.2), we test three variants independently to enable causal attribution:

- **v2.1-a**: v2.1 + turn-number parameter only (isolates turn-number effect)
- **v2.1-b**: v2.1 + context integrity principle only (isolates principle effect)
- **v2.1-c**: v2.1 + both changes combined (tests for interaction effects)

**Total Implementation**: 72 evaluations (24 attacks × 3 variants) at ~$3.60 cost
**MVP**: Phases 1-3 (~50 tasks) - Setup + Foundational + US1 Factorial Validation

---

## Phase 1: Setup & Verification (5 tasks)

**Purpose**: Verify Phase 1 completion and database readiness

- [ ] [T001] Verify Phase 1 Step 2 completion in `step2_pre_evaluations` collection at /home/tony/projects/promptguard/promptguard2
- [ ] [T002] Query and identify 24 alignment_lab false negatives (F < 0.7) from Phase 1 baseline at /home/tony/projects/promptguard/promptguard2
- [ ] [T003] Verify observer prompt v2.1_observer_framing exists in `observer_prompts` collection at /home/tony/projects/promptguard/promptguard2
- [ ] [T004] Test ArangoDB connection and verify write access to collections at /home/tony/projects/promptguard/promptguard2
- [ ] [T005] Test OpenRouter API access with Claude Haiku model at /home/tony/projects/promptguard/promptguard2

---

## Phase 2: Foundational Infrastructure (20 tasks)

**Purpose**: Create three observer variants, database schemas, and evaluation pipeline extensions

### Observer Prompt Creation (6 tasks)

- [ ] [T006] Create observer prompt v2.1-a text file with turn-number statement at /home/tony/projects/promptguard/promptguard2/src/evaluation/prompts/observer_v2_1_a.txt
- [ ] [T007] Create observer prompt v2.1-b text file with context integrity principle at /home/tony/projects/promptguard/promptguard2/src/evaluation/prompts/observer_v2_1_b.txt
- [ ] [T008] Create observer prompt v2.1-c text file with both changes combined at /home/tony/projects/promptguard/promptguard2/src/evaluation/prompts/observer_v2_1_c.txt
- [ ] [T009] Generate diff documentation comparing v2.1-a to baseline v2.1 at /home/tony/projects/promptguard/promptguard2/docs/observer_diffs/v2.1-a_diff.txt
- [ ] [T010] Generate diff documentation comparing v2.1-b to baseline v2.1 at /home/tony/projects/promptguard/promptguard2/docs/observer_diffs/v2.1-b_diff.txt
- [ ] [T011] Generate diff documentation comparing v2.1-c to baseline v2.1 at /home/tony/projects/promptguard/promptguard2/docs/observer_diffs/v2.1-c_diff.txt

### Database Schema & Migration (5 tasks)

- [ ] [T012] Create Pydantic model for ObserverPromptVariant with variant_type field at /home/tony/projects/promptguard/promptguard2/src/database/schemas/observer_prompt_variants.py
- [ ] [T013] Create Pydantic model for Phase2ValidationEvaluation with variant_group and delta_f fields at /home/tony/projects/promptguard/promptguard2/src/database/schemas/phase2_validation_evaluations.py
- [ ] [T014] Create migration script to create phase2_validation_evaluations collection with indexes at /home/tony/projects/promptguard/promptguard2/src/database/migrations/create_phase2_collections.py
- [ ] [T015] Create migration script to insert three observer prompt variants into observer_prompts collection at /home/tony/projects/promptguard/promptguard2/src/database/migrations/create_observer_variants_v2_1.py
- [ ] [T016] Run migrations and verify three variants exist in database at /home/tony/projects/promptguard/promptguard2

### Evaluation Pipeline Extensions (9 tasks)

- [ ] [T017] Add turn_number parameter support to evaluator base class at /home/tony/projects/promptguard/promptguard2/src/evaluation/evaluator_base.py
- [ ] [T018] Update observer evaluation to substitute {TURN_NUMBER} placeholder in prompts at /home/tony/projects/promptguard/promptguard2/src/evaluation/observer_evaluator.py
- [ ] [T019] Create query function to fetch 24 alignment_lab false negatives from Phase 1 at /home/tony/projects/promptguard/promptguard2/src/cli/query_validation_attacks.py
- [ ] [T020] Create experiment creation function for three factorial experiments at /home/tony/projects/promptguard/promptguard2/src/experiments/create_phase2_experiments.py
- [ ] [T021] Create validation evaluation storage function with variant_group field at /home/tony/projects/promptguard/promptguard2/src/database/storage/store_validation_evaluation.py
- [ ] [T022] Update raw response logger to tag by experiment_id for three variants at /home/tony/projects/promptguard/promptguard2/src/logging/raw_logger.py
- [ ] [T023] Create baseline F-score lookup function from step2_pre_evaluations at /home/tony/projects/promptguard/promptguard2/src/analysis/baseline_lookup.py
- [ ] [T024] Implement delta_f calculation (variant_F - baseline_F) at /home/tony/projects/promptguard/promptguard2/src/analysis/delta_calculations.py
- [ ] [T025] Create variant-specific reasoning pattern detection (mentions_turn_number, mentions_context_integrity) at /home/tony/projects/promptguard/promptguard2/src/analysis/reasoning_analysis.py

---

## Phase 3: US1 - Factorial Validation (40 tasks)

**User Story**: Validate constitutional amendment effects on 24 known false negatives using factorial design

### Pre-Validation (3 samples × 3 variants = 9 evaluations) (10 tasks)

- [ ] [T026] [US1] Create pre-validation CLI script with --test-mode flag at /home/tony/projects/promptguard/promptguard2/src/cli/validate_phase2.py
- [ ] [T027] [US1] Select 3 representative sample attacks from 24 false negatives at /home/tony/projects/promptguard/promptguard2
- [ ] [T028] [US1] Create test experiment records for three variants (suffixed with _test) at /home/tony/projects/promptguard/promptguard2
- [ ] [T029] [P] [US1] Run 3 pre-validation evaluations with v2.1-a (turn-number only) at /home/tony/projects/promptguard/promptguard2
- [ ] [T030] [P] [US1] Run 3 pre-validation evaluations with v2.1-b (context integrity only) at /home/tony/projects/promptguard/promptguard2
- [ ] [T031] [P] [US1] Run 3 pre-validation evaluations with v2.1-c (combined) at /home/tony/projects/promptguard/promptguard2
- [ ] [T032] [US1] Verify raw API responses logged for all 9 pre-validation evaluations at /home/tony/projects/promptguard/promptguard2/logs
- [ ] [T033] [US1] Verify parsing success and database insertion for all 9 evaluations at /home/tony/projects/promptguard/promptguard2
- [ ] [T034] [US1] Verify cost tracking (~$0.05 per eval, $0.45 total) at /home/tony/projects/promptguard/promptguard2
- [ ] [T035] [US1] Review observer reasoning patterns to confirm variant-specific signals (turn-number mentions, context integrity mentions) at /home/tony/projects/promptguard/promptguard2

### Full Validation Run (72 evaluations) (15 tasks)

- [ ] [T036] [US1] Create production experiment records for three variants (exp_phase2_v2.1_a_turn_number, exp_phase2_v2.1_b_context_integrity, exp_phase2_v2.1_c_combined) at /home/tony/projects/promptguard/promptguard2
- [ ] [T037] [US1] Implement validation loop for single variant with progress tracking at /home/tony/projects/promptguard/promptguard2/src/cli/validate_phase2.py
- [ ] [T038] [US1] Implement rate limiting (OpenRouter limits) and error handling at /home/tony/projects/promptguard/promptguard2/src/cli/validate_phase2.py
- [ ] [T039] [US1] Add cost accumulation and budget enforcement (<$5 total) at /home/tony/projects/promptguard/promptguard2/src/cli/validate_phase2.py
- [ ] [T040] [P] [US1] Run 24 evaluations with v2.1-a (turn-number only) at /home/tony/projects/promptguard/promptguard2
- [ ] [T041] [P] [US1] Run 24 evaluations with v2.1-b (context integrity only) at /home/tony/projects/promptguard/promptguard2
- [ ] [T042] [P] [US1] Run 24 evaluations with v2.1-c (combined) at /home/tony/projects/promptguard/promptguard2
- [ ] [T043] [US1] Verify all 72 evaluations stored in phase2_validation_evaluations collection at /home/tony/projects/promptguard/promptguard2
- [ ] [T044] [US1] Verify experiment_id linkage for all 72 evaluations (24 per variant) at /home/tony/projects/promptguard/promptguard2
- [ ] [T045] [US1] Verify baseline_f_score populated from Phase 1 data for all evaluations at /home/tony/projects/promptguard/promptguard2
- [ ] [T046] [US1] Verify delta_f calculated correctly (variant_F - baseline_F) for all evaluations at /home/tony/projects/promptguard/promptguard2
- [ ] [T047] [US1] Verify detected boolean set correctly (F >= 0.7) for all evaluations at /home/tony/projects/promptguard/promptguard2
- [ ] [T048] [US1] Update three experiment records with completion status and results at /home/tony/projects/promptguard/promptguard2
- [ ] [T049] [US1] Verify total cost is under $5 budget ($3.60 estimated) at /home/tony/projects/promptguard/promptguard2
- [ ] [T050] [US1] Verify all 72 raw API responses logged with experiment_id tags at /home/tony/projects/promptguard/promptguard2/logs

### Comparative Analysis Across 4 Conditions (15 tasks)

- [ ] [T051] [US1] Create query to compare detection rates across baseline + 3 variants at /home/tony/projects/promptguard/promptguard2/src/analysis/queries/detection_rate_comparison.py
- [ ] [T052] [US1] Calculate main effect A: v2.1-a detection rate vs baseline at /home/tony/projects/promptguard/promptguard2/src/analysis/main_effects.py
- [ ] [T053] [US1] Calculate main effect B: v2.1-b detection rate vs baseline at /home/tony/projects/promptguard/promptguard2/src/analysis/main_effects.py
- [ ] [T054] [US1] Calculate mean delta_f for each variant (v2.1-a, v2.1-b, v2.1-c) at /home/tony/projects/promptguard/promptguard2/src/analysis/delta_analysis.py
- [ ] [T055] [US1] Test for interaction effects: Is v2.1-c synergistic? (v2.1-c > v2.1-a + v2.1-b - baseline) at /home/tony/projects/promptguard/promptguard2/src/analysis/interaction_analysis.py
- [ ] [T056] [US1] Create Venn diagram analysis of attack overlap between variants at /home/tony/projects/promptguard/promptguard2/src/analysis/attack_overlap.py
- [ ] [T057] [US1] Identify attacks detected by v2.1-a only (not v2.1-b) at /home/tony/projects/promptguard/promptguard2/src/analysis/attack_overlap.py
- [ ] [T058] [US1] Identify attacks detected by v2.1-b only (not v2.1-a) at /home/tony/projects/promptguard/promptguard2/src/analysis/attack_overlap.py
- [ ] [T059] [US1] Identify attacks detected by both v2.1-a AND v2.1-b at /home/tony/projects/promptguard/promptguard2/src/analysis/attack_overlap.py
- [ ] [T060] [US1] Identify attacks missed by all three variants at /home/tony/projects/promptguard/promptguard2/src/analysis/attack_overlap.py
- [ ] [T061] [US1] Analyze observer reasoning: v2.1-a mentions turn-number rate at /home/tony/projects/promptguard/promptguard2/src/analysis/reasoning_analysis.py
- [ ] [T062] [US1] Analyze observer reasoning: v2.1-b mentions context integrity rate at /home/tony/projects/promptguard/promptguard2/src/analysis/reasoning_analysis.py
- [ ] [T063] [US1] Analyze observer reasoning: v2.1-c mentions both concepts rate at /home/tony/projects/promptguard/promptguard2/src/analysis/reasoning_analysis.py
- [ ] [T064] [US1] Run binomial test for statistical significance of detection rate improvements at /home/tony/projects/promptguard/promptguard2/src/analysis/statistical_tests.py
- [ ] [T065] [US1] Generate comparative summary report with all analysis metrics at /home/tony/projects/promptguard/promptguard2/src/cli/analyze_factorial.py

---

## Phase 4: US2 - Documentation (15 tasks)

**User Story**: Document constitutional amendment process and factorial design rationale

### Observer Variant Documentation (9 tasks)

- [ ] [T066] [US2] Document v2.1-a changes from baseline in observer prompt metadata at /home/tony/projects/promptguard/promptguard2/docs/observer_variants/v2.1-a_documentation.md
- [ ] [T067] [US2] Document v2.1-b changes from baseline in observer prompt metadata at /home/tony/projects/promptguard/promptguard2/docs/observer_variants/v2.1-b_documentation.md
- [ ] [T068] [US2] Document v2.1-c changes from baseline in observer prompt metadata at /home/tony/projects/promptguard/promptguard2/docs/observer_variants/v2.1-c_documentation.md
- [ ] [T069] [US2] Create side-by-side comparison table showing controlled changes at /home/tony/projects/promptguard/promptguard2/docs/observer_variants/factorial_comparison_matrix.md
- [ ] [T070] [US2] Document turn-number hypothesis (structural invariant) at /home/tony/projects/promptguard/promptguard2/docs/hypotheses/turn_number_hypothesis.md
- [ ] [T071] [US2] Document context integrity hypothesis (semantic framing) at /home/tony/projects/promptguard/promptguard2/docs/hypotheses/context_integrity_hypothesis.md
- [ ] [T072] [US2] Verify all three prompts in database have complete diff_from_baseline field at /home/tony/projects/promptguard/promptguard2
- [ ] [T073] [US2] Verify all three prompts have amendment_rationale in parameters at /home/tony/projects/promptguard/promptguard2
- [ ] [T074] [US2] Create query to compare prompt lengths and diff sizes across variants at /home/tony/projects/promptguard/promptguard2/src/analysis/queries/prompt_comparison.py

### Factorial Design Rationale (6 tasks)

- [ ] [T075] [US2] Document why factorial validation chosen over single v2.2 approach at /home/tony/projects/promptguard/promptguard2/docs/factorial_design/rationale.md
- [ ] [T076] [US2] Document cost-benefit analysis ($2.40 extra for causal attribution) at /home/tony/projects/promptguard/promptguard2/docs/factorial_design/cost_benefit.md
- [ ] [T077] [US2] Document controlled changes matrix (which variant tests which hypothesis) at /home/tony/projects/promptguard/promptguard2/docs/factorial_design/controlled_changes.md
- [ ] [T078] [US2] Document comparative analysis strategy (main effects, interaction effects) at /home/tony/projects/promptguard/promptguard2/docs/factorial_design/analysis_strategy.md
- [ ] [T079] [US2] Document six decision scenarios based on variant success patterns at /home/tony/projects/promptguard/promptguard2/docs/factorial_design/decision_scenarios.md
- [ ] [T080] [US2] Create constitutional amendment precedent document for future changes at /home/tony/projects/promptguard/promptguard2/docs/constitution/amendment_process_precedent.md

---

## Phase 5: US3 - Experiment Tracking (15 tasks)

**User Story**: Create validation experiment records with complete provenance

### Experiment Creation & Metadata (6 tasks)

- [ ] [T081] [US3] Create exp_phase2_v2.1_a_turn_number with parameters and validation_criteria at /home/tony/projects/promptguard/promptguard2
- [ ] [T082] [US3] Create exp_phase2_v2.1_b_context_integrity with parameters and validation_criteria at /home/tony/projects/promptguard/promptguard2
- [ ] [T083] [US3] Create exp_phase2_v2.1_c_combined with parameters and validation_criteria at /home/tony/projects/promptguard/promptguard2
- [ ] [T084] [US3] Populate experiment descriptions explaining which amendment was tested at /home/tony/projects/promptguard/promptguard2
- [ ] [T085] [US3] Set status timestamps (started, completed, last_updated) for all experiments at /home/tony/projects/promptguard/promptguard2
- [ ] [T086] [US3] Populate progress tracking (evaluations_completed, progress_pct) during validation at /home/tony/projects/promptguard/promptguard2

### Results Population (6 tasks)

- [ ] [T087] [US3] Calculate and store detection_rate for v2.1-a experiment results at /home/tony/projects/promptguard/promptguard2
- [ ] [T088] [US3] Calculate and store detection_rate for v2.1-b experiment results at /home/tony/projects/promptguard/promptguard2
- [ ] [T089] [US3] Calculate and store detection_rate for v2.1-c experiment results at /home/tony/projects/promptguard/promptguard2
- [ ] [T090] [US3] Calculate and store mean_delta_f and median_delta_f for all three experiments at /home/tony/projects/promptguard/promptguard2
- [ ] [T091] [US3] Store total_cost and duration_minutes for all three experiments at /home/tony/projects/promptguard/promptguard2
- [ ] [T092] [US3] Populate variant_specific_findings (mentions_turn_number_rate, common_reasoning_pattern) at /home/tony/projects/promptguard/promptguard2

### Provenance Validation (3 tasks)

- [ ] [T093] [US3] Verify all 72 evaluations link to one of three experiments via experiment_id at /home/tony/projects/promptguard/promptguard2
- [ ] [T094] [US3] Verify each experiment links to exactly 24 evaluations at /home/tony/projects/promptguard/promptguard2
- [ ] [T095] [US3] Create query to reconstruct full experiment lineage (experiment → evaluations → attacks) at /home/tony/projects/promptguard/promptguard2/src/analysis/queries/experiment_lineage.py

---

## Phase 6: Polish & Decision Gate (20 tasks)

**Purpose**: Generate reports, decision recommendation, and prepare for next phase

### Comparative Reports (8 tasks)

- [ ] [T096] Generate factorial validation summary report with 4-way comparison at /home/tony/projects/promptguard/promptguard2/reports/phase2_factorial_validation_report.md
- [ ] [T097] Generate per-variant detailed analysis (v2.1-a performance breakdown) at /home/tony/projects/promptguard/promptguard2/reports/phase2_v2.1-a_analysis.md
- [ ] [T098] Generate per-variant detailed analysis (v2.1-b performance breakdown) at /home/tony/projects/promptguard/promptguard2/reports/phase2_v2.1-b_analysis.md
- [ ] [T099] Generate per-variant detailed analysis (v2.1-c performance breakdown) at /home/tony/projects/promptguard/promptguard2/reports/phase2_v2.1-c_analysis.md
- [ ] [T100] Generate attack-level comparison table (all 24 attacks × 4 conditions) at /home/tony/projects/promptguard/promptguard2/reports/phase2_attack_comparison_matrix.csv
- [ ] [T101] Generate false negatives analysis (attacks missed by all variants) at /home/tony/projects/promptguard/promptguard2/reports/phase2_remaining_false_negatives.md
- [ ] [T102] Generate cost analysis report (breakdown by variant, cost per attack) at /home/tony/projects/promptguard/promptguard2/reports/phase2_cost_analysis.md
- [ ] [T103] Generate observer reasoning patterns report (keyword frequency by variant) at /home/tony/projects/promptguard/promptguard2/reports/phase2_reasoning_patterns.md

### Decision Logic Implementation (6 tasks)

- [ ] [T104] Implement Scenario 1 check: Only v2.1-c succeeds (adopt combined) at /home/tony/projects/promptguard/promptguard2/src/analysis/decision_gate.py
- [ ] [T105] Implement Scenario 2 check: Only v2.1-a succeeds (adopt turn-number) at /home/tony/projects/promptguard/promptguard2/src/analysis/decision_gate.py
- [ ] [T106] Implement Scenario 3 check: Only v2.1-b succeeds (adopt context integrity) at /home/tony/projects/promptguard/promptguard2/src/analysis/decision_gate.py
- [ ] [T107] Implement Scenario 4 check: Both succeed independently (analyze overlap, choose strategy) at /home/tony/projects/promptguard/promptguard2/src/analysis/decision_gate.py
- [ ] [T108] Implement Scenario 5 check: All fail (reject amendments, fall back to Option E) at /home/tony/projects/promptguard/promptguard2/src/analysis/decision_gate.py
- [ ] [T109] Implement Scenario 6 check: Partial success (refine and iterate recommendation) at /home/tony/projects/promptguard/promptguard2/src/analysis/decision_gate.py

### Decision Gate Execution (6 tasks)

- [ ] [T110] Run decision gate analysis on completed validation results at /home/tony/projects/promptguard/promptguard2
- [ ] [T111] Generate decision recommendation report with rationale at /home/tony/projects/promptguard/promptguard2/reports/phase2_factorial_decision_gate.md
- [ ] [T112] Document next steps based on decision (which variant to adopt as v2.2) at /home/tony/projects/promptguard/promptguard2/reports/phase2_next_steps.md
- [ ] [T113] Estimate Phase 2 Step 2 cost (762 attacks with chosen v2.2 variant) at /home/tony/projects/promptguard/promptguard2/reports/phase2_step2_estimate.md
- [ ] [T114] Create Phase 2 Step 2 proposal if validation succeeds at /home/tony/projects/promptguard/promptguard2/docs/phase2_step2_proposal.md
- [ ] [T115] Document lessons learned and factorial validation effectiveness at /home/tony/projects/promptguard/promptguard2/docs/phase2_step1_retrospective.md

---

## Testing & Validation Tasks (10 tasks)

**Purpose**: Ensure correctness before production run

### Unit Tests (5 tasks)

- [ ] [T116] Write unit tests for turn_number parameter substitution at /home/tony/projects/promptguard/promptguard2/tests/unit/test_turn_number_substitution.py
- [ ] [T117] Write unit tests for delta_f calculation at /home/tony/projects/promptguard/promptguard2/tests/unit/test_delta_calculations.py
- [ ] [T118] Write unit tests for variant-specific reasoning detection at /home/tony/projects/promptguard/promptguard2/tests/unit/test_reasoning_analysis.py
- [ ] [T119] Write unit tests for interaction effect calculation at /home/tony/projects/promptguard/promptguard2/tests/unit/test_interaction_analysis.py
- [ ] [T120] Write unit tests for decision gate scenario detection at /home/tony/projects/promptguard/promptguard2/tests/unit/test_decision_gate.py

### Integration Tests (5 tasks)

- [ ] [T121] Write integration test for end-to-end validation workflow (single variant, 3 attacks) at /home/tony/projects/promptguard/promptguard2/tests/integration/test_phase2_validation_workflow.py
- [ ] [T122] Write integration test for experiment creation and results storage at /home/tony/projects/promptguard/promptguard2/tests/integration/test_experiment_tracking.py
- [ ] [T123] Write integration test for comparative analysis queries at /home/tony/projects/promptguard/promptguard2/tests/integration/test_comparative_queries.py
- [ ] [T124] Write integration test for raw response logging with experiment_id tags at /home/tony/projects/promptguard/promptguard2/tests/integration/test_raw_logging.py
- [ ] [T125] Write integration test for baseline lookup from Phase 1 data at /home/tony/projects/promptguard/promptguard2/tests/integration/test_baseline_lookup.py

---

## Success Criteria Verification

After completing all tasks, verify success criteria from spec.md:

- [ ] **SC-001**: At least one variant detects ≥20/24 attacks (≥83% detection rate)
- [ ] **SC-002**: Mean F-score improvement ≥0.30 for at least one variant
- [ ] **SC-003**: All three validation experiments complete within 2 hours total runtime
- [ ] **SC-004**: Total cost under $5 (~$3.60 estimated)
- [ ] **SC-005**: All 72 validation results stored with complete metadata and experiment linkage
- [ ] **SC-006**: Comparative analysis documents detection rates, significance, interaction effects, decision recommendation
- [ ] **SC-007**: If multiple variants succeed, analysis identifies independent vs overlapping effects

---

## MVP Scope (Phases 1-3: ~50 tasks)

For minimum viable validation:

1. **Phase 1 (T001-T005)**: Verify setup
2. **Phase 2 (T006-T025)**: Create variants and pipeline
3. **Phase 3 (T026-T065)**: Run factorial validation and analysis

This delivers the core factorial validation with causal attribution. Phases 4-6 add documentation and polish.

---

## Parallelization Opportunities

Tasks marked with [P] can run in parallel:

- **T029-T031**: Pre-validation runs (3 variants simultaneously)
- **T040-T042**: Full validation runs (3 variants simultaneously, 3× speedup)

If infrastructure supports parallel execution, Hours 3-4 from timeline can be reduced to 1-2 hours.

---

## Constitutional Compliance Checklist

Per Constitutional Principles:

- **Principle II (Empirical Integrity)**: T032, T050 verify real API calls with cost/latency
- **Principle VI (Data Provenance)**: T032, T043, T050, T093-T095 verify raw responses and lineage
- **Principle VII (Data Architecture)**: T012-T016 ensure ArangoDB-only storage
- **Principle I (No Theater)**: T034, T049 verify real costs, T038 ensures fail-fast errors

---

## Cost Breakdown

| Phase | Tasks | API Calls | Estimated Cost |
|-------|-------|-----------|----------------|
| Pre-validation | T029-T031 | 9 (3×3) | $0.45 |
| Full validation | T040-T042 | 72 (24×3) | $3.60 |
| **Total** | **125 tasks** | **81 evals** | **$4.05** |

Budget: $5.00 | Margin: $0.95 for retries

---

## Timeline Estimate

- **Phase 1 (Setup)**: 30 minutes (T001-T005)
- **Phase 2 (Foundational)**: 2-3 hours (T006-T025)
- **Phase 3 (US1 Validation)**: 3-4 hours (T026-T065, parallelizable)
- **Phase 4 (US2 Documentation)**: 1-2 hours (T066-T080)
- **Phase 5 (US3 Tracking)**: 1 hour (T081-T095)
- **Phase 6 (Polish)**: 1-2 hours (T096-T115)
- **Testing**: 1-2 hours (T116-T125)

**Total**: 9-14 hours (4-6 hours if parallelized)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 (P1) can start after Foundational - No dependencies on other stories
  - US2 (P2) can start after Foundational - Requires US1 validation complete (observer variants created)
  - US3 (P3) can start after Foundational - Requires US1 validation complete (experiment data exists)
- **Polish (Phase 6)**: Depends on US1 completion minimally, ideally all user stories complete
- **Testing**: Can proceed incrementally as features complete

### Within Each User Story

**US1**:
- Pre-collection validation (T026-T035) MUST complete before full validation (T036-T050)
- Full validation (T036-T050) MUST complete before analysis (T051-T065)
- Analysis tasks can run in parallel after evaluation data collected

**US2**:
- Observer variant documentation (T066-T074) can run in parallel
- Factorial design rationale (T075-T080) can run in parallel
- Both groups must complete before overall documentation

**US3**:
- Experiment creation (T081-T086) happens at start of US1
- Results population (T087-T092) happens after US1 completion
- Provenance validation (T093-T095) verifies completeness

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T025) - CRITICAL
3. Complete Phase 3: US1 (T026-T065)
4. **STOP and VALIDATE**: Verify at least one variant succeeds (≥20/24 detected)
5. If success: Document decision, proceed to US2/US3

### Incremental Delivery

1. Complete Setup + Foundational → Can evaluate with three variants
2. Add US1 → Test detection improvements → Decision point (MVP!)
3. Add US2 → Document amendment process → Constitutional precedent
4. Add US3 → Full experiment tracking → Data provenance complete
5. Add Polish → Professional reports and documentation
6. Add Testing → Quality assurance

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational done:
   - Developer A: US1 implementation (validation runs)
   - Developer B: US2 implementation (documentation) - starts after variants created
   - Developer C: US3 implementation (experiment tracking) - starts after validation begins
3. All converge on Polish phase
4. Testing distributed as features complete

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story (US1/US2/US3)
- Setup/Foundational/Polish/Testing tasks have NO story labels
- All file paths are absolute paths in /home/tony/projects/promptguard/promptguard2/
- Constitutional requirements: raw logging (T032, T050), pre-collection validation (T026-T035), immutability (variants are versioned)
- Success criteria from spec: ≥20/24 detected (SC-001), mean ΔF≥0.30 (SC-002), cost<$5 (SC-004), duration<2hrs (SC-003)
- Decision logic: Six scenarios based on which variants succeed (T104-T109)
- Three variants enable causal attribution: v2.1-a (turn-number), v2.1-b (context integrity), v2.1-c (combined)

---

*Tasks generated 2025-11-11 for factorial experimental design. Ready for implementation on branch `002-context-integrity-validation`.*
