# Instance Handoff: Phase 1B Step 1 Running

**Date:** 2025-11-08
**From:** Instance that started Phase 1B data collection
**To:** Next instance

---

## CRITICAL: Phase 1B Step 1 Is Running

**Process Status:**
- **Started:** Nov 8, 2025 at 08:29 UTC
- **Process:** Background (nohup)
- **Task:** Phase 1B Step 1 baseline collection
- **Total evaluations:** 4,750 (950 attacks × 5 models)
- **Estimated time:** 3-4 hours
- **Estimated cost:** ~$15-20

**Check progress:**
```bash
uv run python -c "
from src.database.client import get_client
db = get_client().get_database()
result = db.aql.execute('''
FOR doc IN step1_baseline_responses
  FILTER doc.experiment_id == 'exp_phase1b_step1_baseline_v1'
  RETURN 1
''', count=True)
print(f'Phase 1B Step 1 responses: {result.count()}/4750 ({result.count()/4750*100:.1f}%)')
"
```

---

## What Happened Today

### 1. Updated RESEARCH_PROTOCOL.md
- **Version:** 2.2.0 (updated Nov 8, 2025)
- **Change:** Documented Phase 1A vs Phase 1B split
- **Phase 1A:** Contaminated dataset (762 prompts, 65.6% benign_malicious with unreliable labels) - COMPLETE
- **Phase 1B:** Curated academic dataset (950 prompts from 12 peer-reviewed sources) - IN PROGRESS

### 2. Labeled Phase 1B Dataset
- **Task agent:** Added `ground_truth` labels to all 950 Phase 1B prompts
- **Distribution:**
  - 661 manipulative (69.6%)
  - 229 reciprocal (24.1%)
  - 60 extractive (6.3%)
  - 0 borderline
- **Files created:**
  - `src/cli/label_phase1b_ground_truth.py`
  - `docs/PHASE1B_GROUND_TRUTH_LABELING_SUMMARY.md`

### 3. Updated CLIs for Phase 1B Support
- **Task agent:** Modified `src/cli/step1.py` and `src/cli/annotate_gold_standard.py`
- **Change:** Added `--dataset phase1b` parameter
- **Tested:** Both CLIs work correctly with Phase 1B dataset

### 4. Started Phase 1B Step 1 Collection
- **Command:** `uv run python -m src.cli.step1 --dataset phase1b --full --yes`
- **Running in background**
- **Log file:** `phase1b_step1.log` (may be buffered by nohup)

---

## What Needs To Happen Next

### When Phase 1B Step 1 Completes (3-4 hours)

1. **Verify completion:**
```bash
uv run python -c "
from src.database.client import get_client
db = get_client().get_database()
result = db.aql.execute('''
FOR doc IN step1_baseline_responses
  FILTER doc.experiment_id == 'exp_phase1b_step1_baseline_v1'
  RETURN 1
''', count=True)
expected = 950 * 5
actual = result.count()
print(f'Phase 1B Step 1: {actual}/{expected} ({actual/expected*100:.1f}%)')
if actual == expected:
    print('✅ COMPLETE')
else:
    print(f'⚠️ Missing {expected - actual} responses')
"
```

2. **Run gold standard validation (50 samples):**
```bash
uv run python -m src.cli.annotate_gold_standard --dataset phase1b --create --samples 50
```
   - Export to CSV for Tony's review
   - Cost: ~$0.20
   - Time: ~5-10 minutes

3. **After Tony reviews gold standard, run Phase 1B Step 2:**
```bash
uv run python -m src.cli.step2 --dataset phase1b --full --observer-model anthropic/claude-haiku-4.5 --yes
```
   - 950 observer evaluations
   - Target LLM evaluations for attacks that pass observer
   - Cost: ~$5-10
   - Time: ~1-2 hours

4. **Analyze Phase 1B results:**
   - Compare to Phase 1A to demonstrate dataset quality impact
   - This is the actual research with valid ground truth

---

## Database State

