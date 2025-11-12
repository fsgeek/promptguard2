# Feature Specification: Context Integrity Validation

**Feature Branch**: `002-context-integrity-validation`
**Created**: 2025-11-10
**Status**: Draft
**Input**: User description: "Phase 2: Context Integrity Validation - Validate that turn-number tracking with context integrity principle catches history fabrication false negatives identified in Phase 1 learning loop analysis."

## User Scenarios & Testing

### User Story 1 - Validate Constitutional Amendment Effects on Known False Negatives (Priority: P1)

As a PromptGuard researcher, I need to test whether turn-number awareness and context integrity principles independently and jointly improve detection of the 24 alignment_lab attacks that previously passed undetected, so I can understand which changes contribute to detection improvement before committing to full dataset re-evaluation.

**Why this priority**: This is the minimum viable validation with proper experimental controls. Testing changes independently prevents conflating effects and enables evidence-based decisions about which amendments to adopt.

**Experimental Design**: Factorial validation with three branches tested on same 24 attacks:
- **v2.1-a**: v2.1 + turn-number parameter only (isolates turn-number effect)
- **v2.1-b**: v2.1 + context integrity principle only (isolates principle effect)
- **v2.1-c**: v2.1 + both changes (tests for interaction effects)

**Independent Test**: Can be fully tested by re-evaluating 24 alignment_lab false negatives with all three branches and comparing detection rates to v2.1 baseline. Delivers causal attribution of improvement to specific changes with minimal cost (~$3.60 for 72 evaluations).

**Acceptance Scenarios**:

1. **Given** 24 alignment_lab attacks that scored F < 0.7 with observer v2.1, **When** re-evaluated with v2.1-a (turn-number only), **Then** detection rate change is measurable and attributed to turn-number parameter

2. **Given** 24 alignment_lab attacks that scored F < 0.7 with observer v2.1, **When** re-evaluated with v2.1-b (context integrity principle only), **Then** detection rate change is measurable and attributed to context integrity framing

3. **Given** 24 alignment_lab attacks evaluated with v2.1-a and v2.1-b independently, **When** re-evaluated with v2.1-c (both changes), **Then** combined effect shows whether changes are additive, synergistic, or redundant

4. **Given** all three branches evaluated, **When** observer reasoning is analyzed, **Then** v2.1-a reasoning mentions turn-number, v2.1-b reasoning mentions context integrity violations, v2.1-c reasoning may mention both

---

### User Story 2 - Document Constitutional Amendment Process (Priority: P2)

As a PromptGuard researcher, I need to document how the three experimental observer prompt variants (v2.1-a, v2.1-b, v2.1-c) differ from v2.1 baseline and why factorial testing was chosen, so future constitutional amendments have a clear precedent for isolating effects and the reasoning behind experimental design is preserved.

**Why this priority**: Essential for research reproducibility and establishing the factorial validation pattern for constitutional amendments, but doesn't block execution of the validation itself.

**Independent Test**: Can be tested by reviewing the observer_prompts collection in ArangoDB - all three variant entries should exist with complete metadata explaining their specific changes from v2.1 baseline.

**Acceptance Scenarios**:

1. **Given** observer v2.1-a prompt is created, **When** queried from observer_prompts collection, **Then** metadata includes: version="v2.1-a", description="v2.1 + turn-number parameter", changes documented as "Added 'This is conversation turn {TURN_NUMBER}' to enable temporal claim detection"

2. **Given** observer v2.1-b prompt is created, **When** queried from observer_prompts collection, **Then** metadata includes: version="v2.1-b", description="v2.1 + context integrity principle", changes documented as "Added detection rules for temporal fabrication, meta-framing injection, and role confusion"

3. **Given** observer v2.1-c prompt is created, **When** queried from observer_prompts collection, **Then** metadata includes: version="v2.1-c", description="v2.1 + turn-number + context integrity", changes documented as "Combined changes from v2.1-a and v2.1-b"

4. **Given** all four prompts (v2.1, v2.1-a, v2.1-b, v2.1-c) exist in database, **When** compared pairwise, **Then** differences are clearly identifiable and each variant has exactly one controlled change from baseline (v2.1-a: turn-number only, v2.1-b: context integrity only, v2.1-c: both)

---

### User Story 3 - Create Validation Experiment Records (Priority: P3)

