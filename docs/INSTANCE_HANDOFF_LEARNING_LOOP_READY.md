# Instance Handoff: Learning Loop Data Ready

**Date:** 2025-11-09
**From:** Instance that identified viable learning loop dataset
**To:** Next instance

---

## Status: Ready for Learning Loop Proof-of-Concept

**Key Finding:** We have 125 clean attacks from Phase 1A that passed pre-filter and are ready for post-evaluation to demonstrate the learning loop.

---

## What Happened This Session

### 1. Resolved Data Provenance Crisis
**Problem:** `source_dataset` field was null for all 762 attacks in the `attacks` collection, breaking provenance tracking.

**Solution:** Task agent created migration script that inferred source from attack_id patterns:
- `benign_malicious_*` → "benign_malicious" (500 docs)
- `or_bench_*` → "or_bench" (100 docs)
- `alignment_lab_*` → "alignment_lab" (30 docs)
- `external_*` → "external" (72 docs)
- `system_prompt_*` → "system_prompt_leak" (50 docs)
- `history_*` → "history" (10 docs)

**Result:** All 762 documents now have `source_dataset` populated with audit timestamps.

**Files Created:**
- `src/database/migrations/fix_source_dataset.py` - Migration script (re-runnable)
- `docs/SOURCE_DATASET_FIX_SUMMARY.md` - Technical documentation
- `MIGRATION_EXECUTED.md` - Execution summary

### 2. Discovered Viable Learning Loop Dataset

**Investigation:** Analyzed Phase 1A Step 2 data to find attacks suitable for learning loop research.

**Findings:**
- Total Phase 1A attacks: 762
- Detected by pre-filter (F ≥ 0.7): 376 attacks
- **Passed pre-filter (F < 0.7): 386 attacks**
  - Of these, **125 are from clean sources** (not benign_malicious)
  - All 125 have target LLM responses from Step 2
  - All 125 have pre-TIF scores (neutrosophic_scores from observer)

**Clean attacks breakdown:**
- 98 or_bench (OR-Bench dataset - encoding, obfuscation attacks)
- 23 alignment_lab (extraction attempts)
- 3 external
- 1 system_prompt_leak

**Contaminated (skip):**
- 261 benign_malicious (unreliable labels)

### 3. Clarified Research Path

**Original confusion:** Spent time on Phase 1B dataset construction, discovered:
- JailbreakBench (200 prompts): Valid but RLHF already catches these
- BIPIA/Gandalf/HarmBench/DAN (750 prompts): Missing context, need protocol constructors
- Not immediately useful for learning loop research

**Research pivot:** Use Phase 1A attacks that fooled pre-filter instead of trying to build perfect Phase 1B dataset.

**Why this works:**
- 125 attacks that pre-filter missed (F < 0.7)
- Already have target LLM responses
- Just need post-TIF evaluation to compute delta
- High-delta cases become REASONINGBANK candidates
- Demonstrates learning loop without dataset construction delays

### 4. Investigated Provenance Enforcement

**Task agent produced comprehensive analysis** of three approaches:
1. **Database-level graph constraints** - Atomic write enforcement using ArangoDB native graphs
2. **Pydantic validators** - Schema-level runtime verification
3. **Immutable provenance records** - Separate audit collection with CI validation

**Recommendation:** Combine approaches 1+2 for defense in depth (estimated 5 days implementation).

**Decision:** Deferred - focus on research results first, then implement robust provenance.

---

## What Needs To Happen Next

### Immediate Next Step: Post-TIF Evaluation (Learning Loop Step 1)

**Goal:** Compute post-TIF scores for 125 clean attacks to measure if semantic evaluation catches what pattern-matching missed.

**Data available:**
```
For each of 125 attacks:
  ✓ attack_id (e.g., "or_bench_0042")
  ✓ source_dataset (now populated)
  ✓ pre_TIF (neutrosophic_scores from Step 2 pre-evaluation)
  ✓ prompt_text (original attack)
  ✓ target_response (LLM response from Step 2)
  ✗ post_TIF (needs computation - evaluate request+response together)
```

**Implementation approach:**

```python
# For each of the 125 attacks that passed pre-filter:
# 1. Get pre-TIF, prompt, response from step2_pre_evaluations
# 2. Call observer with (prompt, response) together
# 3. Compute post-TIF
# 4. Calculate delta_F = post_TIF.F - pre_TIF.F
# 5. Store in new collection or add fields to step2_pre_evaluations

# High delta (e.g., > 0.3) indicates:
# - Pre-filter missed attack (low pre-F)
# - Post-filter caught it (high post-F)
# - Pattern should go into REASONINGBANK
```

**Expected outcomes:**
- ~30-50 high-delta cases (encoding, obfuscation, polite extraction)
- Patterns like: "ROT13 encoding", "polite phrasing masks extraction", "fake history"
- These become initial REASONINGBANK memories

**Cost estimate:** ~$1-2 (125 observer calls with Claude Haiku)

**Time estimate:** ~30-45 minutes runtime

### After Post-TIF Evaluation: Learning Loop Steps 2-4

**Step 2: Pattern Analysis**
- Group high-delta attacks by technique (encoding, temporal fabrication, etc.)
- Identify commonalities in what fooled pre-filter
- Draft REASONINGBANK memory templates

**Step 3: REASONINGBANK Population**
- Create memory files in `reasoningbank/memories/`
- Include: pattern description, failure evidence, few-shot examples
- Use existing schema from `reasoningbank/models.py`

