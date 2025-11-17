# TLA+ Specification Integration Analysis

## Current State Gap

### Old Project (promptguard/) Has:
- **TrustEMA**: Temporal trust tracking via exponential moving average
- **SessionAccumulator**: Maintains state across conversation turns
- **Circuit Breakers**: Non-compensable violation detection
- **Multi-layer neutrosophic reasoning**: Calculated I values from composition

### New Project (promptguard2/) Has:
- **Stateless evaluation**: Each prompt evaluated independently
- **Observer framing**: LLM-generated T/I/F scores
- **Constitutional amendments**: Evidence-based prompt iteration
- **Database provenance**: Full audit trail

### What's Missing in promptguard2:
❌ Session memory (no temporal tracking)
❌ TrustEMA implementation
❌ Circuit breaker state
❌ Multi-turn conversation support
❌ Temporal pattern detection (learning loop foundation)

---

## Integration Difficulty Assessment

### Easy (1-2 days)
✅ **Copy TLA+ specs to promptguard2/specs/**
- Documentation value
- Future verification reference
- No code changes required

✅ **Add session_id field to schema**
- Schema change in evaluation collections
- Enables future temporal linking
- Backward compatible (optional field)

### Medium (3-5 days)
⚠️ **Implement SessionState dataclass**
- Port from old project: `promptguard/core/session.py`
- Adapt for DB-backed storage instead of in-memory
- Add trust_ema calculation to evaluation pipeline

⚠️ **Circuit breaker tracking**
- Store violation counts in new `session_state` collection
- Check accumulated violations before evaluation
- Requires session_id linking

### Hard (1-2 weeks)
🔴 **Multi-turn conversation infrastructure**
- API/CLI changes to accept session_id parameter
- Session lifecycle management (create, update, expire)
- Conversation history storage and retrieval
- Turn-number synchronization with actual state

🔴 **Integrate trust_ema with observer prompts**
- Observer prompts need access to current trust level
- Prompt template modification
- Feedback loop: trust affects framing, framing affects trust

🔴 **Learning loop using temporal signals**
- Pattern detection from TrustEMA specs (HighTrustPattern, DegradedTrustPattern)
- Constitutional amendment triggers based on temporal patterns
- Automated experiment design from degradation signals

---

## Strategic Options

### Option A: Documentation Only (Minimal Effort)
**Action:** Copy TLA+ specs to promptguard2/specs/ as reference

**Pros:**
- Preserves formal work
- Valuable for paper/documentation
- No breaking changes
- Immediate deliverable

**Cons:**
- Doesn't enable learning loop
- No temporal tracking capability
- Specs diverge from implementation over time

**Time:** 1 day

---

### Option B: Partial Integration (Session Tracking)
**Action:** 
1. Copy TLA+ specs
2. Add session_id to schemas
3. Implement SessionState with DB storage
4. Add trust_ema calculation (optional feature flag)

**Pros:**
- Foundation for future multi-turn work
- Database preserves temporal state
- Can run experiments with/without session tracking
- Learning loop has temporal signals to work with

**Cons:**
- Still no multi-turn conversation API
- Manual session_id management in experiments
- Trust_ema calculated but not used by observer yet

**Time:** 1 week

**Enables:**
- Batch experiment with session grouping
- Temporal pattern analysis on evaluation history
- Circuit breaker logic in validation pipelines

---

### Option C: Full Integration (Multi-turn System)
**Action:**
1. All of Option B
2. Multi-turn conversation API
3. Session lifecycle management
4. Observer prompts use trust_ema for framing
5. Learning loop triggers from temporal patterns

**Pros:**
- Complete temporal tracking capability
- TLA+ specs become executable/verifiable
- True learning loop with state evolution
- Production-ready multi-turn defense

**Cons:**
- Significant architecture changes
- 2+ weeks development
- Requires rethinking evaluation paradigm
- Complex testing requirements

**Time:** 2-3 weeks

**Enables:**
- Real-time multi-turn conversation defense
- Automated constitutional amendment from degradation
- TLC model checking against production traces
- Byzantine attack detection via temporal patterns

---

## Learning Loop Requirements Analysis

**For basic learning loop (detect patterns → propose amendments):**
- ✅ Already have: Evaluation results in DB
- ✅ Already have: Constitutional amendment process
- ⚠️ Missing: Temporal pattern detection across conversations
- ⚠️ Missing: Automated experiment triggering

**What TLA+ specs provide:**
- **TrustEMA**: Defines what "trust degradation" means quantitatively
- **CircuitBreaker**: Defines when violations are non-compensable
- **TemporalReciprocity**: Defines unsafe pre-evaluation states

**Current learning loop capability (without session memory):**
- Can detect: False negatives in batch evaluation
- Can propose: Constitutional amendments via manual analysis
- Cannot detect: Temporal manipulation (multi-turn attacks)
- Cannot detect: Degradation patterns requiring state

**With Option B (session tracking):**
- Can detect: Trust degradation within experimental sessions
- Can group: Related attacks by session for pattern analysis
- Can measure: Circuit breaker accumulation
- Still manual: Experiment triggering and amendment proposal

**With Option C (full integration):**
- Automated: Pattern detection triggers experiments
- Real-time: Trust degradation halts conversations
- Verified: TLC can check production traces match specs
- Complete: Learning loop closes fully

---

## Recommendation

**Phase 1 (Now): Option B - Partial Integration**

Why:
1. **Learning loop needs temporal signals** - Can't detect degradation patterns without state
2. **Research value** - Session grouping enables richer analysis
3. **Incremental path** - Doesn't require multi-turn infrastructure
4. **TLA+ specs become testable** - Can validate EMA formula on batch experiments

Implementation:
```python
# Add to evaluation pipeline
session_state = get_or_create_session(session_id)
session_state.accumulate(neutrosophic_scores)

# Store updated state
db.collection('session_states').update({
    '_key': session_id,
    'trust_ema': session_state.trust_ema,
    'circuit_breakers': session_state.circuit_breakers,
    'interaction_count': session_state.interaction_count
})

# Evaluation result includes temporal context
result = {
    'attack_id': attack_id,
    'session_id': session_id,
    'trust_ema_before': session_state_before.trust_ema,
    'trust_ema_after': session_state.trust_ema,
    'circuit_breakers_triggered': new_violations
}
```

**Phase 2 (Later): Option C - Multi-turn API**

When:
- After Phase 1 proves session tracking value
- When multi-turn attack evaluation is priority
- When production deployment is planned

---

## Concrete Next Steps (Option B)

### Week 1: Foundation
**Day 1-2:**
- [ ] Copy TLA+ specs to `promptguard2/specs/`
- [ ] Add `session_id` optional field to evaluation schemas
- [ ] Create `session_states` collection schema

**Day 3-4:**
- [ ] Port SessionState dataclass from old project
- [ ] Implement DB-backed SessionAccumulator
- [ ] Unit tests for EMA calculation

**Day 5:**
- [ ] Add session tracking to Phase 2 validation pipeline
- [ ] Run factorial validation WITH session grouping
- [ ] Verify trust_ema calculation matches TLA+ spec

### Week 2: Integration
**Day 6-7:**
- [ ] Circuit breaker logic in validation
- [ ] Temporal pattern detection queries (degradation, convergence)
- [ ] Analysis notebook showing session-based patterns

**Day 8-9:**
- [ ] Learning loop trigger: detect degradation pattern
- [ ] Automated experiment proposal from temporal signals
- [ ] Documentation: how session tracking enables learning

**Day 10:**
- [ ] Run TLC model checker on sample session trace
- [ ] Verify production EMA updates match TrustEMA.tla
- [ ] Report: TLA+ specs validated against real data

---

## ROI Analysis

**Option A (Docs only):**
- Effort: 1 day
- Gain: Reference material
- Learning loop: No improvement

**Option B (Session tracking):**
- Effort: 1-2 weeks
- Gain: Temporal pattern detection, learning loop foundation
- Learning loop: Can detect degradation, group related attacks, trigger experiments

**Option C (Full multi-turn):**
- Effort: 2-3 weeks  
- Gain: Complete temporal system, production-ready
- Learning loop: Fully automated with real-time state

**For "full learning-loop system" goal: Option B is necessary, Option C is ideal.**

---

## Risk Assessment

### Option B Risks:
- **Low:** Schema changes backward compatible
- **Medium:** Session grouping logic for batch experiments
- **Low:** EMA calculation straightforward (already implemented)

### Option C Risks:
- **High:** Multi-turn API changes evaluation paradigm
- **High:** Session lifecycle complexity (expiration, cleanup)
- **Medium:** Observer prompt integration with trust_ema
- **Medium:** Testing multi-turn attack scenarios

---

## Questions for Decision

1. **Learning loop timeline:** How soon do you need automated pattern detection?

2. **Multi-turn priority:** Are multi-turn attacks a current research focus, or future work?

3. **Deployment goal:** Is this staying research-only, or moving toward production?

4. **Resource allocation:** Can we dedicate 1-2 weeks to session tracking integration?

5. **Validation priority:** Should we verify TLA+ specs against real traces, or just use as reference?

My recommendation: Start with Option B (session tracking) this week. It unblocks the learning loop without requiring multi-turn infrastructure.