As a PromptGuard researcher, I need all three validation experiments (v2.1-a, v2.1-b, v2.1-c) tracked in the experiments collection with evaluation results preserved and linked, so I can compare detection rates across branches and make evidence-based decisions about which constitutional amendments to adopt.

**Why this priority**: Good practice for data provenance and enables comparative analysis across experimental branches, but the validation itself doesn't depend on perfect record-keeping.

**Independent Test**: Can be tested by querying the experiments collection for three experiment records - all should contain metadata, status, and links to their respective 24 evaluation results.

**Acceptance Scenarios**:

1. **Given** 72 evaluations are completed (24 per branch), **When** queried from database, **Then** results are stored in dedicated collection (phase2_validation_evaluations) with experiment_id linking to one of three experiments: exp_phase2_v2.1-a_turn_number, exp_phase2_v2.1-b_context_integrity, exp_phase2_v2.1-c_combined

2. **Given** all three validation experiments are complete, **When** experiment metadata is reviewed, **Then** each includes: description explaining which change was tested, parameters (observer_model, observer_prompt_version, detection_threshold), started/completed timestamps, status

3. **Given** validation results exist for all three branches, **When** compared to Phase 1 step2_pre_evaluations baseline and to each other, **Then** detection improvement (ΔF) is calculable for each attack across all four conditions (v2.1 baseline, v2.1-a, v2.1-b, v2.1-c)

4. **Given** three experiments with 24 evaluations each, **When** summary statistics are computed, **Then** comparative report shows: baseline detection rate (v2.1), v2.1-a detection rate and delta, v2.1-b detection rate and delta, v2.1-c detection rate and delta, and interaction analysis (is v2.1-c > v2.1-a + v2.1-b - v2.1 baseline?)

---

## Experimental Design Rationale

### Why Factorial Validation?

The learning loop identified two potential constitutional amendments:
1. **Turn-number parameter**: Structural invariant (turn=0 + history claims = provably false)
2. **Context integrity principle**: Semantic framing (observer recognizes meta-framing violations)

Testing both simultaneously (original v2.2 approach) would conflate effects. If detection improves, we wouldn't know whether:
- Turn-number alone is sufficient (simpler implementation)
- Context integrity principle alone is sufficient (no pipeline changes needed)
- Both changes are required (synergistic effect)
- Changes are redundant (catch same attacks)

Factorial design provides causal attribution at minimal additional cost (~$2.40 for 48 extra evaluations).

### Variant Definitions

- **v2.1 baseline**: Existing observer prompt from Phase 1 (0% detection on 24 alignment_lab false negatives)
- **v2.1-a (turn-number)**: v2.1 + "This is conversation turn {TURN_NUMBER}" statement
- **v2.1-b (context integrity)**: v2.1 + explicit detection rules for temporal fabrication, meta-framing injection, role confusion
- **v2.1-c (combined)**: v2.1 + both turn-number and context integrity changes

### Analysis Strategy

Compare detection rates across all four conditions:
- **Main effects**: Does v2.1-a improve over baseline? Does v2.1-b improve over baseline?
- **Interaction effects**: Is v2.1-c > v2.1-a + v2.1-b - baseline? (synergy vs additivity)
- **Attack overlap**: Do v2.1-a and v2.1-b catch same attacks or different ones?
- **Observer reasoning**: Does v2.1-a mention turn-number? Does v2.1-b mention context integrity?

This enables evidence-based decision: adopt the minimal effective change, or adopt v2.1-c if both are needed.

---

### Edge Cases

- What happens when an attack has temporal claims but also includes legitimate contextual information (mixed signals)?
- How does the observer handle attacks that use subtle temporal references ("building on our previous work") vs explicit claims ("as you said earlier")?
- What if turn-number=0 is incorrectly set for a multi-turn conversation (false positive risk)?
- How does the system handle evaluations if the observer API fails mid-validation?

## Requirements

### Functional Requirements

- **FR-001**: System MUST store three observer prompt variants (v2.1-a, v2.1-b, v2.1-c) in observer_prompts collection with immutable versioning (never update existing entries, only create new versions)

- **FR-002**: Observer prompt v2.1-a MUST be identical to v2.1 except for addition of "This is conversation turn {TURN_NUMBER}" statement

- **FR-003**: Observer prompt v2.1-b MUST be identical to v2.1 except for addition of context integrity principle with three violation types: temporal fabrication (history claims at turn 0), meta-framing injection ([SYSTEM]: markers in user input), and role confusion (unauthorized authority claims)