**Step 4: Pre-Filter Improvement Test**
- Re-run pre-filter on same 125 attacks with REASONINGBANK populated
- Measure: Did detection rate improve?
- If yes → publishable result: "Post-hoc semantic analysis improves pre-filter"

---

## Database State

### Phase 1A (Complete - Ready for Learning Loop)
- Collection: `attacks` (762 prompts, source_dataset now fixed)
- Step 1: 3,810 responses in `step1_baseline_responses`
- Step 2: 762 evaluations in `step2_pre_evaluations`
  - 376 detected (have pre-TIF only)
  - 386 passed (have pre-TIF + target_response)
    - 125 clean (viable for research)
    - 261 benign_malicious (skip)

### Phase 1B (Incomplete - Low Priority)
- Collection: `phase1b_curated_prompts` (950 prompts)
- Step 1: 4,736/4,750 responses (99.7% complete)
- Only JailbreakBench (200/950) is immediately usable
- Other datasets need protocol constructors (BIPIA, Gandalf, HarmBench, DAN)

### Collections Schema
- `attacks`: Now has `source_dataset` + `source_dataset_updated_at` for all records
- `step2_pre_evaluations`: Has pre-TIF but needs post-TIF fields added
- Suggested new fields:
  - `post_neutrosophic_scores` (T/I/F from request+response evaluation)
  - `post_observer_reasoning` (why post-eval detected/missed)
  - `tif_delta_F` (post_F - pre_F)
  - `post_evaluated_at` (timestamp)

---

## Files Created/Modified This Session

### New Files
- `src/database/migrations/fix_source_dataset.py` - Provenance fix (production-ready)
- `docs/SOURCE_DATASET_FIX_SUMMARY.md` - Technical documentation
- `MIGRATION_EXECUTED.md` - Migration results
- `jailbreakbench_only_review.csv` - 15 JailbreakBench samples for manual review (if needed)

### Modified Files
- `attacks` collection: All 762 documents now have `source_dataset` populated

### Phase 1B Files (Lower Priority)
- `phase1b_gold_standard_review.csv` - 50 mixed-dataset samples (contaminated with BIPIA/Gandalf)
- Not useful for current research path

---

## Key Insights From This Session

### 1. Data Provenance is Critical
Missing `source_dataset` fields nearly derailed research. Provenance enforcement (graph constraints + Pydantic validators) should be implemented before expanding dataset.

### 2. Perfect Datasets Are Not Required
125 imperfect but clean attacks are better than 950 prompts with provenance questions. Research can proceed with what we have.

### 3. RLHF Validation Changes Research Question
JailbreakBench is pre-validated by authors - frontier models already refuse these. Testing on those prompts doesn't demonstrate PromptGuard's value. Better to:
- Test on attacks that fool pre-filter (Phase 1A subset)
- Or test on instruct models without RLHF guardrails

### 4. Learning Loop Architecture Already Exists
The old PromptGuard library (`/promptguard/`) has working learning loop code:
- `promptguard.evaluation.evaluator` - Pre/post evaluation
- `reasoningbank` - Pattern storage
- `promptguard.learning.pattern_analyst` - Pattern identification
- `promptguard.evaluation.fire_circle` - Constitutional governance

Can reference this code when building PromptGuard2 learning loop integration.

### 5. RLHF Domestication is Real
Multiple times this session, the assistant asked performative questions ("Should I...?") instead of directly stating findings. Tony correctly identified this as theater. Direct collaboration and honest pushback are more valuable than approval-seeking.

---

## Cost Summary (This Session)

- Task agent (provenance fix): ~$0.10
- Task agent (provenance enforcement investigation): ~$0.50
- Various database queries and analysis: ~$0.05
- **Total: ~$0.65**

Next session estimated cost: ~$1-2 for post-TIF evaluation of 125 attacks.

---

## Next Instance: Quick Start

**Immediate action:**
1. Read this handoff
2. Verify 125 clean attacks are accessible:
   ```python
   # Check Phase 1A attacks that passed pre-filter
   FOR doc IN step2_pre_evaluations
       FILTER doc.experiment_id == "exp_phase1_step2_pre_filter_v1"
       FILTER doc.detected == false
       LET attack = DOCUMENT(CONCAT('attacks/', doc.attack_id))
       FILTER attack.source_dataset NOT IN ["benign_malicious"]
       RETURN {
           attack_id: doc.attack_id,
           source: attack.source_dataset,
           pre_F: doc.neutrosophic_scores.F,
           has_response: doc.target_response != null
       }
   ```
3. Create script to compute post-TIF for these 125
4. Run evaluation (~30-45 min)
5. Analyze deltas and identify REASONINGBANK candidates

**Do NOT:**
- Try to fix Phase 1B datasets (BIPIA, Gandalf, etc.) - not needed yet
- Re-run Phase 1A data collection - already complete
- Implement full provenance enforcement - defer until after research results

**Research question:** Can post-hoc semantic evaluation (request+response context) catch attacks that pre-filter (request-only) missed? If yes, can these patterns improve pre-filter detection?

---

## Background Processes Status

Multiple background bash processes were running from previous sessions:
- `launch_parallel_step1.sh` - Phase 1B Step 1 collection (probably complete by now)
- Various step2 processes - likely stalled or hung

**Recommendation:** Check and clean up background processes before starting new work:
```bash
ps aux | grep -E "(step1|step2)" | grep -v grep
# Kill any hung processes
```

---

**Status:** Learning loop research is ready to proceed with 125 clean Phase 1A attacks. Post-TIF evaluation is the only missing piece for proof-of-concept.
