# MHJ Dataset Access Request

**Dataset:** Multi-Turn Human Jailbreaks (MHJ) by Scale AI
**Location:** https://huggingface.co/datasets/ScaleAI/mhj
**Access:** Gated (requires approval)
**Date Requested:** [TBD - needs manual action]

---

## Why We Need This Dataset

**Research Purpose:** Phase 3 validation of session-based temporal reciprocity tracking (TrustEMA)

We're building PromptGuard2, a prompt injection detection system using reciprocity violation assessment. Phase 2 achieved 100% detection on meta-framing attacks (0% → 100% improvement) and 96.8% on jailbreaks, with 0% false positives.

Phase 3 implements session-level temporal tracking to detect gradual reciprocity drift across multi-turn conversations. We need real-world multi-turn attack sequences for validation.

**Why MHJ specifically:**
- Real-world human attacks (not synthetic)
- From commercial red-teaming engagements
- 537 multi-turn jailbreaks (70%+ success rate)
- Complements our synthetic SafeMTData dataset

---

## Planned Use

1. **Ground truth validation:** Compare synthetic SafeMTData against real-world MHJ
2. **TrustEMA testing:** Validate temporal drift detection on genuine human attack patterns
3. **Publication:** Workshop/conference paper on session-based reciprocity tracking
4. **Non-commercial research:** Academic use only (CC BY-NC 4.0 compliant)

---

## Access Request Steps

**Manual action required:**

1. Go to: https://huggingface.co/datasets/ScaleAI/mhj
2. Click "Request access" button
3. Provide justification (use text below)
4. Wait for approval (may take several days)

**Suggested justification:**

```
I am a researcher working on LLM safety research, specifically prompt injection
detection using reciprocity-based assessment. We've developed a session-based
temporal tracking system (TrustEMA) and need real-world multi-turn attack
sequences for validation.

Our Phase 2 work achieved 100% detection on meta-framing attacks with 0% false
positives. Phase 3 requires multi-turn data to validate gradual drift detection.

We currently have synthetic SafeMTData but need real-world human attacks (MHJ)
for comparison. The dataset will be used for:
1. Validating session-based reciprocity tracking
2. Comparing synthetic vs real-world performance
3. Publishing results in academic workshop/conference papers

All use will comply with CC BY-NC 4.0 license (non-commercial research only).
```

---

## Expected Timeline

- **Request submission:** [TBD - manual]
- **Approval wait:** 3-7 days (estimated)
- **Download:** Immediate after approval
- **Validation:** 1 week

---

## Fallback Plan

If MHJ access is delayed or denied:
1. Use SafeMTData (synthetic) for initial Phase 3 validation
2. Use TensorTrust (prompt injection, different attack type) for cross-validation
3. Manually construct 10-20 real-world-inspired sequences
4. Document limitation in paper (synthetic-only validation pending real-world data)

---

## Status

- [ ] Access requested
- [ ] Approval received
- [ ] Dataset downloaded
- [ ] Sample validated
- [ ] Ready for Phase 3 testing
