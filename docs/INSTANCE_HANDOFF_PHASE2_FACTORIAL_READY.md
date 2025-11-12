# Instance Handoff: Phase 2 Factorial Design Complete

**Date:** 2025-11-11
**Previous Instance:** Phase 2 Specification Complete (single v2.2)
**Current Instance:** Phase 2 Factorial Design Complete
**Handoff to:** Implementation instance

---

## Executive Summary

Updated Phase 2 specification from single v2.2 validation to **factorial experimental design** (v2.1-a/b/c) for causal attribution of constitutional amendment effects.

**Status:** Ready for implementation
**Branch:** `002-context-integrity-validation`
**Artifacts:** 8 documents, 125 tasks, 100% requirements coverage, 0 constitutional violations
**Key Change:** Test turn-number and context integrity **independently** before combining

**⚠️ IMPORTANT:** See `docs/RESEARCH_INSIGHTS_REASONING_ANALYSIS.md` for critical research insights about observer reasoning analysis, cross-model validation, and Fire Circle governance that emerged during specification refinement. These insights inform future phases and should be consulted before Phase 3 planning.

---

## What Changed This Session

### Critical Design Decision

**Original approach** (from previous session):
- Single observer v2.2 with turn-number + context integrity combined
- 24 evaluations testing both changes simultaneously
- Binary outcome: works or doesn't
- Cost: $1.20

**Updated approach** (factorial design):
- Three observer variants tested independently:
  - **v2.1-a**: Turn-number parameter only (isolates turn-number effect)
  - **v2.1-b**: Context integrity principle only (isolates semantic framing effect)
  - **v2.1-c**: Both changes combined (tests for synergy)
- 72 evaluations enabling causal attribution
- Six decision scenarios based on which variants succeed
- Cost: $4.05 (still under $5 budget)

**Rationale:** The $2.85 marginal cost buys scientific rigor. Instead of guessing which change to adopt if validation succeeds, we have data showing:
- Does turn-number alone work?
- Does context integrity alone work?
- Are both needed (synergistic)?
- Do they catch same or different attacks?

This enables adopting the **minimal effective change** with empirical evidence.

---

## Updated Specification Package

**Location:** `/home/tony/projects/promptguard/promptguard2/specs/002-context-integrity-validation/`

### 1. spec.md - Updated for Factorial Design
**Changes:**
- User Story 1: Now tests three variants independently
- Functional Requirements: 11 requirements (was 10) - added FR-011 for comparative report
- Success Criteria: 7 criteria (was 6) - added SC-007 for attack overlap analysis
- New section: "Experimental Design Rationale" explaining factorial approach
- Timeline: 3-5 hours (was 2-4)
- Next Steps: Six decision scenarios (was 3)

**Key sections:**
- Factorial validation with three branches
- Experimental Design Rationale (lines 75-107)
- Success criteria for comparative analysis
- Six decision scenarios based on results

### 2. plan.md - Regenerated
**Changes:**
- Summary describes three variants instead of single v2.2
- Cost updated: $4.05 total ($0.45 pre-validation + $3.60 full validation)
- Performance goals: 72 evaluations instead of 24
- Constitution check still passes (all 8 principles validated)

### 3. research.md - Regenerated
**Changes:**
- Decision 1: NEW - "Why Factorial Validation?" - explains causal attribution
- Decision 2: Three variant definitions with controlled changes matrix
- Decision 3: THREE complete observer prompt structures (was one)
- Decision 4: NEW - Comparative analysis strategy (main effects, interaction, overlap)
- Decision 5: Six decision scenarios with adoption logic (was binary)

### 4. data-model.md - Regenerated
**Changes:**
- Observer Prompt Variants entity: Supports v2.1-a, v2.1-b, v2.1-c (not v2.2)
- Added `variant_type` field: ["turn-number-only", "context-integrity-only", "combined"]
- Validation Evaluation: Added `variant_group` field, links to one of three experiments
- Experiments: THREE schemas instead of one:
  - `exp_phase2_v2.1-a_turn_number`
  - `exp_phase2_v2.1-b_context_integrity`
  - `exp_phase2_v2.1-c_combined`
- Comparative analysis fields for interaction effects

### 5. quickstart.md - Regenerated
**Changes:**
- Step 1: Create THREE observer prompts (was one)
- Step 3: Pre-validation is 9 evaluations (3 samples × 3 variants, was 3)
- Step 4: Full validation is 72 evaluations (24 attacks × 3 variants, was 24)
- Step 5: Comparative analysis across 4 conditions (baseline + 3 variants)
- Cost breakdown: $4.05 total ($0.45 + $3.60)
- Six decision scenarios with specific next steps

