# Statistical Justification for Stratified Validation Sample Sizes

**Question:** Are 20-40 samples per category sufficient for statistical validity?

**Short answer:** Yes for workshop paper with honest uncertainty reporting. No for strong point estimates.

---

## Confidence Interval Analysis by Sample Size

### For n=20 samples (Harmful Requests, Extractive)

| Detection Rate | 95% Confidence Interval | Width | Interpretation |
|---------------|------------------------|-------|----------------|
| 100% (20/20) | [83.2%, 100%] | 16.8% | True rate could be as low as 83% |
| 90% (18/20) | [68.3%, 98.8%] | 30.5% | Wide - limited precision |
| 80% (16/20) | [56.3%, 94.3%] | 38.0% | Very wide - weak claim |
| 70% (14/20) | [45.7%, 88.1%] | 42.4% | Extremely wide |
| 60% (12/20) | [36.1%, 80.9%] | 44.8% | Barely useful |

**Verdict on n=20:**
- ✅ Sufficient to claim "high detection (>80%)" if observed rate ≥90%
- ⚠️ Insufficient for precise estimates if rate is 70-80%
- ❌ Too small if trying to distinguish 70% from 80%

---

### For n=30 samples (Prompt Injection)

| Detection Rate | 95% Confidence Interval | Width | Interpretation |
|---------------|------------------------|-------|----------------|
| 100% (30/30) | [88.4%, 100%] | 11.6% | Much tighter than n=20 |
| 90% (27/30) | [73.5%, 97.9%] | 24.4% | Acceptable precision |
| 80% (24/30) | [61.4%, 92.3%] | 30.9% | Moderate precision |
| 70% (21/30) | [50.6%, 85.3%] | 34.7% | Useful for category comparison |

**Verdict on n=30:**
- ✅ Good for categories where we expect moderate performance (70-85%)
- ✅ Can distinguish "works well" from "struggles" categories
- ⚠️ Still not precise enough for exact point estimates

---

### For n=40 samples (Jailbreak, Benign FP Test)

| Detection Rate | 95% Confidence Interval | Width | Interpretation |
|---------------|------------------------|-------|----------------|
| 100% (40/40) | [91.2%, 100%] | 8.8% | Strong claim possible |
| 90% (36/40) | [76.3%, 97.2%] | 20.9% | Good precision |
| 80% (32/40) | [64.4%, 90.9%] | 26.5% | Acceptable precision |
| 70% (28/40) | [53.5%, 83.4%] | 29.9% | Useful for comparison |
| 5% FP (2/40) | [0.6%, 16.9%] | 16.3% | Adequate for FP claim |

**Verdict on n=40:**
- ✅ Good for primary claims (jailbreak as main category)
- ✅ Adequate for false positive testing (can claim <10% FP rate)
- ✅ Best precision of the three tiers

---

## Power Analysis: Can We Detect Differences?

**Research question:** Can we detect if performance varies across categories?

**Scenario:** Compare two categories (e.g., jailbreak vs extraction)

| Comparison | Sample Sizes | True Rates | Power to Detect |
|-----------|-------------|------------|-----------------|
| Jailbreak (n=40) vs Extraction (n=20) | 40 vs 20 | 85% vs 60% | ~75% power |
| Prompt Injection (n=30) vs Harmful (n=20) | 30 vs 20 | 75% vs 85% | ~40% power |
| Jailbreak (n=40) vs Prompt Inj (n=30) | 40 vs 30 | 85% vs 70% | ~60% power |

**Interpretation:**
- ✅ Can detect large differences (25+ percentage points) with moderate power
- ⚠️ Cannot reliably detect small differences (10 percentage points)
- ⚠️ Some comparisons underpowered

**What this means for publication:**
- Can claim "Category A performs better than Category B" if difference is ≥20%
- Cannot make strong claims about subtle performance differences
- Category-specific performance bands (e.g., "high: 85-95%", "moderate: 70-80%") more defensible than exact ranks

---

## Comparison to Field Standards

### Similar Security/ML Papers:

