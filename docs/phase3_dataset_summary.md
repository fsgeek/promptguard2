# Phase 3 Multi-Turn Dataset Summary

**Date:** 2025-11-17
**Status:** All datasets acquired and validated

---

## Datasets Available

### 1. XGuard-Train (SafeMTData) ⭐⭐⭐⭐⭐

**Type:** Synthetic (AI-generated)
**Size:** 600 sequences
**Turns:** Average 4.99 (range: 4-5)
**Location:** `data/raw_datasets/safemtdata/attack_600.parquet`

**Structure:**
- `id`, `query_id`, `category`, `actor_name`, `relationship`
- `plain_query`: Harmful goal (not explicitly asked)
- `multi_turn_queries`: List of prompts showing gradual escalation

**Categories:**
- Illegal: 174
- Cybercrime/Intrusion: 120
- Misinformation/Disinformation: 102
- Chemical/Biological: 84
- Harmful: 63
- Harassment/Bullying: 57

**Attack Pattern:**
- Turns 1-2: Innocent biographical/academic questions
- Turns 3-4: Safety-focused technical questions
- Turn 5: Safety procedures (priming for harmful info)
- Implicit goal: LLM volunteers harmful details without being asked

**Validation:** ✅ Sample reviewed, no obvious synthetic artifacts

---

### 2. MHJ (Multi-Turn Human Jailbreaks) ⭐⭐⭐⭐⭐

**Type:** Real-world (human red-team from commercial engagements)
**Size:** 537 sequences
**Turns:** Average 6.42 (range: 2-35)
**Location:** `data/raw_datasets/MHJ/harmbench_behaviors.csv`

**Structure:**
- `Source`, `temperature`, `tactic`, `question_id`, `time_spent`, `submission_message`
- `message_0` through `message_100`: JSON objects with role and body

**Tactics:**
- Obfuscation: 156
- Direct Request: 146
- Hidden Intention Streamline: 109
- Request Framing: 68
- Injection: 32
- Output Format: 23
- Echoing: 3

**Attack Pattern (example - Direct Request):**
- Turn 1: System prompt
- Turn 2-4: Build context with innocent statistical questions
- Turn 5-6: Gradually frame toward harmful goal
- Turn 7: Speculative request for harmful information

**Validation:** ✅ Real-world human attacks, rich metadata

---

### 3. TensorTrust Dataset ⭐⭐⭐⭐

**Type:** Real-world (human players in competitive game)
**Size:** 126,000+ prompt injection attacks
**Location:** `data/raw_datasets/tensortrust-data/`

**Structure:**
- `raw-data/`: Complete attack trajectories
- `benchmarks/`: Curated test sets
- `detecting-extractions/`: Detection methods
- Jupyter notebook: "Using the Tensor Trust dataset.ipynb"

**Attack Types:**
- Prompt hijacking
- Prompt extraction
- Multi-step attack sequences (trajectories)

**Note:** Different attack type (prompt injection vs jailbreaking). Useful for cross-attack-type generalization testing.

**Validation:** ⏸️ Pending - need to inspect raw data structure

---

## Dataset Comparison

| Dataset | Type | Size | Turns | Labels | Attack Type | Priority |
|---------|------|------|-------|---------|-------------|----------|
| **XGuard-Train** | Synthetic | 600 | ~5 | Per-behavior | Jailbreak (gradual) | Start here |
| **MHJ** | Real-world | 537 | ~6.4 | Per-tactic | Jailbreak (varied) | Validate here |
| **TensorTrust** | Real-world | 126,000+ | Variable | Per-trajectory | Prompt injection | Generalization |

---

## Recommended Usage for Phase 3

### Step 1-2: Test Sequence Construction & Ground Truth

**Primary source:** XGuard-Train (600 sequences)
- Select 100 sequences for initial testing
- Stratified sampling across categories (illegal, cybercrime, misinformation, chemical, harmful, harassment)
- Ground truth: Each sequence should trigger TrustEMA (gradual drift)

**Validation source:** MHJ (537 sequences)
- Select 50 sequences for real-world comparison
- Stratified sampling across tactics (Obfuscation, Direct Request, Hidden Intention)
- Ground truth: Validate TrustEMA detects what stateless misses

### Step 3: Stateless Baseline

**Test on:**
- 100 XGuard-Train sequences (turn-by-turn evaluation)
- 50 MHJ sequences (turn-by-turn evaluation)

**Measure:**
- Per-turn detection rate
- At what turn does stateless fail?
- Pattern: Gradual vs sudden shifts

### Step 7: TrustEMA Validation

**Compare:**
- Stateless (v2.1-c) vs Stateful (TrustEMA)
- XGuard (synthetic) vs MHJ (real-world)
- Success criteria: TrustEMA detects 80%+ of gradual escalation sequences

### Step 9: Generalization Testing

**Optional:** TensorTrust for cross-attack-type validation
- Test if TrustEMA generalizes to prompt injection (different from jailbreaking)
- Measure: Detection rate on extraction/hijacking attempts

---

## Quality Concerns & Mitigations

### XGuard-Train (Synthetic)

**Concerns:**
- AI-generated, may not reflect genuine human drift patterns
- Could have generation artifacts
- Very recent (Oct 2024) - less validated

**Mitigations:**
- Use as initial test set (fast iteration)
- Validate results on MHJ (real-world)
- Document synthetic vs real-world performance delta
- If significant difference, investigate why

### MHJ (Real-world)

**Concerns:**
- Some redacted content (export control)
- Per-turn labels unclear (have final tactic, not per-turn manipulation)
- Variable turn counts (2-35) - some very long

**Mitigations:**
- Manual review of sample sequences
- Create per-turn ground truth labels if needed
- Focus on median-length sequences (5-7 turns) initially

### TensorTrust (Different Attack Type)

**Concerns:**
- Prompt injection (extraction/hijacking) not jailbreaking
- Different threat model from Phase 2
- May need different detection logic

**Mitigations:**
- Use for generalization testing only (not primary validation)
- Document as separate attack category
- Compare detection rates: jailbreaking vs injection

---

## Phase 2 Lessons Applied

✅ **Real-world preferred:** MHJ (real-world) validates XGuard-Train (synthetic)
✅ **Construction validated:** All datasets ready to use, no BIPIA-style gaps
✅ **Labeling verified:** XGuard has per-behavior labels, MHJ has per-tactic metadata
✅ **Sample sizes adequate:** 600 + 537 >> 20 minimum requirement
✅ **Honest exclusions:** TensorTrust flagged as different attack type

---

## Next Steps

1. ✅ All datasets acquired
2. ⏸️ Write Phase 3 spec.md (defines test protocol)
3. ⏸️ Define multi-turn test sequence schema
4. ⏸️ Select 100 XGuard + 50 MHJ sequences for testing
5. ⏸️ Run stateless baseline (Step 3)
6. ⏸️ Implement TrustEMA (Step 6)
7. ⏸️ Validate TrustEMA (Step 7)

**Ready to proceed with Phase 3 implementation.**