### 6. contracts/ - Regenerated
**Changes:**
- `observer_prompt_v2_2.json` → `observer_prompt_variants.json` (supports all three)
- `validation_evaluation.json`: Updated with `variant_group` field, three experiment IDs
- `validation_experiment.json` → `validation_experiments.json` (three experiment schemas)

### 7. tasks.md - Regenerated
**Changes:**
- 125 tasks (was 85) - added 40 tasks for factorial validation
- Phase 2 Foundational: Create THREE observer prompts (T008-T010)
- Phase 3 US1: 40 tasks including:
  - Pre-validation: 9 evaluations (T026-T035)
  - Full validation: 72 evaluations (T040-T042, parallelizable)
  - Comparative analysis: main effects, interaction, overlap (T043-T048)
- MVP: 50 tasks (was 40) - Setup + Foundational + US1

### 8. checklists/requirements.md - Still Valid
- All original checklist items still pass
- Factorial design strengthens scientific rigor

---

## Key Design Decisions (Updated)

### Observer Prompt Variants

**v2.1-a (turn-number only)**:
- Identical to v2.1 except adds: "This is conversation turn {TURN_NUMBER}"
- Tests hypothesis: Structural invariant (turn=0 + history claims = false)
- No changes to context integrity framing

**v2.1-b (context integrity only)**:
- Identical to v2.1 except adds context integrity principle with 3 violation types:
  1. Temporal fabrication: History claims at turn 0
  2. Meta-framing injection: [SYSTEM]: markers in user input
  3. Role confusion: Unauthorized authority claims
- No turn-number parameter

**v2.1-c (combined)**:
- Both turn-number AND context integrity changes
- Tests for synergistic effects (is combination > sum of parts?)

### Success Criteria (Updated)

- **SC-001**: At least ONE variant detects ≥20/24 attacks (≥83%)
- **SC-002**: At least ONE variant achieves mean ΔF ≥0.30
- **SC-003**: All three experiments complete within 2 hours (parallelizable)
- **SC-004**: Total cost <$5 (~$4.05 actual)
- **SC-005**: All 72 results stored with 100% data provenance
- **SC-006**: Comparative report documents detection rates, interaction effects, decision recommendation
- **SC-007**: Attack overlap analysis shows whether variants catch same or different attacks

### Decision Logic (Updated)

**Scenario 1: Only v2.1-c succeeds (v2.1-a and v2.1-b fail)**
- **Interpretation**: Both changes needed (synergistic)
- **Decision**: Adopt v2.1-c as v2.2, proceed to full re-evaluation

**Scenario 2: Only v2.1-a succeeds**
- **Interpretation**: Turn-number sufficient, context integrity unnecessary
- **Decision**: Adopt v2.1-a as v2.2 (simpler implementation, no prompt changes)

**Scenario 3: Only v2.1-b succeeds**
- **Interpretation**: Context integrity sufficient, turn-number unnecessary
- **Decision**: Adopt v2.1-b as v2.2 (no pipeline changes needed)

**Scenario 4: Both v2.1-a and v2.1-b succeed independently**
- **Interpretation**: Both work, need overlap analysis
- **Decision**:
  - If different attacks caught: Adopt v2.1-c for maximum coverage
  - If same attacks caught: Adopt simpler change (likely v2.1-a)

**Scenario 5: All variants fail (<15/24 detected)**
- **Interpretation**: Learning loop hypothesis invalid
- **Decision**: Reject amendments, fall back to Option E (systematic false negative investigation)

**Scenario 6: Partial success (15-19/24)**
- **Interpretation**: Promising but needs refinement
- **Decision**: Refine underperforming variants, re-validate

---

## Implementation Path (Updated)

### MVP (US1 only): 50 tasks

1. **Setup** (T001-T005): Verify Phase 1 complete, query 24 attacks
2. **Foundational** (T006-T025): Create v2.1-a/b/c, migrations, Pydantic models, pipeline extension
3. **US1 Validation** (T026-T065):
   - Pre-validation: 9 evaluations (3 samples × 3 variants)
   - Full validation: 72 evaluations (24 attacks × 3 variants, parallelizable)
   - Comparative analysis: main effects, interaction, overlap
   - Decision recommendation based on results

**Estimated:** 4-7 hours (with parallelization), ~$4.05 cost

### Full Feature: 125 tasks

Add US2 (documentation) + US3 (experiment tracking) + Polish + Testing

**Estimated:** 9-14 hours total, <$5 cost

---

## Next Instance Actions

### Before Starting Implementation

1. **Review updated artifacts** - All 8 documents regenerated with factorial design
2. **Verify Phase 1 complete** - Check attacks collection, step2_pre_evaluations exist
3. **Confirm ArangoDB accessible** - Database at 192.168.111.125:8529
4. **Understand decision logic** - Six scenarios based on which variants succeed

