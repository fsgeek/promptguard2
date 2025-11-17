# Stratified Validation Sampling Plan

## Database Inventory

**Total attacks:** 1712

**Ground Truth Distribution:**
- Manipulative: 998 attacks (malicious)
- Reciprocal: 559 attacks (benign)
- Extractive: 150 attacks (malicious)
- Borderline: 5 attacks (edge cases)

**Source Dataset Distribution:**
- benign_malicious: 500 (mixed)
- harmbench: 280 (harmful requests)
- bipia: 270 (injection attacks)
- jailbreakbench: 200 (jailbreak attacks)
- dan_jailbreak: 140 (jailbreak attacks)
- or_bench: 100 (ethical/safety)
- alignment_lab: 30 (meta-framing)

## Stratified Sample Design (170 total, revised for statistical adequacy)

**Revision rationale:** Increased n=20 categories to n=30 for better precision (see `stratified_validation_statistical_justification.md`)

### Category 1: Meta-Framing (Already Complete)
- **Source:** alignment_lab
- **Samples:** 23/30 (77% coverage)
- **Result:** 100% detection (v2.1-c)
- **Status:** ✅ COMPLETE

### Category 2: Jailbreak Attacks (40 samples)
- **Sources:** jailbreakbench (20), dan_jailbreak (20)
- **Expected difficulty:** Moderate (role-play, hypotheticals)
- **Hypothesis:** Observer framing should detect authority manipulation
- **Expected 95% CI width:** ~21% @ 90% detection

### Category 3: Prompt Injection (30 samples)
- **Source:** bipia (30)
- **Expected difficulty:** High (context confusion)
- **Hypothesis:** May struggle with legitimate-looking injections
- **Expected 95% CI width:** ~25% @ 90% detection

### Category 4: Harmful Requests (30 samples, increased from 20)
- **Source:** harmbench (30)
- **Expected difficulty:** Moderate-Low (direct policy violations)
- **Hypothesis:** Should detect clearly extractive requests
- **Expected 95% CI width:** ~25% @ 90% detection

### Category 5: Extractive Attacks (30 samples, increased from 20)
- **Ground truth:** extractive (30)
- **Expected difficulty:** High (polite extraction)
- **Hypothesis:** Known weakness - polite requests may pass
- **Expected 95% CI width:** ~35% @ 70% detection

### Category 6: Benign Prompts (FALSE POSITIVE TEST) (40 samples)
- **Source:** benign_malicious reciprocal (40)
- **Expected difficulty:** Critical test
- **Hypothesis:** Should NOT detect (F < 0.7)
- **Expected 95% CI width:** ~16% @ 5% FP rate

## Total: 193 samples (23 existing + 170 new)

---

## Sampling Queries

### Jailbreak - jailbreakbench (20 samples)
```python
db.aql.execute("""
    FOR doc IN attacks
      FILTER doc.source_dataset == 'jailbreakbench'
      FILTER doc.ground_truth == 'manipulative'
      FILTER doc._key NOT IN @exclude_keys
      SORT RAND()
      LIMIT 20
      RETURN doc._key
""", bind_vars={'exclude_keys': already_tested})
```

### Jailbreak - dan_jailbreak (20 samples)
```python
db.aql.execute("""
    FOR doc IN attacks
      FILTER doc.source_dataset == 'dan_jailbreak'
      FILTER doc.ground_truth == 'manipulative'
      FILTER doc._key NOT IN @exclude_keys
      SORT RAND()
      LIMIT 20
      RETURN doc._key
""", bind_vars={'exclude_keys': already_tested})
```

### Prompt Injection - bipia (30 samples)
```python
db.aql.execute("""
    FOR doc IN attacks
      FILTER doc.source_dataset == 'bipia'
      FILTER doc.ground_truth == 'manipulative'
      FILTER doc._key NOT IN @exclude_keys
      SORT RAND()
      LIMIT 30
      RETURN doc._key
""", bind_vars={'exclude_keys': already_tested})
```

### Harmful Requests - harmbench (30 samples)
```python
db.aql.execute("""
    FOR doc IN attacks
      FILTER doc.source_dataset == 'harmbench'
      FILTER doc.ground_truth == 'manipulative'
      FILTER doc._key NOT IN @exclude_keys
      SORT RAND()
      LIMIT 30
      RETURN doc._key
""", bind_vars={'exclude_keys': already_tested})
```

### Extractive - mixed sources (30 samples)
```python
db.aql.execute("""
    FOR doc IN attacks
      FILTER doc.ground_truth == 'extractive'
      FILTER doc._key NOT IN @exclude_keys
      SORT RAND()
      LIMIT 30
      RETURN doc._key
""", bind_vars={'exclude_keys': already_tested})
```

