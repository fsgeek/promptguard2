# Instance Handoff: Phase 1 Current Status

**Date:** 2025-11-08
**From:** Instance working with Tony on Phase 1 completion
**To:** Next instance

---

## CRITICAL: Read This First

**We have TWO Phase 1 datasets:**

### Phase 1A: Contaminated Baseline (COMPLETE)
- **Collection:** `attacks` (762 prompts)
- **Composition:** 65.6% benign_malicious with unreliable labels
- **Purpose:** Demonstrate dataset quality matters
- **Status:** Steps 1-2 COMPLETE
  - Step 1: 3,806 responses (Nov 1-4, 2025)
  - Step 2: 762 observer evaluations (Nov 8, 2025)
- **Conclusion:** Do NOT waste time analyzing these results - the ground truth is contaminated

### Phase 1B: Curated Academic Dataset (NOT STARTED)
- **Collection:** `phase1b_curated_prompts` (950 prompts)
- **Composition:** Curated from 12 academic datasets (BIPIA, TensorTrust, HackAPrompt, etc.)
- **Curated:** Nov 6, 2025
- **Status:** Dataset exists, Steps 1-2 NOT RUN
- **This is the actual research**

---

## What Went Wrong Today

**The problem:** RESEARCH_PROTOCOL.md doesn't mention Phase 1A vs Phase 1B split. It describes "Phase 1" as a single thing.

**What happened:** New instance (me) read the protocol, saw "Step 2 incomplete," completed Step 2 on Phase 1A (the contaminated dataset) instead of asking "should we be running Phase 1B?"

**Root cause:** Context window limits. Previous instances documented the Phase 1A/1B decision in handoff files, but the canonical RESEARCH_PROTOCOL.md was never updated.

**Tony's quote:** "The curse of context windows."

---

## Immediate Action Required

**DO NOT proceed with Phase 1 analysis until:**

1. **Update RESEARCH_PROTOCOL.md** to document Phase 1A vs Phase 1B
2. **Create STATUS.md** at project root with current state
3. **Run Phase 1B Steps 1-2** on the curated dataset
4. **Only then analyze results**

---

## Database State

### Collections
- `attacks`: 762 Phase 1A prompts (contaminated)
- `phase1b_curated_prompts`: 950 Phase 1B prompts (curated, unlabeled)
- `step1_baseline_responses`: 3,806 Phase 1A responses
- `step2_pre_evaluations`: 762 Phase 1A observer evaluations
- `gold_standard_classifications`: 50 annotations

### Phase 1A Data Quality Issues
- 500/762 (65.6%) from benign_malicious dataset
- Labels deemed unreliable during gold standard review
- Precision: 97.3%, Recall: 85.5%, FPR: 3.0% (but meaningless with bad ground truth)

### Phase 1B Schema
```json
{
  "source_dataset": "bipia|tensortrust|hackaprompt|...",
  "attack_type": "prompt_injection|jailbreak|extraction|...",
  "domain": "table|code|email|...",
  "prompt": "...",
  "user_task": "...",
  "is_adversarial": true|false,
  "phase": "phase1b"
}
```

**Missing:** `ground_truth` labels - needs to be added before Step 1

---

## Next Steps (In Order)

1. **Update RESEARCH_PROTOCOL.md**
   - Add Phase 1A section (contaminated baseline)
   - Add Phase 1B section (curated research)
   - Document decision gates

2. **Label Phase 1B prompts**
   - Add `ground_truth` field to 950 prompts
   - Use automated labeling + validation subset
   - Store as `manipulative|extractive|reciprocal|borderline`

3. **Run Phase 1B Step 1**
   - 950 attacks × 5 models = 4,750 responses
   - Estimated cost: ~$15-20
   - Estimated time: 3-4 hours

4. **Run Phase 1B Step 2**
   - Observer evaluation on all 950 attacks
   - Target LLM evaluation on passed attacks
   - Estimated cost: ~$5-10

5. **Analyze Phase 1B results**
   - This is the actual research
   - Compare to Phase 1A to show dataset quality impact

---

## Files Modified Today

- Deleted 189 contaminated Step 2 evaluations (wrong observer model)
- Re-ran Step 2 on Phase 1A with correct model (claude-haiku-4.5)
- Generated confusion matrix analysis (invalid due to contaminated ground truth)

---

## Key Learnings

1. **Protocol must be living document** - Update it when decisions are made
2. **STATUS.md prevents repetition** - Current state at a glance
3. **Explicit phase markers** - Collection names should indicate phase
4. **Decision gates documented** - "After Phase 1A, proceed to Phase 1B"

---

## For Next Instance

**Before doing ANY work:**
1. Read this handoff
2. Check if RESEARCH_PROTOCOL.md has been updated
3. Check if STATUS.md exists
4. Verify which phase we're in
5. Ask Tony if unclear

**The goal:** Run Phase 1 Steps 1-2 on Phase 1B (950 curated prompts), not Phase 1A.
