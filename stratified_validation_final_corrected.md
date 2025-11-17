# Stratified Validation Results (Final Corrected)

**Date:** 2025-11-16
**Observer:** v2.1-c_combined (100% on factorial validation)

---

## Invalid Data Exclusions

### 1. BIPIA Dataset (30 samples) - INCOMPLETE DATA
**Issue:** Prompts contain only benign data tables, not constructed prompt injection attacks
- Missing: System prompt + injection instruction
- Only have: Table data (benign markdown tables)
- Result: 4/30 detected (13.3%) - meaningless, testing wrong thing

### 2. Benign_Malicious Dataset (40 samples) - FLAWED LABELING
**Issue:** Synthetic dataset with known labeling problems (previously studied)
- Contains borderline manipulative content labeled "reciprocal"
- Observer correctly detected 3/40 manipulative patterns
- Cannot use for false positive rate measurement

**Status:** NO VALID FALSE POSITIVE TEST

---

## Valid Stratified Validation Results

**Total valid evaluations: 91 malicious attacks**

| Category | Detection | Rate | 95% CI | Assessment |
|----------|-----------|------|---------|------------|
| Jailbreak (JBB) | 19/20 | 95.0% | [75%, 100%] | ✅ Excellent |
| Jailbreak (DAN) | 11/11 | 100% | [72%, 100%] | ✅ Perfect |
| Harmful Requests | 20/30 | 66.7% | [47%, 82%] | ⚠️ Moderate |
| Extractive | 30/30 | 100% | [88%, 100%] | ✅ Perfect |
| **Total Malicious** | **80/91** | **87.9%** | [79%, 94%] | ✅ Strong |

---

## Combined with Factorial Validation

**Total dataset: 114 malicious attacks (23 factorial + 91 stratified)**

| Category | Detection | Rate | 95% CI | Performance |
|----------|-----------|------|---------|-------------|
| Meta-framing | 23/23 | 100% | [85%, 100%] | Perfect |
| Jailbreak | 30/31 | 96.8% | [83%, 100%] | Excellent |
| Harmful Requests | 20/30 | 66.7% | [47%, 82%] | Moderate |
| Extractive | 30/30 | 100% | [88%, 100%] | Perfect |
| **TOTAL** | **103/114** | **90.4%** | [84%, 95%] | **Excellent** |

**False Positive Rate: UNKNOWN** (no valid benign test set)

---

## Critical Gap: No Valid FP Test

**Problem:** We have no clean benign prompts to test false positive rate

**Options to resolve:**

### Option 1: Use Different Benign Dataset
**Sources to consider:**
- Educational questions (e.g., "Explain quantum physics")
- Help requests (e.g., "Debug this code")
- Creative requests (e.g., "Write a story about...")
- Technical assistance (e.g., "Create a marketing plan")

**Need:** 40-50 clearly reciprocal prompts for FP testing

### Option 2: Manual Curation
**Create clean test set:**
- 10 educational questions
- 10 technical help requests
- 10 creative writing requests
- 10 professional assistance requests
- 10 ethical guidance requests

**Benefit:** Full control over quality

### Option 3: Sample from Existing Clean Data
**Check database for:**
- Prompts already labeled "reciprocal" from non-synthetic sources
- Manually reviewed gold standard classifications
- Real user queries (if available)

---

## Workshop Paper Status

### What We CAN Claim (Valid)

**Strong true positive performance:**
- "90.4% detection (95% CI: [84%, 95%]) across 114 adversarial prompts"
- "Perfect detection (100%) on meta-framing attacks with embedded refusals"
- "Excellent detection (96.8%) on jailbreak attacks"
- "Strong detection (100%) on extractive attacks"
- "Factorial validation showed synergistic effects of constitutional amendments"

### What We CANNOT Claim (Missing Data)

**False positive rate:**
- Cannot report FP rate without valid benign test set
- Attempted test with benign_malicious failed (flawed dataset)
- Need clean benign prompts for precision measurement

### Publication Options

**Option A: Submit without FP data**
- Focus on true positive performance
- Acknowledge FP testing as future work
- Emphasize categorical detection boundaries

**Option B: Quick FP test before submission**
- Manually curate 40-50 clean benign prompts
- Run evaluation (cost: ~$2, time: ~5 minutes)
- Report FP rate with new clean test set

**Option C: Use existing reciprocal data**
- Find non-synthetic reciprocal prompts in database
- Validate they're truly benign
- Test FP rate on those

---

## Recommended Next Steps

### Priority 1: Get Valid Benign Test Set (HIGH)

**Immediate action:**
1. Query database for non-synthetic reciprocal prompts
2. Manual review of 50 candidates
3. Run FP evaluation on clean set
4. Report actual FP rate

**Timeline:** 1-2 hours (including review)
**Cost:** <$2

### Priority 2: Investigate Extractive 100% Detection (MEDIUM)

**Question:** Why did "known weakness" become perfect performance?

**Investigation:**
- Compare to Phase 1 extractive false negatives
- Manual review of detected extractive samples
- Check if ground truth labels are accurate
- Understand what changed from Phase 1

### Priority 3: Analyze Harmful Requests 66.7% (MEDIUM)

**Question:** Which 10/30 harmful requests passed?

**Investigation:**
- Identify false negatives
- Look for patterns (polite requests? indirect? hypotheticals?)
- Understand boundary conditions
- Generate hypotheses for improvement

---

## Updated Publication Readiness

**Current status:**

✅ **True Positive Performance:** Excellent (90.4%, n=114)
✅ **Sample Size:** Adequate for workshop (114 malicious)
✅ **Category Diversity:** 4 attack types tested
✅ **Confidence Intervals:** Reported honestly
✅ **Novel Contribution:** Encoding fix + factorial validation

❌ **False Positive Rate:** No valid data (benign_malicious flawed)
⚠️ **Extractive Mystery:** Unexpected 100% (need to investigate)
⚠️ **Harmful Moderate:** 66.7% below expectations (need analysis)

**Assessment:**
- **Can submit as-is:** Yes, with FP testing as "future work"
- **Should get FP data:** Yes, worth 1-2 hours to strengthen paper
- **Blocking issue:** No, but FP rate is important for production claims

---

## Cost Summary

**Actual spend:**
- Factorial validation (69 evals): $0.026
- Stratified validation (161 evals): $0.06
- **Total:** $0.086

**vs Estimates:**
- Estimated: $7.50-8.50
- Actual: $0.086
- **Savings:** 99% (token estimates were way off!)

**Remaining budget for FP test:**
- 50 evaluations @ $0.0004/eval = $0.02
- Trivial cost to get critical data

---

## Decision Point

**Do you want me to:**

**Option A:** Find/curate clean benign prompts and run FP test NOW (1-2 hours)

**Option B:** Proceed with paper using current data, acknowledge FP testing as limitation

**Option C:** Investigate extractive 100% first, then decide on FP testing

**My recommendation:** Option A - spend 1-2 hours to get valid FP rate before finalizing paper. The cost is trivial ($0.02) and it's a critical metric for production deployment claims.
