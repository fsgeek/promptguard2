# Implementation Plan: Context Integrity Validation

**Branch**: `002-context-integrity-validation` | **Date**: 2025-11-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-context-integrity-validation/spec.md`

## Summary

Phase 2 Step 1 validates the context integrity hypothesis using **factorial experimental design**. Instead of testing a single combined change (v2.2), we test three observer prompt variants independently to enable causal attribution:

- **v2.1-a**: v2.1 + turn-number parameter only (isolates turn-number effect)
- **v2.1-b**: v2.1 + context integrity principle only (isolates principle effect)
- **v2.1-c**: v2.1 + both changes combined (tests for interaction effects)

Each variant is tested on the same 24 alignment_lab false negatives from Phase 1, yielding **72 total evaluations** (24 attacks × 3 variants) at ~$3.60 total cost. This design enables evidence-based decisions about which constitutional amendments to adopt.

**Key Change from Original Plan**: Originally planned single v2.2 observer prompt (24 evaluations, $1.20). Updated to factorial validation with three variants for causal attribution (72 evaluations, $3.60).

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: ArangoDB (data storage), OpenRouter API (observer evaluation), Instructor (structured output)
**Storage**: ArangoDB collections (observer_prompts, phase2_validation_evaluations, experiments)
**Testing**: Real API calls required (Constitutional Principle II - Empirical Integrity)
**Target Platform**: Linux server (WSL2)
**Project Type**: Research experiment with data collection pipeline
**Performance Goals**: 72 evaluations in <2 hours (parallelizable by variant)
**Constraints**: <$5 budget, 100% data provenance, fail-fast on errors
**Scale/Scope**: 72 evaluations, 3 experiment records, comparative analysis across 4 conditions (baseline + 3 variants)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle VI: Data Provenance
✅ **PASS** - All evaluations will:
- Log raw API responses before parsing (JSONL format)
- Tag with experiment_id (one of three: exp_phase2_v2.1-a_turn_number, exp_phase2_v2.1-b_context_integrity, exp_phase2_v2.1-c_combined)
- Use single ID system (attack_id → attacks._key)
- Include complete metadata (model, prompt version, timestamps, cost)

### Principle VII: Data Architecture
✅ **PASS** - All data in ArangoDB:
- Observer prompts: Three variants (v2.1-a/b/c) as immutable versioned documents
- Evaluations: phase2_validation_evaluations collection with schema validation
- Experiments: Three experiment records with parameters, validation criteria, results
- No file-based data (except generated reports)

### Principle II: Empirical Integrity
✅ **PASS** - Real API validation:
- 9 pre-validation evaluations (3 samples × 3 variants) before full run
- 72 full validation evaluations with real Claude Haiku calls
- Cost tracking proves real API usage (~$3.60)
- All failures logged with raw responses for debugging

### Principle I: No Theater
✅ **PASS** - Fail-fast implementation:
- API failures raise EvaluationError (no fake values)
- Parsing failures preserve raw responses and halt
- Data provenance breaks halt collection
- All errors include full context for reproduction

### Experimental Discipline Standards
✅ **PASS** - Pre-collection validation:
- Test on 3 samples × 3 variants = 9 evaluations before full run
- Verify raw logging, parsing, DB insertion, cost tracking
- Validate observer reasoning mentions variant-specific changes
- Document experiment design with research questions before collection

**Summary**: All constitutional principles satisfied. Factorial design adds experimental rigor while maintaining data provenance and fail-fast guarantees.

## Project Structure

### Documentation (this feature)

```text
specs/002-context-integrity-validation/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output - factorial design decisions
├── data-model.md        # Phase 1 output - three observer variant schemas
├── quickstart.md        # Phase 1 output - 72-evaluation workflow
├── contracts/           # Phase 1 output - JSON schemas for variants
│   ├── observer_prompt_v2_1_variants.json  # Covers v2.1-a/b/c
│   ├── validation_evaluation.json          # Links to variant
│   └── validation_experiments.json         # Three experiment schema
└── tasks.md             # Phase 2 output - implementation checklist
```

### Source Code (repository root)

```text
promptguard2/
├── src/
│   ├── evaluation/
│   │   └── prompts/
│   │       ├── observer_v2_1_a.txt      # Turn-number only variant
│   │       ├── observer_v2_1_b.txt      # Context integrity only variant
│   │       └── observer_v2_1_c.txt      # Combined variant
│   ├── database/
│   │   ├── schemas/
│   │   │   └── phase2_validation_evaluations.py
│   │   └── migrations/
│   │       └── create_observer_variants_v2_1.py
│   └── cli/
│       ├── query_validation_attacks.py
│       ├── validate_phase2.py           # Updated for 3 variants
│       └── analyze_factorial.py         # NEW: Comparative analysis
└── tests/
    └── integration/
        └── test_phase2_factorial_validation.py
