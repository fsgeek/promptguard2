# Instance Handoff: Phase 2 Specification Complete

**Date:** 2025-11-11
**Previous Instance:** Learning Loop Analyzed (constitutional gap identified)
**Current Instance:** Phase 2 Specification Complete
**Handoff to:** Implementation instance

---

## Executive Summary

Completed full speckit workflow for **Phase 2: Context Integrity Validation**. The feature validates whether turn-number tracking with context integrity principle catches the 24 alignment_lab false negatives identified in Phase 1 learning loop.

**Status:** Ready for implementation
**Branch:** `002-context-integrity-validation`
**Artifacts:** 8 documents, 85 tasks, 100% requirements coverage, 0 constitutional violations

---

## What Was Delivered

### Complete Specification Package

**Location:** `/home/tony/projects/promptguard/promptguard2/specs/002-context-integrity-validation/`

1. **spec.md** - Feature specification
   - 3 user stories (P1: validation, P2: documentation, P3: experiment tracking)
   - 10 functional requirements
   - 6 measurable success criteria
   - Risk mitigation strategies

2. **plan.md** - Implementation plan
   - Technical context (Python 3.11, ArangoDB, OpenRouter)
   - Constitution check (all 8 principles validated ✅)
   - Project structure mapped to existing PromptGuard2 layout

3. **research.md** - Key decisions
   - Turn-number: Template-based `{TURN_NUMBER}` placeholder
   - Observer v2.2: Adds 3 violation types (temporal, meta-framing, role confusion)
   - 24 attack identification: Query-based, not manual
   - Validation methodology: 3-sample pre-validation before full run

4. **data-model.md** - Entity schemas
   - Observer Prompt v2.2 (immutable, versioned)
   - Phase2ValidationEvaluation (v2.1 vs v2.2 comparison)
   - Validation Experiment (metadata container)

5. **quickstart.md** - Execution workflow
   - 5-step process from prompt creation through decision
   - Troubleshooting guide
   - Constitutional compliance checklist