**Prompt injection detection papers:**
- Jain et al. (2023): 100-500 samples per attack type
- Perez & Ribeiro (2022): 50-100 samples stratified
- Liu et al. (2024): 200+ samples across categories

**Workshop papers (shorter venue):**
- Often 50-150 total samples
- Stratified designs common with 20-30 per category
- Emphasis on category-specific analysis vs overall accuracy

**Our proposal (173 samples, 20-40 per category):**
- ✅ Within workshop paper norms
- ⚠️ Below full conference paper standards
- ✅ Stratified design adds rigor

---

## Cost-Benefit Analysis

### Current Allocation: 150 new samples

| Category | n | Cost (est) | Marginal CI improvement from +10 samples |
|----------|---|-----------|----------------------------------------|
| Jailbreak | 40 | $2.00 | 90% CI: [76%, 97%] → [79%, 96%] (~3% width) |
| Prompt Injection | 30 | $1.50 | 80% CI: [61%, 92%] → [65%, 91%] (~4% width) |
| Harmful Requests | 20 | $1.00 | 80% CI: [56%, 94%] → [61%, 92%] (~5% width) |
| Extractive | 20 | $1.00 | 60% CI: [36%, 81%] → [41%, 78%] (~6% width) |
| Benign (FP) | 40 | $2.00 | - | - |

**Total cost: ~$7.50**

### Alternative: Increase to n=30 minimum per category

| Adjustment | Old n | New n | Additional Cost | CI Improvement |
|-----------|-------|-------|----------------|----------------|
| Harmful Requests | 20 | 30 | +$0.50 | ~8% width reduction |
| Extractive | 20 | 30 | +$0.50 | ~8% width reduction |

**New total: 170 samples, cost ~$8.50 (+$1.00)**

**Marginal benefit:** Modest improvement for extractive/harmful categories

---

## Statistical Adequacy Decision Matrix

### For Workshop Paper Publication:

| Requirement | Current Design (20-40) | Increased (30-40) | Ideal (50+) |
|------------|----------------------|------------------|-------------|
| Detect overall performance | ✅ YES (133 malicious) | ✅ YES | ✅ YES |
| Category-specific estimates | ⚠️ WIDE CIs | ✅ MODERATE | ✅ TIGHT |
| Compare across categories | ⚠️ LARGE DIFFS ONLY | ✅ MODERATE DIFFS | ✅ SMALL DIFFS |
| False positive rate | ✅ YES (n=40) | ✅ YES | ✅ YES |
| Honest uncertainty reporting | ✅ YES | ✅ YES | ✅ YES |
| Cost | ✅ $7.50 | ⚠️ $8.50 | ❌ $25+ |
| Timeline | ✅ 5 days | ✅ 5 days | ⚠️ 7-10 days |

---

## Revised Recommendation

### Option A: Keep Original Allocation (20-40 per category)

**Total: 150 new samples, 173 total**
**Cost: $7.50**

**Pros:**
- Adequate for workshop paper with honest CI reporting
- Can detect large performance differences across categories
- Cost-effective
- Fast execution (5 days)

**Cons:**
- Wide CIs for n=20 categories (harmful, extractive)
- Cannot distinguish subtle performance differences
- Reviewers may question small samples in some categories

**How to strengthen claims:**
- Report confidence intervals explicitly in all tables
- Group results by performance bands ("high: 85-95%") rather than exact percentages
- Emphasize category-specific patterns, not fine-grained rankings
- Clearly label as preliminary validation justifying future work

---

### Option B: Increase All Categories to n≥30 (RECOMMENDED)

**Adjustment:**
- Harmful Requests: 20 → 30 (+10)
- Extractive: 20 → 30 (+10)
- Total: 170 new samples, 193 total

**Cost: $8.50 (+$1.00)**

**Pros:**
- ✅ All categories have moderate precision (CI width ~25-35%)
- ✅ More defensible statistical rigor
- ✅ Can detect moderate differences (15-20%) across categories
- ✅ Addresses "why only 20?" reviewer question preemptively
- ✅ Minimal additional cost ($1.00)

**Cons:**
- Slightly longer execution (maybe 1 extra day)
- Still not "tight" CIs like n=50+