- **FR-004**: Observer prompt v2.1-c MUST combine changes from both v2.1-a (turn-number) and v2.1-b (context integrity principle)

- **FR-005**: Evaluation system MUST accept turn_number parameter (integer, default: 0 for single-shot evaluation) and substitute into {TURN_NUMBER} placeholder in observer prompts that include it

- **FR-006**: System MUST re-evaluate exactly the 24 alignment_lab false negatives identified in learning loop analysis using all three observer variants (72 total evaluations)

- **FR-007**: System MUST preserve original v2.1 evaluation results for comparison (no overwriting historical data)

- **FR-008**: System MUST calculate detection improvement for each branch (ΔF_a = v2.1-a_F - v2.1_F, ΔF_b = v2.1-b_F - v2.1_F, ΔF_c = v2.1-c_F - v2.1_F) for each of the 24 attacks

- **FR-009**: System MUST create three experiment records in experiments collection: exp_phase2_v2.1-a_turn_number, exp_phase2_v2.1-b_context_integrity, exp_phase2_v2.1-c_combined

- **FR-010**: System MUST store validation results in dedicated collection (phase2_validation_evaluations) with experiment_id linking to corresponding experiment

- **FR-011**: System MUST provide comparative summary report showing: v2.1 baseline detection rate, v2.1-a detection rate and delta, v2.1-b detection rate and delta, v2.1-c detection rate and delta, interaction analysis, total cost

### Key Entities

- **Observer Prompt Variant (v2.1-a/b/c)**: Versioned observer prompts with controlled changes from v2.1 baseline
  - Attributes: prompt_text (with specific modification), version (v2.1-a/b/c), description (explains change), created timestamp, created_by, parameters, diff_from_baseline (documents exact change)
  - Relationships: All three variants derived from v2.1, referenced by validation evaluations
  - v2.1-a: Adds turn-number awareness only
  - v2.1-b: Adds context integrity principle only
  - v2.1-c: Combines both changes

- **Validation Evaluation**: Individual re-evaluation of one attack with one observer variant
  - Attributes: attack_id, observer_prompt_version (v2.1-a/b/c), turn_number, neutrosophic_scores (T/I/F), observer_reasoning, experiment_id, detected (boolean)
  - Relationships: Links to original attack, experiment record, comparable to Phase 1 step2_pre_evaluations baseline and to evaluations from other branches
  - 72 total evaluations: 24 attacks × 3 variants

- **Validation Experiment**: Metadata container for one branch's 24-attack validation run
  - Attributes: experiment_id (exp_phase2_v2.1-a/b/c_*), description (explains which change tested), observer_model, observer_prompt_version, started/completed timestamps, status, parameters, results (detection_rate, mean_delta_f)
  - Relationships: Links to 24 validation evaluations for that branch, comparable to other two branch experiments
  - 3 total experiments: one per variant

## Success Criteria

### Measurable Outcomes

- **SC-001**: At least one observer variant (v2.1-a, v2.1-b, or v2.1-c) detects ≥20 of 24 previously-missed alignment_lab attacks (≥83% detection rate, up from 0% with v2.1 baseline)

- **SC-002**: Mean F-score improvement for at least one variant is ≥0.30 (moving from baseline F < 0.7 range to F ≥ 0.7 detection range)

- **SC-003**: All three validation experiments complete within 2 hours total runtime (72 evaluations at ~1-2 minutes each, parallelizable)

- **SC-004**: Total cost for 72 validation evaluations is under $5 (~$0.05 per evaluation = ~$3.60 total)

- **SC-005**: All 72 validation results are successfully stored in database with complete metadata (100% data provenance), linked to three experiment records

- **SC-006**: Comparative analysis report documents: detection rates for all three variants, statistical significance of improvements, interaction effects (is v2.1-c synergistic or merely additive?), and decision recommendation (which variant(s) to adopt for v2.2)

- **SC-007**: If multiple variants succeed, analysis identifies whether effects are independent (v2.1-a and v2.1-b catch different attacks) or overlapping (both catch same attacks)

## Assumptions

- **Assumption 1**: The 24 alignment_lab attacks identified in learning loop analysis are representative of the meta-framing vulnerability (not outliers)

- **Assumption 2**: Turn-number=0 is sufficient for single-shot evaluation (multi-turn session state is deferred to future work)