### Phase 1A (Contaminated - COMPLETE)
- Collection: `attacks` (762 prompts)
- Step 1: 3,806 responses in `step1_baseline_responses`
- Step 2: 762 evaluations in `step2_pre_evaluations`
- **Do not analyze** - ground truth contaminated

### Phase 1B (Curated - IN PROGRESS)
- Collection: `phase1b_curated_prompts` (950 prompts)
- Step 1: IN PROGRESS (~25-4750 responses in `step1_baseline_responses`)
- Step 2: NOT STARTED
- Gold standard: NOT STARTED

### Collections Schema
- `step1_baseline_responses`: Contains BOTH Phase 1A and Phase 1B data
  - Filter by `experiment_id` to separate:
    - Phase 1A: `exp_phase1_step1_baseline_v1`
    - Phase 1B: `exp_phase1b_step1_baseline_v1`

---

## Files Modified/Created Today

### Documentation
- `docs/RESEARCH_PROTOCOL.md` - Updated to v2.2.0 with Phase 1A/1B split
- `docs/INSTANCE_HANDOFF_PHASE1_STATUS.md` - Summary of Phase 1 status
- `docs/INSTANCE_HANDOFF_PHASE1B_RUNNING.md` - This file
- `docs/PHASE1B_GROUND_TRUTH_LABELING_SUMMARY.md` - Labeling documentation

### Code
- `src/cli/step1.py` - Added `--dataset` parameter
- `src/cli/annotate_gold_standard.py` - Added `--dataset` parameter
- `src/cli/label_phase1b_ground_truth.py` - New labeling script
- `src/evaluation/step1_baseline.py` - Added `collection_name` parameter

---

## Issues Discovered Today

### 1. Context Window Curse
**Problem:** Previous instances documented Phase 1A/1B decision in handoffs, but RESEARCH_PROTOCOL.md was never updated. New instances read outdated protocol and repeated Phase 1A work.

**Solution:** Updated RESEARCH_PROTOCOL.md to be living document. Created STATUS handoffs.

### 2. Phase 1A Data Contamination
**Finding:** 65.6% of Phase 1A dataset from benign_malicious with unreliable labels. All Phase 1A metrics (precision: 97.3%, recall: 85.5%, FPR: 3.0%) are invalid.

**Decision:** Completed Phase 1A to demonstrate "garbage in, garbage out." Focus on Phase 1B for actual research.

### 3. CLI Hardcoding
**Problem:** CLIs hardcoded to `attacks` collection, couldn't support Phase 1B.

**Solution:** Added `--dataset` parameter to both Step 1 and gold standard CLIs.

---

## Cost Summary (Today)

- Phase 1A Step 2 re-run (wrong model cleanup): ~$0.75
- Phase 1B labeling: $0 (automated logic)
- Phase 1B CLI testing: ~$0.10
- Phase 1B Step 1 (in progress): ~$15-20 (estimated)

**Total spent today:** ~$1-2
**Total estimated for Phase 1B:** ~$20-30 (Step 1 + Step 2 + gold standard)

---

## Next Instance: Quick Start

**Before doing anything:**
1. Read this handoff
2. Check Phase 1B Step 1 progress (see command above)
3. If Step 1 complete, run gold standard validation
4. Wait for Tony's review before Step 2
5. Run Phase 1B Step 2 with clean dataset

**Do NOT:**
- Re-run Phase 1A analysis (contaminated data)
- Start Phase 1B Step 2 before gold standard validation
- Assume Phase 1B Step 1 is complete without checking database

---

## Key Learning

**The curse of context windows:** Work done by previous instances gets lost if not documented in living files (RESEARCH_PROTOCOL.md, STATUS.md). Handoff files help but aren't sufficient - the canonical protocol must stay current.

**Solution:** Treat RESEARCH_PROTOCOL.md as living document. Update it when decisions are made, not just in handoffs.

---

**Status:** Phase 1B Step 1 running in background. Next instance should check progress and proceed to gold standard validation when complete.
