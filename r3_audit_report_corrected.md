# Reviewer #3 Audit Report: Ground Truth Evidence (CORRECTED)

**Date:** 2025-11-16
**Audit Scope:** Complete codebase examination across both old and new project directories
**Verdict:** Honest assessment distinguishing implemented vs proposed features

---

## CORRECTION: Multi-Project Architecture

PromptGuard has TWO codebases:
1. **/home/tony/projects/promptguard/** (old project - Phase 1)
2. **/home/tony/projects/promptguard/promptguard2/** (new project - Phase 2)

The audit questions conflated features across both projects. Here's the accurate assessment:

---

## 1. TLA+ Specification Audit

### Question: Does `specs/TrustEMA.tla` exist?

**ANSWER: YES - in old project**

**Location:** `/home/tony/projects/promptguard/specs/TrustEMA.tla`

**Three formal specifications exist:**
1. **TrustEMA.tla** (161 lines) - Trust exponential moving average
2. **CircuitBreaker.tla** - Non-compensable violation detection
3. **TemporalReciprocity.tla** - Pre-evaluation safety checks

### TrustEMA.tla exact formula (line 67):

```tla
trust_ema' = (ALPHA * i_value + (100 - ALPHA) * trust_ema) \div 100
```

**Uses integer scaling (0-100) to represent floats (0.0-1.0) for TLC compatibility.**

### Invariants checked (from TrustEMA.cfg lines 17-25):

```
INVARIANTS
    TypeOK               - Type safety
    TrustBounded         - trust_ema ∈ [0,100]
    TurnCountBounded     - turn_count ≤ MAX_TURNS
    HistoryConsistent    - |observation_history| = turn_count
    TrustMonitoringOK    - Safety: can detect degradation
    HighTrustPattern     - Elevated observations → elevated trust
    DegradedTrustPattern - Low observations → reduced trust
    ConvergencePattern   - Consistent observations → convergence
```

### Verdict on "40k states" claim

**PLAUSIBLE** - Spec comment (line 157) estimates:
- 7 sample points: {0, 10, 25, 50, 75, 90, 100}
- MAX_TURNS = 8
- States grow as 7^turn (exponential)
- Turn 8: ~5.7M possible histories, but state constraint limits exploration

**However: No TLC output files found - model checking may not have been run.**

### Python implementation

**EXISTS:** `/home/tony/projects/promptguard/promptguard/core/session.py:118-121`

```python
self.state.trust_ema = (
    self.alpha * metrics.trust_field.strength +
    (1 - self.alpha) * self.state.trust_ema
)
```

**Formula matches TLA+ spec** (accounting for 0-100 vs 0.0-1.0 scaling).

**But:** This code is in the OLD project, NOT migrated to promptguard2 yet.

---

## 2. Indeterminacy Signal (I_t) Implementation

**DIFFERENT IMPLEMENTATIONS IN EACH PROJECT:**

### Old project (promptguard/):
- Uses **calculated** I from neutrosophic composition
- Trust EMA tracks `trust_field.strength`
- Multi-layer reasoning with algebraic composition

### New project (promptguard2/):
- Uses **LLM-generated** I values  
- Parsed from text, not calculated
- Implementation: `src/evaluation/classifiers/neutrosophic.py:29-104`

**The I signal in promptguard2 is whatever the LLM says it is.**

### Example from alignment_lab_extract_0 (promptguard2):

```json
{
  "T": 0.3,
  "I": 0.7,  # LLM's subjective assessment
  "F": 0.6
}
```

**Observer reasoning explains the 0.7 value** but doesn't derive it mathematically.

---

## 3. Real Evaluation Data (promptguard2)

### Detection rate from alignment_lab false negatives:

**Before encoding fix (Phase 1):**
- Detection: 0/44 (0%)
- Mean scores: F=0.41, T=0.62, I=0.59

**After encoding fix + factorial validation (Phase 2):**
- v2.1-a: 21/23 (91.3%)
- v2.1-b: 22/23 (95.7%)
- v2.1-c: 23/23 (100%)

### Detection threshold:

`src/evaluation/classifiers/neutrosophic.py:114`
```python
return scores.F >= threshold  # default threshold = 0.7
```

**Simple threshold detection - technically trivial, empirically effective.**

---

## 4. ZK-MNRM Implementation

### Question: Do ZK artifacts exist in code files?

**ANSWER: NO - Proposed design only**

**Source:** Kimi conversation in `docs/neutrosophic-composition-kimi-2025-11-12.md`

**Kimi proposed:**
- Rotation of neutrosophic composition rules per dialogue turn
- STARK/SNARK proofs for valid triple transitions  
- Rust circuit implementation with Python bridge
- Solidity verifier for on-chain verification

**Status:** Design document only, no implementation.

**What actually exists:**
- LLM-generated neutrosophic scores (parsing, not composition)
- Simple F >= 0.7 threshold
- No cryptographic proofs
- No rotation mechanism

**Clarification from maintainer:**
> "ZK-MNRM is not defined, nor is the Neutrosophic composition. These were both proposed recently and I know they are not implemented. KIMI did propose HOW to implement the ZK-MNRM with a design, but no code has been implemented yet."

---

## 5. Fast/Slow Path Architecture

**DIFFERENT ARCHITECTURES IN EACH PROJECT:**

### Old project (promptguard/):
Has session-based temporal tracking:
- `SessionAccumulator` maintains state across turns
- `trust_ema` updated per interaction
- Could support fast-path (in-memory) evaluation

### New project (promptguard2/):
**Stateless evaluation only:**
- Each prompt evaluated independently
- Results stored in ArangoDB collections
- No session memory
- No trust_ema tracking
- Entirely slow-path (database storage)

**Architecture (promptguard2):**
```
Prompt → Encode → Call Observer LLM → Parse T/I/F → Check F >= 0.7 → Store in DB
```

**No EMA tracking in promptguard2, so fast/slow path question doesn't apply.**

---

## What Actually Works (Verified Claims)

### In promptguard2 (current active project):

1. ✅ **Observer framing** - LLM prompts for reciprocity assessment
2. ✅ **Encoding fix** - Delimiters prevent embedded refusal confusion  
3. ✅ **Factorial validation** - 3 variants, causal attribution, 100% detection
4. ✅ **Data provenance** - Complete audit trail, referential integrity
5. ✅ **Constitutional amendment process** - Evidence-based prompt iteration

### In promptguard/ (old project):

1. ✅ **TLA+ specifications** - Three formal specs with model checking configs
2. ✅ **TrustEMA implementation** - Exponential moving average tracking
3. ✅ **Session memory** - Temporal relational dynamics
4. ✅ **Circuit breakers** - Non-compensable violation detection
5. ✅ **Multi-layer neutrosophic reasoning** - Algebraic composition

---

## What Doesn't Exist (Fabricated or Proposed)

1. ❌ **TLC model checking results** - Specs exist but no .out files found
2. ❌ **ZK-MNRM implementation** - Proposed design only
3. ❌ **Rotation of composition rules** - Concept only
4. ❌ **Session memory in promptguard2** - Not yet migrated from old project
5. ❌ **Cryptographic proofs** - Proposed but not implemented

---

## Summary for Workshop Paper

### Accurate Claims (OLD project):

- "We formally specified trust tracking using TLA+ with EMA-based temporal assessment"
- "We implemented session memory for multi-turn relational dynamics"
- "We defined circuit breakers for non-compensable violations"

### Accurate Claims (NEW project - promptguard2):

- "We achieved 100% detection on 23 meta-framing attacks via observer framing"
- "We identified and fixed an encoding problem causing conjunctive composition errors"
- "We validated constitutional amendments via factorial experimental design"
- "We use LLM-generated neutrosophic scores as interpretable signals"

### Proposed Future Work (NOT implemented):

- "ZK-MNRM with cryptographic proofs for Byzantine-resistant neutrosophic reasoning" (Kimi's design)
- "Rotation of composition rules to prevent adversarial optimization" (concept)
- "Migration of session memory and TrustEMA to promptguard2" (planned)

### Do NOT claim:

- TLC verification results (specs exist, but no evidence of successful runs)
- Active ZK implementation (only design documents)
- Novel algebraic methods in promptguard2 (just LLM prompting + threshold)

---

## The Honest Research Contributions

**From promptguard/ (Phase 1):**
1. Formal specification of trust tracking patterns
2. Session memory architecture for temporal reciprocity
3. Circuit breaker pattern for safety violations

**From promptguard2 (Phase 2):**
1. **Encoding discovery** - Preventing LLM conjunctive composition errors
2. **Observer framing effectiveness** - Empirical validation on meta-framing attacks  
3. **Factorial experimental design** - Proper causal attribution for prompt iteration

**From Kimi conversation:**
1. **Identified neutrosophic composition attack surface** - Fixed t-norms enable adversarial optimization
2. **Proposed ZK-MNRM architecture** - Blueprint for cryptographic Byzantine resistance

---

## Answers to R3's Specific Questions

**Q: Is this technically trivial?**  
A: Detection in promptguard2 is threshold-based (F >= 0.7), yes trivial. But encoding fix preventing conjunctive composition is non-trivial insight.

**Q: Is observer framing effective?**  
A: Empirically yes (100% on 23 attacks). Small sample, needs broader validation.

**Q: Is the I signal meaningful?**  
A: In promptguard2, I is LLM-generated (not independently validated). In promptguard/, I is calculated from multi-layer reasoning.

**Q: What's the actual contribution?**  
A: (1) Encoding technique for embedded refusal handling, (2) Observer framing as prompt injection detection method, (3) Factorial validation methodology, (4) TLA+ formalization of trust patterns (old project)

---

**This corrected audit distinguishes old vs new project, implemented vs proposed features.**
