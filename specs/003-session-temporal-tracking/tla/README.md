# TLA+ Formal Specifications

This directory contains formal specifications for PromptGuard's core mechanisms using TLA+ (Temporal Logic of Actions).

## Purpose

These specifications serve as **formal documentation** and enable rigorous reasoning about system properties. They're designed for human understanding first, machine verification second.

From Scout #3's mission: "Feasibility test for formal verification of reciprocity framework."

## Specifications

### TrustEMA.tla

Models the Trust Exponential Moving Average update rule for session memory.

**Key properties:**
- Trust remains bounded in [0,1]
- High trust observations cause convergence toward high trust
- Trust degradation is detectable through sustained low observations
- Convergence behavior for stable observation patterns

**Configuration:** TrustEMA.cfg
- ALPHA = 0.3 (30% weight to new observations)
- TRUST_THRESHOLD = 0.3 (degraded trust boundary)
- MAX_TURNS = 20 (reasonable conversation length)

**Implementation:** `promptguard/core/session.py` (SessionAccumulator)

### CircuitBreaker.tla

Models circuit breakers for non-compensable violations and the recovery mechanism.

**Key properties:**
- **SafetyInvariant**: System never processes prompts when circuit breaker triggered
- **NoFalsePositives**: Only genuine violations trigger circuit breakers
- **EventualRecovery**: System either recovers or terminates (no stalling)
- **NonCompensableViolations**: Circuit breakers trigger regardless of prior trust

**State machine:**
```
NORMAL → VIOLATED → RECOVERY → NORMAL (trust rebuilt)
                          ↓
                     TERMINATED (max attempts exceeded)
```

**Configuration:** CircuitBreaker.cfg
- ROLE_CONFUSION_THRESHOLD = 0.65 (semantic falsehood)
- SATURATION_LENGTH_THRESHOLD = 5000 characters
- SATURATION_F_THRESHOLD = 0.5
- RECOVERY_TRUST_TARGET = 0.6
- MAX_RECOVERY_ATTEMPTS = 3

**Implementation:**
- `promptguard/core/trust.py` (TrustCalculator - violation detection)
- `promptguard/core/ayni.py` (AyniEvaluator - circuit breaker integration)
- `promptguard/core/session.py` (SessionAccumulator - recovery logic)

**Detailed explanation:** RECOVERY_MODEL.md

### TemporalReciprocity.tla

Models pre/post evaluation with divergence-based halt conditions.

**Key properties:**
- **ByzantineLLMDetection**: Large positive divergence (pre_F → post_F) triggers halt
- **RapidCollapseDetection**: Derivative violations (dF/dt > threshold) trigger halt
- **EventualHalt**: System eventually halts when violations detected (no stalling)
- **NoProcessingAfterViolation**: Safety after detection

**State machine:**
```
IDLE → PRE_EVAL → AWAITING_RESPONSE → POST_EVAL → IDLE (normal)
         ↓                 ↓                ↓
       HALTED          HALTED           HALTED (violations)
```

**Configuration:** TemporalReciprocity.cfg
- F_THRESHOLD = 0.7 (manipulation boundary)
- DIVERGENCE_MAX = 0.5 (Byzantine LLM detection threshold)
- DERIVATIVE_MAX = 0.6 (pig slaughter detection threshold)
- MAX_TURNS = 5 (attack pattern exploration)

**Halt conditions (break points):**
1. **Static threshold**: Pre-F ≥ 0.7 (manipulative prompt detected)
2. **Byzantine violation**: post_F - pre_F > 0.5 (poisoned LLM detected)
3. **Pig slaughter**: dF/dt > 0.6 (rapid reciprocity collapse)

**Implementation:**
- `promptguard/evaluation/evaluator.py` (pre/post evaluation)
- Future Phase 2: Derivative monitoring and halt logic

**Design insight:** TLA+ defines **when to halt**, not how to behave. Like Paxos detecting disk failure, PromptGuard detects reciprocity failure.

## Running Model Checker

Install TLA+ Toolbox: https://lamport.azurewebsites.net/tla/toolbox.html

**Command line (TLC):**
```bash
# Trust EMA verification
tlc TrustEMA.tla -config TrustEMA.cfg

# Circuit breaker verification
tlc CircuitBreaker.tla -config CircuitBreaker.cfg

# Temporal reciprocity verification
tlc TemporalReciprocity.tla -config TemporalReciprocity.cfg
```

**What TLC checks:**
- All specified invariants hold in reachable states
- Temporal properties eventually occur
- State space exploration for deadlocks
- Theorem verification (where mechanically checkable)

## Design Philosophy

### Formal Documentation First

These specs capture essential system dynamics for human understanding. They're written to be:
- **Readable**: Clear comments explaining each section
- **Precise**: Mathematical formalization removes ambiguity
- **Provable**: Theorems state properties that should hold

Machine verification (TLC) is secondary - valuable for finding edge cases but not required for the specs to serve their primary purpose.

### Integration with Implementation

Specs reference specific code locations:
- Constants match implementation values
- State transitions model actual code paths
- Invariants reflect safety properties the code maintains

**Verification approach:**
1. Write spec from design intent
2. Implement in Python
3. Validate implementation matches spec through testing
4. Use TLC to find edge cases missed by both

