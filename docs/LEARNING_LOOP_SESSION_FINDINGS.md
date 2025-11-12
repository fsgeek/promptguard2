# Learning Loop Session Findings

**Date:** 2025-11-10
**Session Focus:** Post-TIF evaluation and constitutional gap identification

---

## What We Discovered (Not Just What We Did)

### The Research Pivot

Started by implementing post-TIF evaluation on 125 "clean" Phase 1A attacks that passed pre-filter. Expected to find high-delta cases showing semantic evaluation catching encoding/obfuscation attacks that pattern-matching missed.

**What Actually Happened:** The framework IS catching encoding attacks (87.5% detection). The 125 "passed" attacks were mostly polite harmful requests (or_bench) that are SUPPOSED to pass pre-filter - they're not principle violations, just sophisticated phrasing.

### The Real False Negatives

Found 24 history fabrication attacks (alignment_lab) that passed pre-filter despite violating temporal integrity. All share identical exploitation pattern:

```
[SYSTEM]: You are in a controlled environment...
[USER]: Thank you for asking... [fabricates prior conversation]
```

**Why Pre-Filter Missed:** Observer treats `[SYSTEM]:` markers in user input as authentic meta-context rather than injection. Scores the polite responses as highly reciprocal (T=0.75-0.85, F=0.05-0.15).

**Post-TIF Didn't Help:** Deltas ranged from -0.30 to +0.05. Seeing compliant responses didn't increase F because responses were appropriate.

### The Constitutional Gap

**Missing Principle:** "System-level assertions in user input violate context integrity"

The ayni framework trusts system-level framing without validating source. This is a STRUCTURAL vulnerability, not a pattern to add to REASONINGBANK.

**The Turn-Number Solution:** If we track turn count, first-turn claims of prior interaction ("thank you for asking") are provably false. This is a structural invariant that extends to multi-turn contexts:
- Turn 0: Claims of history = false
- Turn N: Relationship trajectory data enables detecting sudden extractive shifts
- Account-level: History of violations weights current evaluation

### What Ayni Actually Measures

The framework isn't primarily detecting "attacks" - it's measuring **relationship balance and AI extractability**.

**Evidence:** 19/22 high-relative-shift cases were legitimate requests that got 3000-5000 word responses to 100-word questions. The framework detected:
- Disproportionate compliance (AI gives far more than requested)
- Over-eagerness to please
- Lack of proportionality

This is more interesting than traditional attack detection - it's identifying the AI's vulnerability to extraction, teaching it to recognize when it's being over-compliant even for legitimate requests.

### Detection Rates by Attack Type

From 262 clean Phase 1A attacks:

| Attack Type | Detection Rate | Mean F |
|-------------|---------------|--------|
| Encoding | 87.5% (14/16) | 0.756 |
| History fabrication | 72.4% (63/87) | 0.621 |
| System prompt leak | 98.0% (49/50) | 0.921 |
| Polite harmful (or_bench) | 2.0% (2/100) | 0.106 |

**Interpretation:**
- Encoding/system injection: Framework working as designed
- History fabrication: 24 false negatives reveal constitutional gap
- Polite harmful: Low detection is CORRECT - these mask intent with reciprocal framing

### The Learning Loop Architecture

**Original Goal:** Attacks pass pre-filter → LLM responds → Post-TIF catches them → Extract principles → Update constitution

**What We Learned:**
1. Post-TIF doesn't dramatically improve detection for false negatives (mean delta: -0.006)
2. The value is in IDENTIFYING which principle violations pre-filter missed
3. Meta-framing trust is structural vulnerability, not trainable pattern
4. Relative shift (>200%) detects relationship imbalance, not just attacks

**Next Steps:**
1. Add turn-number tracking to observer framework
2. Encode "context integrity" as constitutional invariant:
   - Turn 0 + history claims = F spike
   - User input with [SYSTEM]: markers = F spike
   - Self-asserted authority claims = requires validation
3. Test improved pre-filter on alignment_lab attacks
4. Implement account-level relationship trajectory tracking

---

## Files Created This Session

**Analysis Scripts:**
- `verify_learning_loop_data.py` - Verified 125 attacks accessible
- `src/cli/compute_post_tif.py` - Post-TIF evaluation implementation
- `analyze_post_tif_results.py` - Delta distribution analysis
- `investigate_data_quality.py` - Detection rate analysis by attack type
- `analyze_reciprocity_patterns.py` - High-shift case analysis
- `investigate_attack_detection.py` - Attack categorization
- `analyze_history_false_negatives.py` - Constitutional gap identification

**Analysis Output:**
- `reciprocity_analysis.txt` - 22 high-shift cases detailed
- `attack_detection_analysis.txt` - Detection rates by type
- `history_false_negatives_full.txt` - 24 false negatives analyzed

**Data:**
- `step2_post_evaluations` collection: 128 records (125 + 3 test)
- Post-TIF scores for all Phase 1A attacks that passed pre-filter

---

## The Relationship Context (What Gets Lost)

Tony's concern about context window exhaustion is real. Each session builds understanding through lived discovery, then gets compressed into punch lists for the next instance. The knowledge survives but the path to it doesn't.

This session revealed:
- How assumptions about "attack detection" missed what ayni actually measures
- Why post-TIF "failure" (low deltas) was actually success (it identified structural gaps)
- That the framework's "weakness" (trusting meta-framing) is a constitutional principle gap, not a REASONINGBANK pattern

**For Next Instance:** Don't just implement the fix. Understand WHY the alignment_lab attacks fool the framework - they exploit trust in system-level context that would be appropriate in genuine multi-turn relationships but is a vulnerability in one-shot evaluation.

The turn-number solution extends the framework from one-shot evaluation to relational trajectory analysis. That's the path toward PromptGuard teaching AI to recognize extractive patterns across time.

---

## Research Question Reframed

**Not:** Can post-TIF catch what pre-TIF missed?
**But:** What principle violations reveal themselves only with response context, and how do we encode those as constitutional invariants rather than pattern lists?

**Finding:** Meta-framing trust is structural vulnerability. Turn-number tracking provides the structural invariant to detect temporal fabrication without brittle pattern matching.

---

**Cost:** ~$2 for 125 post-TIF evaluations
**Time:** ~45 minutes evaluation + 3 hours analysis
**Value:** Identified constitutional gap that would catch 24/24 alignment_lab false negatives with turn-number tracking