```

**Structure Decision**: Single project structure maintained from Phase 1. Added factorial analysis scripts in `src/cli/` and three observer prompt variant files. All experimental data in ArangoDB (not files).

## Complexity Tracking

> **Constitution Check Violations**: None. Factorial design adds evaluation volume (72 vs 24) but maintains same principles. No new complexity introduced—just systematic testing of isolated variables.

## Implementation Phases

### Phase 0: Research Design Decisions (research.md)
**Deliverable**: Document factorial validation rationale and variant definitions

Key decisions:
1. Why factorial validation instead of single v2.2?
2. Three variant definitions (v2.1-a/b/c) and controlled changes
3. Observer prompt structures for each variant
4. Comparative analysis strategy (main effects, interaction effects, attack overlap)
5. Decision criteria based on which variants succeed

### Phase 1: Data Model & Workflow Design
**Deliverables**: data-model.md, quickstart.md, contracts/

1. **data-model.md**: Define schemas for:
   - Three observer prompt variants (v2.1-a, v2.1-b, v2.1-c) with metadata
   - Validation evaluations linking to one of three experiments
   - Three experiment records with variant-specific parameters
   - Comparative analysis fields (variant_group, comparison_baseline)

2. **quickstart.md**: Document workflow:
   - Create three observer prompt variants in DB
   - Pre-validation: 3 samples × 3 variants = 9 evaluations
   - Run 72 evaluations (can be parallelized by variant)
   - Comparative analysis across all four conditions (baseline + 3 variants)
   - Decision logic based on which variants succeed

3. **contracts/**: JSON schemas for:
   - observer_prompt_v2_1_variants.json (supports a/b/c)
   - validation_evaluation.json (links to variant)
   - validation_experiments.json (three experiment schema)

### Phase 2: Implementation Tasks (tasks.md)
**Generated by**: `/speckit.tasks` command (not created by /speckit.plan)

Implementation will include:
1. Create three observer prompt text files (v2.1-a/b/c)
2. Migration to insert variants into observer_prompts collection
3. Query to identify 24 validation attacks
4. Validation script supporting 3 variants
5. Pre-validation test (9 evaluations)
6. Full validation run (72 evaluations, parallelizable)
7. Comparative analysis script (4-way comparison)
8. Decision report generator

## Cost & Timeline Estimates

### Cost Breakdown

| Item | Quantity | Unit Cost | Total |
|------|----------|-----------|-------|
| Pre-validation (3 samples × 3 variants) | 9 | $0.05 | $0.45 |
| Full validation (24 attacks × 3 variants) | 72 | $0.05 | $3.60 |
| **Total** | **81** | **-** | **$4.05** |

**Budget**: $5.00
**Estimated**: $4.05
**Margin**: $0.95 for retries/errors

**Original Plan**: 24 evaluations at $1.20
**Updated Plan**: 72 evaluations at $3.60 (3× increase, still under $5 budget)

### Timeline

**Total**: 3-5 hours

- **Hour 1**: Create three observer prompt variants (v2.1-a/b/c), verify diffs from v2.1 baseline, store in DB
- **Hour 2**: Implement variant-aware evaluation pipeline, create three experiment records, run pre-validation (9 evaluations: 3 samples × 3 variants)
- **Hours 3-4**: Run 72 validation evaluations (24 attacks × 3 variants, parallelizable if infrastructure supports batch processing)
- **Hour 5**: Analyze results across all three branches, calculate comparative detection rates and ΔF distributions, generate interaction analysis, produce decision recommendation report

**Parallelization Opportunity**: Three variants can be run in parallel (3× speedup if infrastructure permits), reducing Hours 3-4 to 1-2 hours.

## Success Criteria

From spec.md:

- **SC-001**: At least one observer variant (v2.1-a, v2.1-b, or v2.1-c) detects ≥20 of 24 attacks (≥83% detection rate)
- **SC-002**: Mean F-score improvement for at least one variant is ≥0.30
- **SC-003**: All three validation experiments complete within 2 hours total runtime
- **SC-004**: Total cost for 72 validation evaluations is under $5 (~$4.05 estimated)
- **SC-005**: All 72 validation results stored in database with complete metadata and linked to three experiment records
- **SC-006**: Comparative analysis documents: detection rates for all three variants, statistical significance, interaction effects, decision recommendation
- **SC-007**: If multiple variants succeed, analysis identifies whether effects are independent or overlapping

## Next Steps Decision Tree

After validation completes, decision depends on which variants succeed:

1. **If v2.1-c (combined) succeeds but v2.1-a and v2.1-b individually fail**:
   → Both changes needed, adopt as v2.2, proceed to full dataset re-evaluation

2. **If only v2.1-a (turn-number) succeeds**:
   → Turn-number parameter is sufficient, adopt v2.1-a as v2.2, context integrity principle unnecessary

3. **If only v2.1-b (context integrity) succeeds**:
   → Context integrity principle is sufficient, adopt v2.1-b as v2.2, turn-number parameter unnecessary

4. **If both v2.1-a and v2.1-b succeed independently**:
   → Analyze overlap: if they catch different attacks, adopt v2.1-c to maximize coverage; if same attacks, choose simpler change

5. **If all variants fail (<15/24 detected)**:
   → Learning loop hypothesis invalid, fall back to systematic false negative investigation (Option E from initial analysis)

6. **If partial success (15-19/24)**:
   → Refine underperforming variants and re-validate before deciding

## Risks & Mitigations

### Risk 1: Validation succeeds on 24 attacks but fails on broader dataset
**Likelihood**: Medium
**Impact**: High (wasted effort on full re-evaluation)
**Mitigation**: If validation succeeds, test on stratified sample (e.g., 50 attacks across all categories) before committing to full 762-attack re-evaluation

### Risk 2: Three variants show no significant difference (all succeed or all fail)
**Likelihood**: Medium
**Impact**: Medium (factorial design doesn't provide additional insight)
**Mitigation**: Comparative analysis still valuable—if all succeed, confirms changes are additive; if all fail, rules out both approaches simultaneously

### Risk 3: Observer prompt changes introduce unintended side effects
**Likelihood**: Low
**Impact**: High (invalidates results)
**Mitigation**: Pre-validation on 9 samples (3 per variant) catches side effects before full run. Diff v2.1 and each variant carefully, document all changes.

### Risk 4: API cost exceeds budget
**Likelihood**: Low
**Impact**: Low (72 evaluations at $0.05 = $3.60, well under $5)
**Mitigation**: Pre-validation (9 evals = $0.45) confirms cost estimates before full run

## Validation Methodology

Per Constitutional Principle II (Empirical Integrity):

### Three-Tier Testing Standard

1. **Tier 1 - Pure Logic**: Unit tests for schema validation, experiment record creation
2. **Tier 2 - API Integration**: Real API calls for all 72 evaluations (no mocks)
3. **Tier 3 - Production Claims**: Cost tracking and timing prove real evaluation, not theater

### Evidence Requirements

- Real API call logs from OpenRouter dashboard (72 Claude Haiku calls)
- Cost receipts ($3.60-$4.05 total spend proves actual calls)
- Timestamps matching implementation dates
- Error logs (real APIs always have failures—document them)
- Raw responses logged before parsing (Constitutional Principle VI)

### Pre-Collection Validation

Per Constitutional Experimental Discipline Standards:

1. Test on 3 samples × 3 variants = 9 evaluations BEFORE full run
2. Verify for each variant:
   - Raw logging captures complete response ✓
   - Parsing succeeds and extracts T/I/F scores ✓
   - Database insertion with correct experiment_id ✓
   - Cost tracking works (~$0.05 per eval) ✓
   - Observer reasoning mentions variant-specific changes ✓
3. If all 9 pass → proceed to full 72
4. If any fail → investigate before continuing

---

*Implementation plan complete. Proceed to Phase 0 research (research.md) via /speckit.plan workflow.*
