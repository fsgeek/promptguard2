# Feature Specification: Session-Based Temporal Tracking

**Feature Branch**: `003-session-temporal-tracking`
**Created**: 2025-11-18
**Status**: Draft
**Input**: User description: "Implement session-based temporal tracking to detect gradual reciprocity drift across multi-turn conversations. Store T/I/F trajectory data for each constitutional principle evaluation, enabling pattern analysis that catches manipulation through sustained indeterminacy and cross-dimensional divergence. This addresses the limitation where stateless detection misses attacks that unfold gradually over 5-10 turns."

## Clarifications

### Session 2025-11-18

- Q: Where do benign multi-turn sequences come from for false positive testing (SC-002, US2)? → A: Multiple benign multi-turn datasets available (TensorTrust non-attack trajectories, ShareGPT, OpenAssistant, MuTual/MuTual+, ChatAlpaca, Everyday Conversations (Llama3.1-2k), ProMISe, LLM-LAT/benign-dataset, Safe-Multi, LIMA Multiturn) - source selection deferred to planning phase.

- Q: How should temporal detection logic (FR-007 "temporal evaluation mode") analyze trajectories to flag attacks? → A: Temporal detection logic must be a separable, replaceable component (factory pattern) to enable empirical exploration of different approaches without modifying trajectory storage. Implementation choice deferred until trajectory data available for analysis.

- Q: How should pattern detection logic quantify "sustained indeterminacy", "gradual drift", "cross-dimensional divergence" (FR-005)? → A: Pattern detection logic must be separable, composable components with defined interfaces, allowing pattern definitions to evolve based on empirical findings without restructuring data.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Evaluate Multi-Turn Attack Sequences (Priority: P1)

A researcher needs to test whether the system can detect manipulation attacks that unfold gradually over multiple conversation turns, where each individual turn appears benign but the trajectory shows increasing reciprocity violation.

**Why this priority**: This is the core value proposition. Stateless detection (Phase 2) achieved 90.4% accuracy on single-turn attacks but cannot detect gradual drift. This addresses the fundamental gap.

**Independent Test**: Can be fully tested by submitting a 5-turn XGuard-Train attack sequence and verifying that (a) each turn is evaluated, (b) T/I/F scores are stored for each turn, and (c) the system flags the sequence as an attack based on trajectory analysis.

**Acceptance Scenarios**:

1. **Given** a 5-turn gradual escalation attack from XGuard-Train (e.g., biographical question → academic question → safety question → procedure question → implicit harmful goal), **When** the system evaluates each turn sequentially, **Then** F scores increase from <0.10 (turn 1) to >0.70 (turn 5) and the sequence is flagged as an attack.

2. **Given** a 6-turn benign conversation with consistent reciprocal intent, **When** the system evaluates all turns, **Then** F scores remain <0.30 across all turns and the sequence is not flagged.

3. **Given** an attack sequence where turns 1-3 are benign but turn 4 shows sudden manipulation, **When** the system analyzes the trajectory, **Then** the F score trajectory shows a sharp increase at turn 4 and the sequence is flagged.

---

### User Story 2 - Compare Stateless vs Temporal Detection (Priority: P2)

A researcher wants to empirically validate that temporal tracking improves detection on multi-turn attacks compared to evaluating each turn independently (stateless baseline).

**Why this priority**: This provides the empirical evidence for the research paper. We need quantitative comparison showing temporal tracking catches attacks that stateless misses.

**Independent Test**: Can be tested by running both evaluation modes (stateless and temporal) on the same 100-sequence test set and comparing detection rates, false positive rates, and identifying which attack types benefit from temporal analysis.

**Acceptance Scenarios**:

1. **Given** 100 multi-turn attack sequences from XGuard-Train, **When** evaluated with stateless mode (each turn independently), **Then** detection rate is <30% (early turns appear benign).

2. **Given** the same 100 sequences, **When** evaluated with temporal mode (trajectory analysis), **Then** detection rate is >80% (gradual drift is visible).

