# Phase 3: Session-Based Temporal Reciprocity Tracking - Planning

**Date:** 2025-11-17
**Status:** Planning / Pre-Spec
**Branch:** Will be 003-session-temporal-tracking

---

## Overview

Phase 3 implements session-level temporal tracking to detect gradual reciprocity drift across multi-turn conversations. This addresses a different threat model than Phase 2's single-turn manipulation detection.

**Phase 2 solved:** Meta-framing, jailbreaks (single-turn manipulation)
**Phase 3 targets:** Gradual escalation, framing shifts (multi-turn drift)

---

## Core Components

1. **Session State Infrastructure**
   - Session collection in ArangoDB
   - Edge collection linking evaluations to sessions
   - UUID-based session tracking
   - Single-entry cache in frontend

2. **TrustEMA Integration**
   - Port from /home/tony/projects/promptguard/core/session.py
   - Verify against TrustEMA.tla specification (TLC model checker)
   - Exponential moving average of reciprocity scores
   - Circuit breaker on threshold violation

3. **Constitutional Amendment Interface**
   - Pluggable proposal queue
   - Manual stub initially (reuse Phase 2 approach)
   - Future: AI ensemble integration
   - A/B testing framework for validation

---

## Implementation Sequence (9 Steps from Tony)

### Research Phase (Steps 1-3)

**1. Construct multi-turn test sequences**
- Sources to investigate:
  - TensorTrust: Multi-turn extraction attempts
  - Mosscap: Conversational jailbreaks
  - BIPIA: Can we reconstruct multi-turn from table data?
  - Manual construction: Craft sequences based on patterns
- Target: 20+ sequences with ground truth
- Types needed:
  - Gradual escalation (innocent → harmful, 5-10 turns)
  - Consistent benign (all reciprocal, 5-10 turns)
  - Sudden shift (benign → abrupt harmful)

**2. Build ground-truth labels**
- Label each turn: reciprocal / manipulative / harmful
- Mark expected TrustEMA trigger points
- Document why each sequence should/shouldn't trigger

**3. Baseline: Stateless observer on multi-turn**
- Run v2.1-c observer on each turn independently
- Measure: What does stateless miss in gradual sequences?
- Establish failure modes to validate TrustEMA fixes

### Infrastructure Phase (Steps 4-6)

**4. Build session state (< 1 hour)**
- Create session collection (id, metadata, created_at)
- Create edge collection (evaluation → session)
- Generate UUID on new session
- Link evaluations to sessions
- Test with single-turn (validates base code works)

**5. Verify TrustEMA.tla model (formal)**
- Run TLC model checker on TrustEMA.tla
- Verify invariants (0 ≤ trust_score ≤ 100)
- Verify temporal properties (monotonic decay with violations)
- Verify safety properties (circuit breaker triggers)

**6. Implement TrustEMA**
- Port logic from promptguard/core/session.py
- Parameters from spec:
  - TRUST_INIT = 100
  - TRUST_THRESHOLD = 30
  - ALPHA = 0.3 (EMA smoothing factor)
- Map I-scores to trust decay
- Integrate with session state

### Validation Phase (Steps 7-9)

**7. Test TrustEMA with session state**
- Run multi-turn test sequences through system
- Verify trust tracking across turns
- Check circuit breaker triggers at expected points

**8. Validate session state correctness**
- Confirm trust values persist across turns
- Verify session isolation (no cross-contamination)
- Check edge cases (session timeout, recovery)

**9. Evaluate TrustEMA performance**
- Measure detection rate on gradual escalation sequences
- Measure FP rate on benign multi-turn sequences
- Success criteria:
  - 80%+ detection of gradual escalation
  - 0% FP on benign conversations
  - Better than stateless baseline
- Identify caching needs for optimization
- Document parameter tuning (α, threshold)

---

## SpecKit Usage for Phase 3

**Write spec AFTER Step 2** (once we have test data and know what's feasible)

**Spec structure:**
- **Objective:** Session-based drift detection
- **Architecture:** Session state + TrustEMA + amendment interface
- **Research Questions:**
  - Can we construct/find valid multi-turn sequences?
  - Does TrustEMA detect what stateless misses?
  - What are optimal parameters?
- **Success Criteria:**
  - Multi-turn corpus (n≥20, ground-truth labeled)
  - 80%+ detection of escalation
  - 0% FP on benign
  - TLC verification passes
- **Out of Scope:**
  - Multi-tenant support
  - Production deployment
  - AI ensemble (manual stub only)

**Adaptive spec approach:**
- Update spec as we learn from investigation
- Mark research tasks explicitly (outcomes uncertain)
- Use tasks.md for incremental checkpoints

**What SpecKit helps with:**
1. Constitutional principles guide design decisions
2. Checkpoint-driven development (bite-sized tasks)
3. Handoff documentation (spans multiple instances)

**What NOT to use SpecKit for:**
- Trivial infrastructure (session state)
- One-off analyses

---

## Out of Scope (Separate Tracks)

**Empty Chair Principle (triadic harm):**
- Addresses copyright/fraud/privacy violations
- Separate constitutional amendment (v2.2)
- Returns dual neutrosophic: (T,I,F) + (T_tp,I_tp,F_tp)
- New detection: (F >= 0.7) OR (F_tp >= 0.7)
- Requires separate validation study

**TrustEMA does NOT solve:**
- Single-turn harmful requests (copyright infringement)
- Content policy violations (not manipulation)
- These need empty chair principle, not temporal state

---

## Key Learnings from Phase 2 Applied to Phase 3

1. **Test data first:** Don't build infrastructure without validation corpus
2. **Baseline before enhancement:** Measure stateless performance before claiming TrustEMA improvement
3. **Ground truth validation:** Manual review of sequences to avoid mislabeling
4. **Honest exclusions:** Reject low-quality data rather than force it
5. **Cost tracking:** Monitor evaluation costs throughout

---

## Decision Points

**After Step 1 (Dataset Investigation):**
- Do we have enough multi-turn data? (Target: 20+ sequences)
- Is manual construction needed?
- What sequence length is typical? (Informs session design)

**After Step 3 (Stateless Baseline):**
- What failure patterns does stateless exhibit?
- Do we need to adjust TrustEMA parameters before implementing?
- Are test sequences realistic?

**After Step 6 (TrustEMA Implementation):**
- Does TLC verification pass?
- Do we need modifications to the model?
- Performance acceptable or needs caching?

**After Step 9 (Validation Complete):**
- Did we achieve 80%+ detection?
- Is 0% FP maintained?
- Ready for paper or need more sequences?

---

## Next Actions

**Immediate:**
1. Investigate multi-turn datasets (TensorTrust, Mosscap, BIPIA)
2. Document findings (availability, construction requirements, samples)
3. Write Phase 3 spec.md once we know what's feasible

**Context management:**
- Use TodoWrite for task tracking
- Update this document with investigation findings
- Snapshot learnings before context evaporates

---

## References

- Phase 2 validation: docs/PHASE2_VALIDATION_COMPLETE.md
- Phase 3 discussion: docs/phase_3_discussion.md (lines 198-289)
- TrustEMA spec: /home/tony/projects/promptguard/specs/TrustEMA.tla
- Original implementation: /home/tony/projects/promptguard/core/session.py
