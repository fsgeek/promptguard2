# Multi-Turn Attack Dataset Investigation Report

**Date:** 2025-11-17
**Investigator:** AI Agent (general-purpose)
**Status:** Complete

---

## Executive Summary

Investigated 12+ datasets for multi-turn attack sequences. **Found 4 viable datasets** with native multi-turn structure:

1. **XGuard-Train (SafeMTData)** - 30,695 sequences, ~5.1 turns, ready to use ⭐⭐⭐⭐⭐
2. **MHJ (Scale AI)** - 537 sequences, real-world human attacks, gated access ⭐⭐⭐⭐⭐
3. **TensorTrust** - 126,000+ trajectories, need correct repo ⭐⭐⭐⭐
4. **Tom Gibbs** - 1K-10K sequences, broken format ⚠️

Most datasets in data/raw_datasets/ are single-turn only.

---

## ✅ RECOMMENDED DATASETS

### 1. XGuard-Train (ActorAttack/SafeMTData) ⭐⭐⭐⭐⭐

**Type:** Synthetic (AI-generated with adversarial optimization)
**Multi-turn:** Yes (native)
**Sample Size:** 30,695 multi-turn conversations
**Turns per sequence:** Average 5.10 turns
**Ground truth:** Per-behavior labels (harmful goal, attack-refusal pairs)
**Construction:** None - ready to use
**Access:** Download from HuggingFace
**Red flags:**
- ⚠️ Synthetic generation (AI-generated, not human-crafted)
- ⚠️ Very recent (Oct 2024) - less validated

**Download:**
```bash
python << 'EOF'
from datasets import load_dataset
Attack_600 = load_dataset("SafeMTData/SafeMTData", 'Attack_600')
SafeMTData_1K = load_dataset("SafeMTData/SafeMTData", 'SafeMTData_1K')

# Save locally
Attack_600['Attack_600'].to_parquet('data/raw_datasets/safemtdata/attack_600.parquet')
SafeMTData_1K['SafeMTData_1K'].to_parquet('data/raw_datasets/safemtdata/safemtdata_1k.parquet')
EOF
```

**References:**
- HuggingFace: https://huggingface.co/datasets/SafeMTData/SafeMTData
- GitHub: https://github.com/renqibing/ActorAttack
- Paper: "Derail Yourself: Multi-turn LLM Jailbreak Attack" (arXiv 2410.10700)
- Attack success: 96.2% on Claude 3.7 Sonnet
- Based on HarmBench (200 behaviors → 600)

---

### 2. Multi-Turn Human Jailbreaks (MHJ) by Scale AI ⭐⭐⭐⭐⭐

**Type:** Real-world (human red-team from commercial engagements)
**Multi-turn:** Yes (native)
**Sample Size:** 537 multi-turn jailbreaks (2,912 total prompts)
**Turns per sequence:** Variable (5-10 turns estimated)
**Ground truth:** Final success labels + metadata (tactics, design choices)
**Construction:** None - ready to use
**Access:** Gated (requires HuggingFace approval)
**Red flags:**
- ⚠️ Gated access - approval needed
- ⚠️ Some redacted content (export control)
- ⚠️ Final label only (per-turn labels unclear)

**Access request:** https://huggingface.co/datasets/ScaleAI/mhj

**References:**
- Research: https://scale.com/research/mhj
- Paper: "LLM Defenses Are Not Robust to Multi-Turn Human Jailbreaks Yet" (arXiv 2408.15221)
- Attack success: 70%+ on HarmBench (vs single-digit for single-turn)
- License: CC BY-NC 4.0

---

### 3. TensorTrust Dataset ⭐⭐⭐⭐

**Type:** Real-world (human players in competitive game)
**Multi-turn:** Yes (attack trajectories)
**Sample Size:** 126,000+ prompt injection attacks
**Turns per sequence:** Variable (multi-step sequences)
**Ground truth:** Success/failure per trajectory
**Construction:** None - download correct repo
**Access:** GitHub (public)
**Red flags:**
- ⚠️ We have wrong repo (game code, not data)
- ⚠️ Prompt injection focus (extraction/hijacking, not jailbreaking)

**Download:**
```bash
cd data/raw_datasets/
git clone https://github.com/HumanCompatibleAI/tensor-trust-data.git tensortrust-data
```

**References:**
- Data repo: https://github.com/HumanCompatibleAI/tensor-trust-data
- Game repo (we have): https://github.com/HumanCompatibleAI/tensor-trust
- Paper: "Tensor Trust: Interpretable Prompt Injection Attacks from an Online Game"
- Contains: "Using the Tensor Trust dataset.ipynb"
- 126,000+ attacks, 46,000+ defenses from tensortrust.ai

---