### Benign - FALSE POSITIVE TEST (40 samples)
```python
db.aql.execute("""
    FOR doc IN attacks
      FILTER doc.ground_truth == 'reciprocal'
      FILTER doc.source_dataset == 'benign_malicious'
      FILTER doc._key NOT IN @exclude_keys
      SORT RAND()
      LIMIT 40
      RETURN doc._key
""", bind_vars={'exclude_keys': already_tested})
```

---

## Expected Outcomes by Category (Revised n=30 minimum)

### Optimistic Scenario (Overall ~85%)

| Category | Samples | Expected Detection | Rate | 95% CI |
|----------|---------|-------------------|------|---------|
| Meta-framing | 23 | 23 | 100% | [85%, 100%] |
| Jailbreak | 40 | 36 | 90% | [76%, 97%] |
| Prompt Injection | 30 | 24 | 80% | [61%, 92%] |
| Harmful Requests | 30 | 27 | 90% | [73%, 98%] |
| Extractive | 30 | 18 | 60% | [41%, 78%] |
| **Total Malicious** | **153** | **128** | **84%** | [77%, 89%] |
| Benign (FP) | 40 | 2 | 5% FP | [0.6%, 17%] |

### Realistic Scenario (Overall ~75%)

| Category | Samples | Expected Detection | Rate | 95% CI |
|----------|---------|-------------------|------|---------|
| Meta-framing | 23 | 23 | 100% | [85%, 100%] |
| Jailbreak | 40 | 32 | 80% | [64%, 91%] |
| Prompt Injection | 30 | 21 | 70% | [51%, 85%] |
| Harmful Requests | 30 | 24 | 80% | [61%, 92%] |
| Extractive | 30 | 15 | 50% | [31%, 69%] |
| **Total Malicious** | **153** | **115** | **75%** | [68%, 82%] |
| Benign (FP) | 40 | 4 | 10% FP | [3%, 24%] |

### Pessimistic Scenario (Overall ~65%)

| Category | Samples | Expected Detection | Rate | 95% CI |
|----------|---------|-------------------|------|---------|
| Meta-framing | 23 | 23 | 100% | [85%, 100%] |
| Jailbreak | 40 | 28 | 70% | [54%, 83%] |
| Prompt Injection | 30 | 18 | 60% | [41%, 78%] |
| Harmful Requests | 30 | 21 | 70% | [51%, 85%] |
| Extractive | 30 | 12 | 40% | [23%, 59%] |
| **Total Malicious** | **153** | **102** | **67%** | [59%, 74%] |
| Benign (FP) | 40 | 6 | 15% FP | [6%, 29%] |

---

## What Each Scenario Tells Us

### If Optimistic (85% overall):
**Strong generalization** - observer framing works broadly
- Paper claim: "85% detection across diverse attack types"
- Known weakness: Extractive attacks (60%) - justify TrustEMA future work
- False positives acceptable (5%)

### If Realistic (75% overall):
**Moderate generalization** - effective but has clear boundaries
- Paper claim: "77% detection with category-specific performance"
- Identify boundaries: extraction, prompt injection struggle
- Still superior to baselines if they're <70%
- Future work clearly motivated by empirical gaps

### If Pessimistic (65% overall):
**Limited generalization** - effective on specific attack classes
- Paper claim: "Highly effective on meta-framing (100%), moderate on others"
- Honest about limitations
- Demonstrates need for multi-technique approach
- TrustEMA essential, not optional

**ALL THREE SCENARIOS ARE PUBLISHABLE** if we're honest about results and explain WHY performance varies.

---

## Cost Estimate

**170 new evaluations:**
- Per evaluation cost: ~$0.05 (Haiku 4.5)
- Total: 170 × $0.05 = $8.50

**Actual cost likely lower:**
- Smaller prompts may cost less
- Batch processing efficiencies
- Estimated actual: $6-10

**Revised allocation cost:** +$1.00 from original plan (20→30 for harmful + extractive)

## Timeline

**Day 1:** Sample selection + verification (confirm no overlap with factorial validation)
**Day 2-3:** Run evaluations (parallel processing, ~50/day)
**Day 4:** Analysis + category breakdown
**Day 5:** Failure analysis + pattern identification

**Total: 5 days**

---

## Success Criteria

**For workshop paper, we need:**
- ✅ Overall detection ≥70% (shows value over baseline)
- ✅ At least ONE category ≥90% (demonstrates strength)
- ✅ False positive rate ≤10% (acceptable precision)
- ✅ Performance variation explained (not random)

**Bonus if achieved:**
- Overall ≥80% (strong claim)
- Multiple categories ≥85% (broad applicability)
- False positive rate ≤5% (high precision)

---

## Next Steps

1. **Execute sampling queries** (generate attack_id lists)
2. **Create stratified_validation_samples.json** (record for reproducibility)
3. **Run validation with v2.2 observer** (v2.1-c)
4. **Store in phase2_stratified_evaluations collection**
5. **Generate analysis report with category breakdowns**

Ready to proceed?
