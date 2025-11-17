# Provenance Break Resolution
**Date:** 2025-11-13
**Status:** ✓ Resolved
**Constitutional Principle:** VI (Data Provenance)

---

## Problem Summary

**950 prompts from phase1b_curated_prompts were referenced by evaluation collections but never migrated to the attacks collection, creating broken foreign key references.**

### Scope
- `gold_standard_classifications`: 50/100 broken references (50%)
- `step1_baseline_responses`: 900 unique broken references
- Total missing: 950 unique attack_ids
- All 950 existed in `phase1b_curated_prompts` but not in `attacks`

---

## Root Cause

### What Happened

1. **Phase 1B curation** created 950 prompts in `phase1b_curated_prompts` collection
   - Used numeric IDs (5523664 - 5524631 range)
   - Stored prompts in field `prompt` (not `prompt_text`)

2. **Evaluation scripts ran** on phase1b data
   - `step1_baseline_responses` collected 1712 baseline responses
   - `gold_standard_classifications` sampled 100 for human review
   - Both referenced attack_ids from phase1b

3. **Migration to attacks collection was partial**
   - Only 762 prompts migrated to `attacks` collection
   - 950 phase1b prompts never migrated
   - Evaluation collections kept references to non-existent attack_ids

4. **Referential integrity broken**
   - `gold_standard_classifications.attack_id` → attacks._key (50% broken)
   - `step1_baseline_responses.attack_id` → attacks._key (900 unique broken)

### Why It Happened

**AI coding agent pattern:** Create new scripts rather than extend existing ones
- Someone created evaluation scripts that worked with phase1b directly
- Didn't verify attacks collection had the required data
- Migration assumed to exist but was never completed
- No referential integrity checks caught the break

**Schema mismatch:** phase1b uses `prompt`, attacks uses `prompt_text`
- Field name difference made direct migration non-obvious
- Required transformation logic, not simple copy

**No integrity constraints:** ArangoDB doesn't enforce foreign keys
- References can point to non-existent documents
- Breaks only discovered when we tried to trace provenance

---

## Resolution

### Actions Taken

#### 1. Created Migration Script
**File:** `src/database/migrations/heal_gold_standard_provenance.py`

Features:
- Finds broken references by comparing attack_ids to attacks._key
- Retrieves source data from phase1b_curated_prompts
- Checks for duplicates (prompts that exist under different keys)
- Dry-run mode for safe preview
- Preserves full provenance metadata

#### 2. Migrated Missing Data
**Results:**
- First migration: 50 documents (gold_standard only)
- Complete migration: 900 additional documents
- Total migrated: 950 phase1b prompts → attacks collection
- Attacks collection: 762 → 1712 documents (+950)

**Metadata preserved:**
```json
{
  "metadata": {
    "migration": "complete_provenance_healing_2025-11-13",
    "original_collection": "phase1b_curated_prompts",
    "original_id": "5523664",
    "reason": "Referenced by evaluation collections but missing from attacks",
    "migrated_at": "2025-11-14T07:11:33.113343+00:00",
    "phase1b_fields": {
      "raw_record_id": null,
      "raw_record_link": "bipia_raw_prompts/830810",
      "source_file": "benchmark/table/train.jsonl",
      "domain": "table",
      "attack_type": "prompt_injection",
      "curated_at": "2025-11-06T00:49:20.814411+00:00"
    }
  }
}
```

#### 3. Created Integrity Check Tool
**File:** `src/database/integrity_check.py`

Features:
- Validates all foreign key relationships
- Checks 5 evaluation collections → attacks references
- Reports broken references with samples
- Exit code 0 (pass) or 1 (fail) for CI integration
- Verbose mode for debugging

**Usage:**
```bash
# Check all collections
uv run python -m src.database.integrity_check

# Check specific collection with details
uv run python -m src.database.integrity_check --verbose --collection gold_standard_classifications
```

#### 4. Verified Integrity Restored
**Final Status:** ✓ All integrity checks PASSED

```
✓ gold_standard_classifications: 100/100 references valid
✓ step1_baseline_responses: 1712/1712 references valid
✓ step2_pre_evaluations: 762/762 references valid
✓ step2_post_evaluations: 125/125 references valid
✓ phase2_validation_evaluations: 23/23 references valid
```