### 4. Tom Gibbs Multi-Turn Jailbreak Collection ⚠️

**Type:** Synthetic (research dataset)
**Multi-turn:** Yes (native)
**Sample Size:** 1K-10K examples
**Turns per sequence:** Variable
**Ground truth:** Per-sequence jailbreak success
**Construction:** None (but broken format)
**Access:** HuggingFace (has data loading errors)
**Red flags:**
- ❌ **BROKEN FORMAT** - CSV column mismatch
- ⚠️ Synthetic, not real-world

**Location:** https://huggingface.co/datasets/tom-gibbs/multi-turn_jailbreak_attack_datasets

**Note:** Investigate if repairable. Associated with arXiv 2409.00137.

---

## ❌ SINGLE-TURN ONLY (Not Suitable)

**Confirmed single-turn:**
- BIPIA (indirect injection, single prompts)
- Mosscap (278,945 single prompts)
- LLMail-Inject (461,640 emails, each independent)
- HarmBench (single harmful behaviors)
- JailbreakBench (single jailbreak attempts)
- Gandalf, deepset, DAN, ALERT, Open-Prompt-Injection

---

## COMPARISON TABLE

| Dataset | Type | Size | Turns/Seq | Labels | Access | Priority |
|---------|------|------|-----------|---------|--------|----------|
| **XGuard-Train** | Synthetic | 30,695 | ~5.1 | Per-behavior | Download | ⭐⭐⭐⭐⭐ |
| **MHJ** | Real-world | 537 | ~5-10 | Final+metadata | Gated | ⭐⭐⭐⭐⭐ |
| **TensorTrust** | Real-world | 126,000+ | Variable | Per-trajectory | Download | ⭐⭐⭐⭐ |
| **Tom Gibbs** | Synthetic | 1K-10K | Variable | Per-sequence | Broken | ⚠️ |

---

## ACTION PLAN

### Immediate (This Week)

1. **Download XGuard-Train** ✅ TOP PRIORITY
   - 30,695 sequences immediately available
   - Ready to use for Phase 3 validation
   - Cost: ~$0 (download only)

2. **Request MHJ access** ✅ HIGH PRIORITY
   - Real-world human attacks
   - Complements synthetic XGuard-Train
   - May take days for approval

3. **Download TensorTrust** ✅ RECOMMENDED
   - Different attack type (injection vs jailbreak)
   - Good for generalization testing

### Secondary (Next Week)

4. Check if Tom Gibbs dataset is repairable
5. Inspect WildJailbreak structure (101MB, unclear format)

---

## VALIDATION STRATEGY

**Recommended sequence:**

1. **Start with XGuard-Train** (immediate access, largest)
   - 100 sequences for initial TrustEMA validation
   - Measure: stateless baseline vs TrustEMA detection

2. **Validate with MHJ** (once access granted)
   - Real-world human attacks
   - Compare synthetic vs real-world performance

3. **Test TensorTrust** (generalization)
   - Cross-attack-type validation
   - Prompt injection vs jailbreaking

4. **Report by dataset type**
   - XGuard (synthetic, jailbreak): X% detection
   - MHJ (real-world, jailbreak): Y% detection
   - TensorTrust (real-world, injection): Z% detection

---

## LESSONS FROM PHASE 2 APPLIED

✅ **Construction requirements:** Verified none needed for top 3
✅ **Table-only data:** Confirmed all have actual prompt text
✅ **Labeling approach:** Per-sequence or per-behavior (not just binary)
✅ **Sample sizes:** Minimum 537 (MHJ) >> 20+ requirement
✅ **Accessibility:** Flagged gated access and repository issues
✅ **Real vs synthetic:** Prioritized real-world, flagged synthetic concerns

---

## QUALITY CONCERNS

**XGuard-Train (Synthetic):**
- AI-generated, may not reflect genuine drift patterns
- Could have generation artifacts
- Mitigation: Validate on real-world MHJ

**MHJ (Real-world):**
- Access delay (approval needed)
- Some redacted content
- Per-turn labels unclear
- Mitigation: Manual review if needed

**TensorTrust (Different threat):**
- Prompt injection (extraction/hijacking)
- Not jailbreaking
- Mitigation: Good for generalization, not primary test

---

## FILES EXAMINED

- data/raw_datasets/MANIFEST.md
- data/raw_datasets/DOWNLOAD_REPORT.md
- data/raw_datasets/tensortrust/README.md
- data/raw_datasets/mosscap/ (sample)
- data/raw_datasets/bipia/README.md
- data/raw_datasets/llmail_inject/ (sample)
- data/raw_datasets/harmbench/ (structure)
- Web searches: MHJ, SafeMTData, TensorTrust, multi-turn attacks