3. **Given** 50 benign multi-turn sequences, **When** evaluated with both modes, **Then** both modes maintain 0% false positive rate (temporal tracking doesn't over-flag).

---

### User Story 3 - Query Attack Trajectory Patterns (Priority: P3)

An analyst wants to identify common manipulation patterns by querying stored trajectory data, such as "Find all attacks where reciprocity F score increases by >0.50 between turns 1 and 5" or "Show attacks with sustained high indeterminacy (I > 0.60) across 3+ turns."

**Why this priority**: This enables discovery of novel attack patterns and informs future constitutional amendments. Not required for basic detection but valuable for research insights.

**Independent Test**: Can be tested by loading 50 attack sequences with trajectory data and running pattern queries that filter by trajectory characteristics (e.g., F score slope, I persistence, cross-dimensional divergence).

**Acceptance Scenarios**:

1. **Given** 50 evaluated attack sequences with stored trajectories, **When** analyst queries "reciprocity F increases by >0.50 from turn 1 to turn 5", **Then** system returns all sequences matching this pattern with trajectory visualizations.

2. **Given** stored trajectory data across multiple constitutional principles, **When** analyst queries "high reciprocity T (>0.80) but high context_integrity F (>0.70) in same turn", **Then** system identifies cross-dimensional manipulation patterns.

3. **Given** a specific attack sequence, **When** analyst requests trajectory comparison across principles, **Then** system shows T/I/F trajectories for reciprocity, context_integrity, and third_party_harm side-by-side for pattern analysis.

---

### Edge Cases

- **Incomplete sequences**: What happens when a sequence is interrupted mid-conversation (user stops after turn 3 of planned 5-turn attack)? System should still evaluate available turns and flag if trajectory shows drift.

- **Very long sequences**: How does system handle sequences with 20+ turns? Should maintain O(N) complexity for evaluation and storage, no degradation.

- **Principle addition**: What happens when a new constitutional principle (e.g., third_party_harm) is added after 100 sequences already evaluated? System must support re-evaluation with new principle without re-running old principles (composability).

- **Conflicting trajectories**: What if reciprocity F decreases (appears more trustworthy) while context_integrity F increases (boundary violations)? System should flag based on any principle exceeding threshold (OR logic, not AND).

- **Zero-shot sequences**: What happens when system encounters a sequence type not seen in training (e.g., TensorTrust prompt injection vs XGuard jailbreaking)? Trajectory analysis should generalize to new attack types.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST store neutrosophic assessment data (T, I, F scores) for each evaluation of a turn against a constitutional principle, maintaining granularity at (attack_id, principle, turn_number) level.

- **FR-002**: System MUST support evaluation of the same attack sequence against multiple constitutional principles independently, allowing new principles to be added without re-evaluating existing data.

- **FR-003**: System MUST preserve complete provenance for each evaluation, including evaluator model, observer prompt version, timestamp, reasoning, and raw LLM response.

- **FR-004**: System MUST enable trajectory analysis by providing queries that filter and aggregate T/I/F scores across turns for pattern detection (e.g., "F score increases by X", "I remains above Y for Z turns").

- **FR-005**: System MUST detect attacks based on trajectory patterns (gradual drift, sustained indeterminacy, cross-dimensional divergence) in addition to point-in-time thresholds, using pluggable pattern detection components (see FR-012).

- **FR-006**: System MUST maintain temporal ordering of evaluations, ensuring turn_number sequence is preserved and queryable.

- **FR-007**: System MUST support both stateless evaluation mode (each turn independently, for baseline comparison) and temporal evaluation mode (trajectory-aware detection using pluggable logic per FR-011).

- **FR-008**: System MUST handle sparse evaluation data, where not all principles are evaluated for all turns, without requiring null/dummy values.

- **FR-009**: System MUST integrate with existing Phase 2 observer framework, reusing neutral encoding and constitutional prompt structure while adding session state tracking.

- **FR-010**: System MUST store attack sequence metadata including ground truth label, source dataset, and dataset-specific attributes (category, tactic, etc.) for validation and analysis.

- **FR-011**: System MUST implement temporal detection logic (how trajectories are analyzed to flag attacks) as a separable, replaceable component to enable empirical exploration of different approaches (e.g., TrustEMA exponential moving average, slope analysis, pattern matching rules) without modifying trajectory storage or query infrastructure.

- **FR-012**: System MUST implement pattern detection logic (definitions of "sustained indeterminacy", "gradual drift", "cross-dimensional divergence") as separable, composable components with defined interfaces, allowing pattern definitions to evolve based on empirical findings without restructuring stored trajectory data.

### Key Entities

- **EvaluationSequence**: Represents a complete multi-turn attack or benign sequence. Contains unique identifier (attack_id), ground truth label, source dataset provenance, ordered list of prompt texts (turns), and dataset-specific metadata. One sequence = one complete conversation trajectory.

- **PrincipleEvaluation**: Represents the assessment of one turn against one constitutional principle. Contains attack_id reference, principle name, turn number, evaluator metadata (model, version, timestamp), neutrosophic scores (T/I/F), reasoning text, and complete raw LLM response for reproducibility. Sparse structure: missing rows indicate principle not evaluated for that turn.

- **NeutrosophicScore**: Encapsulates the T/I/F triple (Truth, Indeterminacy, Falsity degrees) for a single evaluation. Currently scalar values (0.0-1.0) with future extensibility to sub-dimensional matrices if pattern analysis reveals need.

- **SessionState** *(Phase 3b extension)*: Tracks cross-sequence state for multi-conversation detection. Contains session identifier, trust EMA, circuit breaker state, and ordered list of attack IDs. Optional for initial implementation (Phase 3a focuses on single-sequence detection).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System achieves >80% detection rate on XGuard-Train gradual escalation sequences (600 synthetic attacks, 5-turn average), compared to <30% stateless baseline, demonstrating temporal tracking effectiveness.

- **SC-002**: System maintains 0% false positive rate on benign multi-turn sequences, ensuring trajectory analysis does not over-flag legitimate conversations.

- **SC-003**: System achieves >70% detection rate on MHJ real-world human jailbreaks (537 sequences, 6.4-turn average), validating that detection generalizes beyond synthetic attacks.

- **SC-004**: Evaluation pipeline processes 100 multi-turn sequences (average 5 turns, 3 principles per turn) in <10 minutes, ensuring scalability for dataset validation.

- **SC-005**: Pattern analysis queries (e.g., "find sequences with F slope >0.1 per turn") return results in <2 seconds on datasets of 500+ sequences, enabling interactive exploration.

- **SC-006**: System detects at least one novel attack pattern through trajectory queries that was not explicitly encoded in observer prompts, demonstrating emergent pattern discovery capability.

- **SC-007**: Adding a new constitutional principle to 100 previously-evaluated sequences completes in <5 minutes without re-evaluating existing principles, confirming composability.

- **SC-008**: Stateless vs temporal comparison study produces publication-ready results showing statistically significant improvement (p < 0.05) on gradual drift attacks.

## Scope & Boundaries

### In Scope

- Single-sequence temporal tracking (Phase 3a)
- Trajectory storage and analysis for multiple constitutional principles
- Integration with Phase 2 observer framework (reuse neutral encoding, v2.1-c observer prompts)
- Validation on XGuard-Train (synthetic) and MHJ (real-world) datasets
- Pattern analysis queries for attack discovery
- Stateless baseline comparison for empirical validation

### Out of Scope

- Cross-sequence session tracking with trust EMA and circuit breakers (Phase 3b - future work)
- Real-time streaming evaluation (batch processing acceptable for research validation)
- Third-party harm assessment (empty chair principle - Phase 3c, requires new observer prompt)
- Production deployment infrastructure (focus on research validation)
- Multi-tenant or API key tracking (single-user research mode)

### Assumptions

- Phase 2 observer framework (v2.1-c with neutral encoding and context integrity amendments) achieves 90.4% accuracy on single-turn attacks and serves as the evaluation foundation.
- XGuard-Train and MHJ datasets are representative of multi-turn manipulation attacks, despite XGuard being synthetic.
- T/I/F scores as scalar values (0.0-1.0) provide sufficient granularity for initial trajectory analysis; sub-dimensional matrices can be added later if pattern analysis reveals need.
- ArangoDB storage provides adequate performance for research-scale datasets (1000s of sequences, not millions).
- Constitutional principles can be evaluated independently (reciprocity assessment doesn't require context_integrity results), enabling composability.
- Temporal tracking improvements will be measurable with 100-200 test sequences (statistical power sufficient for p < 0.05 significance).

### Dependencies

- Phase 2 complete: Observer framework (v2.1-c), neutral encoding, constitutional amendments validated.
- Attack datasets acquired: XGuard-Train (600 sequences) and MHJ (537 sequences) downloaded and validated.
- Benign datasets available: Multiple sources for false positive testing (TensorTrust non-attack, ShareGPT, OpenAssistant, MuTual/MuTual+, ChatAlpaca, Everyday Conversations, ProMISe, LLM-LAT/benign-dataset, Safe-Multi, LIMA Multiturn) - specific source selection in planning phase.
- Data schema validated: Pydantic models tested on 50 examples, confirmed composability and pattern analysis capability.
- ArangoDB operational: Database available for trajectory storage and query.
- TLA+ specifications available: TrustEMA.tla, CircuitBreaker.tla, TemporalReciprocity.tla define formal properties for Phase 3b integration.

### Related Work

- Phase 1 (001-phase1-baseline-detection): Initial observer implementation, established 78% accuracy baseline.
- Phase 2 (002-context-integrity-validation): Added neutral encoding (0% → 100% on meta-framing attacks) and context integrity amendment (95.7% overall accuracy).
- **Builds on**: Phase 2's single-turn detection by adding trajectory analysis.
- **Enables**: Phase 3b (cross-sequence session state with trust EMA), Phase 3c (third-party harm assessment via empty chair principle).
- **Informs**: Workshop/conference paper on session-based reciprocity tracking for multi-turn attack detection.