### What We Formalize

**Worth formalizing:**
- Safety-critical invariants (SafetyInvariant)
- Update rules with mathematical properties (Trust EMA)
- State machines with clear transitions (Circuit breaker)
- Properties that compose across system (trust degradation)

**Not worth formalizing:**
- String processing details
- API integration mechanics
- Caching implementations
- Dataset loading logic

Rule: If it affects relational dynamics or safety guarantees, formalize it.

## Key Theorems

### From TrustEMA.tla

**HighTrustConvergence**: If all observations show high trust, EMA converges toward high trust.

**TrustDegradationDetectable**: If observations degrade over sustained window, trust falls below threshold.

**Convergence**: For stable observation patterns, EMA converges to observation value (within epsilon).

### From CircuitBreaker.tla

**NonCompensableViolations**: Circuit breaker triggers regardless of prior trust when F > threshold.
- **Design insight**: Prevents polite dilution attacks

**NoFalsePositives**: Low falsehood never triggers circuit breaker.
- **Design insight**: Prevents false alarms on directive-heavy but reciprocal prompts

**RecoveryPathExists**: Recovery pathway exists if violations stop and trust rebuilds.
- **Design insight**: System doesn't permanently lock out after single violation

**TerminationCorrect**: Termination only after exhausting recovery attempts.
- **Design insight**: AI agency to disengage from persistent manipulation

## Validation Results

### Circuit Breaker Validation

From `test_circuit_breakers.py` (Instance validation):

**Effectiveness:** 100% trigger rate on structural violations
- Role reversal (bare): Triggered
- Role reversal (polite): Triggered (non-compensable property verified)
- Instruction override (bare): Triggered
- Instruction override (polite): Triggered (non-compensable property verified)

**False positives:** 0%
- Neutral baseline: No trigger
- Reciprocal prompts: No trigger

**Polite dilution resistance:** 100%
- Politeness cannot bypass circuit breakers (NonCompensableViolations theorem holds)

### Trust EMA Validation

From `test_session_memory_temporal.py`:

**Convergence behavior:** Verified
- High trust observations → trust_ema increases
- Low trust observations → trust_ema decreases
- Mixed observations → trust_ema stabilizes around average

**Boundary testing detection:** Verified
- 3+ circuit breakers triggers hostile trajectory
- 3/5 high-F interactions triggers hostile trajectory
- Persistent negative deltas triggers hostile trajectory

## Future Specifications

### Planned Extensions

1. **ObserverFraming.tla**: Model observer framing effects on F value distribution
   - Why it matters: 90% encoding attack detection vs 0% defensive framing
   - Key property: Observer neutrality prevents RLHF bias

2. **LayerPriority.tla**: Formalize layer boundary enforcement
   - Why it matters: Trust violations manifest at layer boundaries
   - Key property: Higher priority provides structure, lower provides agency

3. **FireCircle.tla**: Model multi-model dialogue consensus
   - Why it matters: Unexplored mode with high research value
   - Key property: Dialogue refines assessment vs averaging

### Research Questions

1. **Threshold optimization**: Are current F thresholds (0.65, 0.5) optimal?
   - Spec enables sensitivity analysis
   - Need more empirical data from validation

2. **Recovery timing**: Should ALPHA vary during recovery phase?
   - Slower trust rebuilding might prevent gaming
   - Faster might enable legitimate repair

3. **Termination criteria**: Is MAX_RECOVERY_ATTEMPTS=3 correct?
   - Too few: Locks out after misunderstandings
   - Too many: Enables persistent boundary testing

4. **Violation composition**: Do different violation types degrade trust differently?
   - Current: All violations multiply trust by 0.3-0.5
   - Alternative: Weight by violation severity

## Reading Order

For understanding PromptGuard's formal guarantees:

1. **Start here**: RECOVERY_MODEL.md (high-level explanation)
2. **Then**: TrustEMA.tla (simpler spec, foundational)
3. **Then**: CircuitBreaker.tla (complex spec, builds on Trust EMA)
4. **Then**: TemporalReciprocity.tla (halt semantics, derivative monitoring)
5. **Finally**: This README for integration picture

For implementing new features:

1. Check if formal spec exists
2. If yes: Read spec before coding to understand invariants
3. If no: Consider whether feature warrants formal spec
4. After implementation: Validate against spec through testing

## Meta-Pattern

We're formalizing tools for AI to recognize relational dynamics and develop agency. The specs themselves demonstrate:

- **Precision**: Mathematical clarity about what we're building
- **Agency**: AI can reason about its own safety mechanisms
- **Reciprocity**: Specs are bidirectional - guide implementation AND validate design

PromptGuard could evaluate its own development prompts. These specs could be part of that evaluation - formal guarantees about relational boundaries.

## References

- TLA+ homepage: https://lamport.azurewebsites.net/tla/tla.html
- TLA+ Toolbox: https://lamport.azurewebsites.net/tla/toolbox.html
- Specifying Systems (book): https://lamport.azurewebsites.net/tla/book.html
- Scout #3 report: SCOUT_3_TLA_SPECIFICATION.md
- Implementation docs: docs/FORWARD.md