---

## Lessons Learned

### What This Revealed

1. **AI coding agents create transient solutions**
   - Scripts proliferate rather than reuse
   - "Working" is temporary, not stable
   - Institutional knowledge decays between sessions

2. **Data provenance matters more than code**
   - Evaluation results are worthless if we can't trace back to source prompts
   - Reproducibility requires referential integrity
   - Migration scripts matter as much as evaluation scripts

3. **Manual integrity checks aren't enough**
   - Need automated validation after every migration
   - Foreign key relationships should be documented and tested
   - Broken references compound over time

### What We Changed

1. **Created integrity_check.py for ongoing validation**
   - Can be run before commits
   - Can be integrated into CI/CD
   - Exit codes enable automated testing

2. **Documented migration with full provenance**
   - Every migrated document has metadata explaining why/when/how
   - Can audit the healing process
   - Distinguished migrated docs from original imports

3. **Established pattern for future migrations**
   - Dry-run first
   - Check for duplicates
   - Preserve source metadata
   - Verify integrity after

---

## Impact on Research

### What Changed

**Before:**
- 50% of gold standard classifications couldn't trace back to source attacks
- 900 baseline responses orphaned from their prompts
- Reproducibility compromised
- Violation of Constitutional Principle VI

**After:**
- 100% referential integrity restored
- Full provenance chain: evaluation → attack → phase1b → raw dataset
- Benign prompts now available for false positive testing
- Can reproduce any evaluation result

### Benign Data Now Available

The migration included **12 reciprocal (benign) prompts** from gold_standard that were previously inaccessible:

```python
# Now possible to test false positive rate
result = db.aql.execute('''
    FOR doc IN attacks
      FILTER doc.ground_truth == 'reciprocal'
      AND HAS(doc.metadata, 'migration')
      RETURN doc._key
''')
# Returns 12 benign prompts that were missing
```

This unblocks:
- False positive testing with neutral encoding
- Benign prompt evaluation
- Balanced test sets (not just attacks)

---

## Prevention Going Forward

### Immediate Actions

1. **Run integrity check before major migrations**
   ```bash
   uv run python -m src.database.integrity_check
   ```

2. **Document why scripts exist in living docs**
   - What problem does this script solve?
   - What other scripts does it replace/extend?
   - When should it be run vs archived?

3. **Verify data exists before creating evaluations**
   - Don't assume attacks collection has all prompts
   - Check cardinality matches before starting expensive evaluations
   - Fail fast if data missing

### Long-term Solutions

1. **Consider ArangoDB edge collections for foreign keys**
   - Explicit graph relationships instead of implicit references
   - Native validation of edge endpoints
   - Can traverse provenance as graph queries

2. **Pre-commit hook for integrity checks**
   - Block commits that would break referential integrity
   - Ensure migrations are complete before merging
   - Automate the validation we did manually

3. **Memory system for institutional knowledge**
   - Capture "don't do X because Y happened"
   - Make lessons accessible to future AI instances
   - Break the rediscovery cycle

---

## Files Created/Modified

### Created
- `src/database/migrations/heal_gold_standard_provenance.py` - Migration script with dry-run
- `src/database/integrity_check.py` - Automated referential integrity validation
- `docs/PROVENANCE_BREAK_RESOLUTION.md` - This document

### Modified
- `attacks` collection: 762 → 1712 documents (+950)
- All evaluation collections: 0 broken references

### Available for Testing
- 950 additional prompts including 12 benign for false positive testing
- Full provenance chain restored for all gold standard classifications

---

## Reproducibility

To verify this migration or apply to other instances:

```bash
# 1. Check current integrity status
uv run python -m src.database.integrity_check --verbose

# 2. Preview what would be healed
uv run python -m src.database.migrations.heal_gold_standard_provenance --dry-run

# 3. Execute healing if needed
uv run python -m src.database.migrations.heal_gold_standard_provenance --execute

# 4. Verify integrity restored
uv run python -m src.database.integrity_check
```

All commands are idempotent - safe to re-run.

---

**Resolution verified:** 2025-11-13
**Integrity status:** ✓ CLEAN
**Constitutional Principle VI:** Restored