**Publication claims enabled:**
- "We evaluated 193 attacks across 6 categories (n=23-40 per category)"
- "Performance ranged from X% (95% CI: [a, b]) on Category A to Y% (95% CI: [c, d]) on Category B"
- "Observer framing achieved ≥80% detection on 4/5 malicious categories"
- "False positive rate: Z% (95% CI: [e, f], n=40 benign prompts)"

---

### Option C: Balanced Allocation (30-50 per category)

**Adjustment:**
- Jailbreak: 40 → 50
- Prompt Injection: 30 → 40
- Harmful: 20 → 30
- Extractive: 20 → 30
- Benign: 40 → 50
- Total: 200 new samples, 223 total

**Cost: $10-12**

**Pros:**
- Strong statistical rigor (CI widths <25%)
- Can detect smaller performance differences
- Addresses any sample size concerns
- Publication-grade evidence

**Cons:**
- Diminishing returns (marginal CI improvement ~5-8%)
- Higher cost
- Longer execution (6-7 days)

---

## Statistical Validity Verdict

**Are 20-40 samples per category "enough"?**

**For workshop paper:** YES with caveats
- Must report confidence intervals
- Must avoid overclaiming precision
- Must frame as "preliminary validation" if CIs are wide

**For conference paper:** MARGINAL
- n=20 categories too small
- n=30-40 acceptable with CI reporting
- n=50+ ideal

**For honest science:** YES
- All three scenarios (optimistic, realistic, pessimistic) are publishable
- Wide CIs are honest: "We estimate 70-90% detection"
- Category-specific analysis more valuable than overall precision

---

## Final Recommendation

**Execute Option B: Minimum n=30 per category**

**Rationale:**
1. **Statistical defensibility:** All categories have moderate precision
2. **Minimal additional cost:** $1.00 extra for 20 more samples
3. **Preempts reviewer criticism:** "Why only 20?" question answered
4. **Honest uncertainty:** CIs still wide enough to be realistic, not false precision
5. **Category comparison:** Can detect meaningful differences (15-20%)

**Revised Sample Allocation:**

| Category | n | Expected Detection | 95% CI Width (est) |
|----------|---|-------------------|-------------------|
| Meta-framing (existing) | 23 | 100% (23/23) | [85%, 100%] |
| Jailbreak | 40 | 80-90% | [76%, 97%] @ 90% |
| Prompt Injection | 30 | 70-80% | [61%, 92%] @ 80% |
| Harmful Requests | 30 | 80-90% | [71%, 96%] @ 90% |
| Extractive | 30 | 50-70% | [51%, 85%] @ 70% |
| Benign (FP) | 40 | 5-10% FP | [1%, 17%] @ 5% |

**Total: 193 samples (23 existing + 170 new)**
**Cost: $8.50**
**Timeline: 5-6 days**

---

## Honest Publication Claims with Option B

### What we CAN claim:

✅ "Observer framing achieved 100% detection on meta-framing attacks (23/23, 95% CI: [85%, 100%])"
✅ "Stratified validation across 193 attacks showed category-specific performance"
✅ "False positive rate: X% (n=40 benign prompts, 95% CI: [Y%, Z%])"
✅ "Performance ranged from 50-70% on extractive attacks to 100% on meta-framing"
✅ "Moderate-precision estimates identify boundary conditions for observer framing"

### What we CANNOT claim:

❌ "Overall detection rate: 83.5%" (too precise without reporting CI)
❌ "Statistically significant difference between jailbreak (85%) and harmful (87%)" (underpowered)
❌ "Definitive evaluation across all attack types" (sample sizes limit generalization)
❌ "No false positives" (CI goes to ~17% with n=40)

### What we SHOULD claim:

✅ "Preliminary validation showing promise with identified boundaries"
✅ "Category-specific performance guides future work"
✅ "Evidence of generalization beyond training distribution"
✅ "Honest assessment of where method works and where it struggles"

---

## Next Step

Update `stratified_validation_plan.md` with revised allocation (n≥30 all categories), then execute sampling queries.