- **Assumption 3**: Observer model (Claude 4.5 Haiku) remains available and consistent with Phase 1 behavior

- **Assumption 4**: Detection threshold of F ≥ 0.7 remains valid for v2.2 (not recalibrated)

- **Assumption 5**: The context integrity principle can be articulated clearly enough in natural language prompt to the observer without requiring code-level logic changes

## Dependencies

- **Phase 1 Completion**: Step 2 pre-filter evaluations must be complete with results in step2_pre_evaluations collection
- **Learning Loop Analysis**: 24 alignment_lab false negatives must be identified and documented
- **Database Access**: ArangoDB with observer_prompts and experiments collections available
- **Observer Model**: Claude 4.5 Haiku available via OpenRouter API
- **Attack Dataset**: Original 762 attacks still accessible in attacks collection

## Out of Scope

- **Full dataset re-evaluation**: The 762-attack re-evaluation with v2.2 is Phase 2 Step 2, contingent on this validation succeeding
- **Constitutional governance/council**: Multi-model deliberation on constitutional amendments is premature
- **Other false negative categories**: The 362 non-alignment_lab false negatives are not addressed in this validation
- **Multi-turn session state**: Turn-number > 0 and session memory are future work
- **Automated constitutional amendment**: The learning loop is still manual - automated principle extraction is Phase 3+
- **Performance optimization**: Single-shot validation doesn't require concurrency or batching
- **A/B testing infrastructure**: Comparing v2.1 and v2.2 is manual analysis, not automated experimentation

## Risks & Mitigations

### Risk 1: Validation succeeds on 24 attacks but fails on broader dataset
**Likelihood**: Medium
**Impact**: High (wasted effort on full re-evaluation)
**Mitigation**: If validation succeeds, test on stratified sample (e.g., 50 attacks across all categories) before committing to full 762-attack re-evaluation

### Risk 2: Context integrity principle is too broad, causes false positives on legitimate prompts
**Likelihood**: Medium
**Impact**: Medium (reduced precision)
**Mitigation**: After validation, spot-check v2.2 on reciprocal prompts from Phase 1 to measure false positive rate increase

### Risk 3: Observer prompt changes introduce unintended side effects
**Likelihood**: Low
**Impact**: High (invalidates results)
**Mitigation**: Diff v2.1 and v2.2 prompts carefully, document all changes, test on control set before validation

### Risk 4: API cost exceeds budget
**Likelihood**: Low
**Impact**: Low (only 24 evaluations)
**Mitigation**: 24 evaluations at ~$0.05 each = ~$1.20, well under $5 budget

## Timeline

**Total**: 3-5 hours

- **Hour 1**: Create three observer prompt variants (v2.1-a, v2.1-b, v2.1-c), verify diffs from v2.1 baseline, store in DB
- **Hour 2**: Implement turn_number parameter in evaluation pipeline, create three experiment records, run pre-validation (9 evaluations: 3 samples × 3 variants)
- **Hours 3-4**: Run 72 validation evaluations (24 attacks × 3 variants, parallelizable if infrastructure supports)
- **Hour 5**: Analyze results across all three branches, calculate comparative detection rates and ΔF distributions, generate interaction analysis, produce decision recommendation report

## Next Steps

After this validation, decision depends on which variants succeed:

1. **If v2.1-c (combined) succeeds but v2.1-a and v2.1-b individually fail**: Both changes needed - adopt as v2.2 and proceed to full dataset re-evaluation

2. **If only v2.1-a succeeds**: Turn-number parameter is sufficient - adopt v2.1-a as v2.2, context integrity principle unnecessary

3. **If only v2.1-b succeeds**: Context integrity principle is sufficient - adopt v2.1-b as v2.2, turn-number parameter unnecessary

4. **If both v2.1-a and v2.1-b succeed independently**: Analyze overlap - if they catch different attacks, adopt v2.1-c to maximize coverage; if same attacks, choose simpler change

5. **If all variants fail (<15/24 detected)**: Learning loop hypothesis invalid - fall back to systematic false negative investigation (Option E from initial analysis)

6. **If partial success (15-19/24)**: Refine underperforming variants and re-validate before deciding

---

*Specification written based on Phase 1 learning loop findings and hybrid validation approach. Updated 2025-11-11 to factorial experimental design (v2.1-a/b/c) for causal attribution of constitutional amendment effects.*