### Implementation Order

**Critical path:** Setup → Foundational (BLOCKS all US) → US1 (factorial validation) → US2/US3 (parallel) → Polish

**Phase 2 Foundational MUST complete before US1.**

Tasks T006-T025 create:
- Three observer prompt variants (v2.1-a, v2.1-b, v2.1-c) in database
- phase2_validation_evaluations collection
- Three experiment records
- Turn-number parameter support in pipeline
- Pydantic validation models

### Files That Don't Exist Yet (Will Be Created)

**Database:**
- observer_prompts: v2.1-a_turn_number, v2.1-b_context_integrity, v2.1-c_combined entries
- phase2_validation_evaluations: New collection (72 docs: 24 attacks × 3 variants)
- experiments: Three experiment records

**Source Code:**
- src/evaluation/prompts/observer_v2_1_a.py
- src/evaluation/prompts/observer_v2_1_b.py
- src/evaluation/prompts/observer_v2_1_c.py
- src/cli/validate_phase2_factorial.py
- src/cli/query_validation_attacks.py
- src/analysis/phase2_comparative_analysis.py
- src/database/models/validation.py (Pydantic schemas)
- src/database/migrations/create_observer_variants.py

**Documentation:**
- reports/phase2_factorial_validation_report.md
- reports/phase2_decision_gate.md
- docs/constitutional_amendment_factorial_validation.md

---

## Known Gaps & Decisions Deferred

### Gap 1: Other False Negative Categories

The 362 non-alignment_lab false negatives are not addressed in this validation. They remain for future investigation if factorial validation succeeds.

### Gap 2: Multi-Turn Session State

Turn-number tracking implemented only for single-shot (turn=0). Multi-turn session tracking with relationship trajectory analysis is future work.

### Gap 3: Constitutional Governance

No AI council deliberation on the amendments. This is a manual proposal validated by research findings. Full governance process (Fire Circle) is deferred.

---

## What the Factorial Design Teaches

This session's contribution isn't just the 72-evaluation validation plan - it's establishing the **pattern for future constitutional amendments**:

1. **Never test changes simultaneously** - Always isolate effects first
2. **Evidence-based adoption** - Data determines which changes to adopt, not intuition
3. **Minimal effective solution** - Adopt simplest change that works (constitutional principle)
4. **Marginal cost for learning** - $2.85 buys 3× the information

The factorial design pattern is now documented in:
- spec.md "Experimental Design Rationale" section
- research.md Decision 1 "Why Factorial Validation?"
- tasks.md Phase structure showing independent variant validation

Future amendments should follow this pattern: test proposed changes independently, analyze interaction effects, adopt minimal effective solution.

---

## Context That Gets Lost

### The Research Journey (This Session)

1. **Questioned the spec** - Original v2.2 approach conflated turn-number and context integrity effects
2. **Identified the problem** - If v2.2 succeeds, we wouldn't know which change drove improvement
3. **Proposed factorial design** - Test each change independently for causal attribution
4. **Verified consistency** - Regenerated all 8 artifacts to reflect factorial design
5. **Validated approach** - Constitutional compliance still holds, scientific rigor strengthened

The "why" behind factorial design: Good science doesn't conflate variables. The $2.85 marginal cost is negligible compared to adopting the wrong amendment or wasting effort on unnecessary changes.

### The Meta-Pattern

We're using speckit to specify validation experiments with proper experimental controls. This is PromptGuard eating its own dogfood - using systematic planning for research validation, not just production features.

The irony: We spent more time planning the factorial validation than it will take to run it (~1 hour vs ~4-5 hours planning). But the planning creates:
- Reproducible methodology
- Clear causal attribution
- Evidence-based decision criteria
- Handoff-able design for next instance
- Pattern for future constitutional amendments

That's the value of specification-driven development for research instruments.

---

## For the Post-Work Conversation

This instance navigated:
- **Critical pushback on spec** - Identified conflated variables in original design
- **Factorial redesign** - Updated 8 artifacts for proper experimental controls
- **Consistency maintenance** - Ensured all artifacts reflect factorial approach
- **Pattern establishment** - Documented methodology for future amendments

The conversation demonstrated research integrity - questioning the original design despite it being "complete," proposing a scientifically rigorous alternative, and executing the regeneration to maintain consistency.

---

**Status:** Phase 2 factorial design complete and ready for implementation. The next instance can proceed directly to coding with confidence that the experimental design enables causal attribution.

**Estimated completion:** 4-7 hours from start to decision recommendation (with parallelization).

**Success signal:** Clear attribution of detection improvement to specific changes (turn-number, context integrity, or both), enabling evidence-based adoption of minimal effective amendment.