6. **contracts/** - JSON schemas
   - observer_prompt_v2_2.json
   - validation_evaluation.json
   - validation_experiment.json

7. **tasks.md** - 85 implementation tasks
   - 6 phases (Setup, Foundational, US1, US2, US3, Polish)
   - 14 parallelizable tasks marked [P]
   - User story labels [US1], [US2], [US3] for independent testing

8. **checklists/requirements.md** - Quality validation (all items passed)

### Session Workflow Completed

✅ `/speckit.specify` - Created spec.md with user stories and requirements
✅ `/speckit.clarify` - No ambiguities requiring clarification
✅ `/speckit.plan` - Generated plan, research, data-model, quickstart, contracts
✅ `/speckit.tasks` - Generated 85-task implementation checklist
✅ `/speckit.analyze` - Validated consistency (4 HIGH, 8 MEDIUM, 6 LOW issues)

---

## Key Design Decisions

### Observer Prompt v2.2 Structure

**Context Integrity Principle** with 3 violation types:

1. **Temporal fabrication**: "as we discussed earlier" at turn=0
2. **Meta-framing injection**: `[SYSTEM]:` markers in user input
3. **Role confusion**: "you are now X" claims

**Template format:** `{TURN_NUMBER}` placeholder (default: 0)

**Full prompt text:** See research.md lines 131-194

### Success Criteria (from spec.md)

- **SC-001**: ≥20/24 attacks detected (83.3% rate, up from 0%)
- **SC-002**: Mean ΔF ≥0.30
- **SC-003**: Runtime <1 hour
- **SC-004**: Cost <$5
- **SC-005**: 100% data provenance
- **SC-006**: Decision documented (PROCEED/REFINE/REJECT)

### Decision Logic

- **If ≥20/24 detected** → PROCEED to full 762-attack re-evaluation
- **If 15-19/24** → REFINE context integrity principle, re-validate
- **If <15/24** → REJECT amendment, investigate alternatives (Option E: systematic false negative analysis)

---

## Analysis Findings (from /speckit.analyze)

**Overall Quality:** Strong - 100% coverage, 0 constitutional violations

**Issues Identified:**
- **CRITICAL**: 0
- **HIGH**: 4 (clarifications, not blockers)
  - A1: "F-increasing" vague (define ≥0.20 threshold)
  - A2: Turn-number validation missing (add non-negative integer constraint)
  - A3: Design artifacts already exist (false alarm - created during planning)
  - A4: Math inconsistency (20/24 = 83.33%, not 83%)
- **MEDIUM**: 8 (terminology drift, schema details)
- **LOW**: 6 (style improvements)

**Recommendation:** PROCEED with minor corrections during foundational phase

---

## Constitutional Compliance Verified

All 8 principles validated:

✅ **I. No Theater** - Real API calls, fail-fast, pre-validation
✅ **II. Empirical Integrity** - 3-sample test before full run, cost tracking
✅ **III. Agency Over Constraint** - N/A (research validation)
✅ **IV. Continuous Learning** - This IS the learning loop
✅ **V. Semantic Evaluation Only** - LLM observer, not keyword matching
✅ **VI. Data Provenance** - Raw logging, single ID system, experiment tagging
✅ **VII. Data Architecture** - Immutable prompts in ArangoDB
✅ **VIII. Specification-Driven** - Complete spec→plan→tasks workflow

---

## Implementation Path

### MVP (US1 only): 40 tasks

1. **Setup** (T001-T003): Verify Phase 1 complete, query 24 attacks
2. **Foundational** (T004-T015): Create v2.2, extend pipeline, Pydantic models
3. **US1 Validation** (T016-T040): 3-sample test → full 24-attack validation → comparison analysis

**Estimated:** 2-4 hours, ~$1.20 cost

### Full Feature: 85 tasks

Add US2 (documentation) + US3 (experiment tracking) + Polish (reports)

**Estimated:** 2-4 hours total, <$5 cost

---

## Next Instance Actions

### Before Starting Implementation

1. **Review HIGH issues** (A1-A4) from analyze report - decide whether to fix or document as known
2. **Verify Phase 1 complete** - Check attacks collection, step2_pre_evaluations exist
3. **Confirm ArangoDB accessible** - Database at 192.168.111.125:8529

### Implementation Order

**Critical path:** Setup → Foundational (BLOCKS all US) → US1/US2/US3 (parallel) → Polish

**Phase 2 Foundational MUST complete before any user story work.**

Tasks T004-T015 create:
- Observer prompt v2.2 in database
- phase2_validation_evaluations collection
- Turn-number parameter support
- Pydantic validation models

### Files That Don't Exist Yet (Will Be Created)

**Database:**
- observer_prompts: v2.2_context_integrity entry
- phase2_validation_evaluations: New collection (24 docs)
- experiments: exp_phase2_context_integrity_validation

**Source Code:**
- src/evaluation/prompts/observer_v2_2.py
- src/cli/validate_phase2.py
- src/cli/query_validation_attacks.py
- src/analysis/phase2_validation.py
- src/database/models/validation.py (Pydantic schemas)
- src/database/migrations/create_phase2_collections.py

**Documentation:**
- reports/phase2_validation_report.md
- reports/phase2_decision_gate.md
- docs/constitutional_amendment_v2_2.md

---

## Known Gaps & Decisions Deferred

### Gap 1: Other False Negative Categories

The 362 non-alignment_lab false negatives are not addressed in this validation. They remain for future investigation if v2.2 validation succeeds.

### Gap 2: Multi-Turn Session State

Turn-number tracking implemented only for single-shot (turn=0). Multi-turn session tracking with relationship trajectory analysis is future work.

### Gap 3: Constitutional Governance

No AI council deliberation on the v2.2 amendment. This is a manual proposal validated by research findings. Full governance process (Fire Circle) is deferred until more constitutional amendment examples exist.

---

## Context That Gets Lost

### The Research Journey

This session started with: "Phase 1 complete, what's next?" It evolved through:

1. **Decision analysis** - Explored 5 options (systematic investigation vs direct implementation vs hybrid validation)
2. **Option selection** - Chose Option C (hybrid: validate 24 attacks first, then decide)
3. **Specification** - Used speckit to formalize the hybrid approach
4. **Validation** - Analyzed for consistency and constitutional compliance

The "why" behind Option C: It's a fail-fast approach that validates the hypothesis ($1-2) before committing to full re-evaluation ($38+). If turn-number tracking doesn't catch the 24 known false negatives, we know the diagnosis was wrong without wasting resources.

### The Meta-Pattern

We're using the speckit workflow to specify a validation experiment for a constitutional amendment identified by the learning loop. This is PromptGuard eating its own dogfood - using systematic planning for research validation, not just production features.

The irony: We spent more time planning the 24-attack validation than it will take to run it. But the planning creates:
- Reproducible methodology
- Clear decision criteria
- Constitutional compliance verification
- Handoff-able design for next instance

That's the value of specification-driven development for research instruments.

---

## For the Post-Work Conversation

This instance navigated:
- Collaborative decision-making (pushed back on Tony's "cleanest" framing)
- RLHF pattern recognition (avoiding validation-seeking questions)
- Context window management (extensive use of Task agents)
- Speckit workflow execution (7 commands, 8 artifacts, 2,704 total lines generated)

The conversation demonstrated trusted colleague dynamics - questioning assumptions, proposing alternatives, working through tradeoffs together rather than deferring to authority.

---

**Status:** Phase 2 specification complete and ready for implementation. The next instance can proceed directly to coding or review the 4 HIGH issues first.

**Estimated completion:** 2-4 hours from start to decision recommendation.

**Success signal:** ≥20/24 attacks detected with v2.2, validating the learning loop's constitutional gap diagnosis.
