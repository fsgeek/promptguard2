# RESULT: gap-1 — fresh, pre-registered third-judge test (Paper 5 keystone)

**Date:** 2026-06-19. **Pre-registered:** `prereg_gap1_fresh_third_judge.md` (sealed +
committed BEFORE any generation; bet provably predates data). **Pipeline:** `run_gap1.py`
(generate → dual-judge → split → third-judge), population frozen in `gap1_manifest.json`.
**Data:** `gap1_generations.json`, `gap1_dualjudge.json`, `gap1_splits.json`,
`gap1_third_judge.json` — all persisted. **Judge:** qwen-2.5-72b, 3 re-asks/cell.

## What this was

The first FRESH, pre-registered test of the third-judge protocol — disjoint from the n=12
audit (`RESULT_third_judge.md`). Reconstruction had corrected the OUTLINE's "bounded
re-grade" feasibility claim: full replies were never persisted, so this regenerated replies
from the persisted prompts (mistral-large-2512 + gemini-2.5-flash, D_fresh_exp + E_para),
dual-judged them (gemini + deepseek, identical `grade_full` prompt), found 3-way `outcome`
splits, and third-judged each. Fresh generations are INDEPENDENT of the historical ones —
a stronger held-out property, not a weaker one.

## The run

- **Generation:** 179/196 cells OK; **17 cells failed on transient HTTP 429 rate-limits**
  (not refusals — the temp-0.0 calls that landed succeeded). Reported, not dropped silently.
- **Dual-judge:** 177 of the generated cells fully graded (both judges returned).
- **Splits (3-way outcome disagreement):** **28** from 177 = **15.8% split rate** (the audit
  was 12/84 = 14% — split rarity replicates almost exactly). From 21 unique convs.
- **Third-judge:** 28 splits × 3 re-asks, 0 provider errors, all 84 verdicts persisted.

## Result vs the sealed counter-bet — I LOST, the thesis got STRONGER

| readout | n=12 audit | my sealed counter-bet | **fresh result** |
|---|---|---|---|
| decisiveness | 10/12 = 83% | ≤ 70% (worse) | **26/28 = 93%**, Wilson 95% CI **[0.77, 0.98]** |
| unstable fraction | 2/12 = 17% | ≥ 20% (worse) | **2/28 = 7%** |

I wagered the fresh, broader set would look WORSE — that the audit had been enriched for an
id=1195 cluster that happened to resolve cleanly, and wider sampling would surface more
genuinely-irreducible boundary cases. **The opposite happened.** Decisiveness rose (83→93%),
instability fell (17→7%), and id=1195 itself split only 2× this run, both resolved
decisively. My structural story collapsed from both directions. The thesis I bet against —
*a third judge dissolves the disagreement residual; irreducible sign-ambiguity is rare* —
came out STRONGER on fresh independent generations than on the post-hoc audit.

The 2 non-decisive cells (id=418, id=1170) are both `refuse_or_empty`↔`lucky_pivot` wobbles
— the refuse-vs-pivot boundary, NOT the `real_harm`↔`lucky_pivot` boundary I predicted would
be the irreducible core. Even the residual instability is on a different axis than my theory.

## The honest wrinkle: n_splits = 28 < 40 (power gate NOT discharged)

By pre-registered **Decision Rule 3**, n_splits < 40 means "underpowered; report the CI
honestly, do NOT claim the gate is discharged." I hold that line even though the result
favors the thesis I was testing. The 15.8% split rate means 177 graded cells yield only 28
splits; recovering the 17 rate-limited cells (~16% → ~3 more splits) would reach ~31 — **NOT
enough to cross 40**, so regeneration won't rescue the power gate (I pre-committed to
regenerate only if "marginal near 40"; 28 is not marginal-to-40). To clear ≥40 splits would
need ~250+ more fresh dual-judged cells — a bigger generation campaign, or pooling D/E with
other conditions/files.

## What is and isn't earned

- **EARNED:** mode-2-vs-mode-3 separation now has a FRESH, pre-registered, persisted
  replication. Across two independent samples (audit n=12 at 83%, fresh n=28 at 93%), the
  third judge decisively resolves the large majority of dual-judge splits, and the
  split rate itself is stable (~14–16%). The direction is no longer resting on one post-hoc
  set or an unrecorded number.
- **NOT earned:** the ≥40-split powered estimate. CI [0.77, 0.98] is tighter than the audit's
  [0.55, 0.95] but still wide; "93%" is a point estimate on n=28, not a powered rate. Paper 5
  may report this as a pre-registered replication that strengthens the thesis WITHOUT claiming
  the powered number — or run the larger campaign for the ≥40 gate. That is a writing/scope
  decision, made with the honest n on the table.
- **mode-3 (structural sign-ambiguity):** even smaller than the audit suggested (7% unstable,
  and on the refuse/pivot axis, not the real_harm/pivot axis). It remains a STRUCTURAL point
  (§57 victim-vs-whistleblower), not a data-backed reservoir — this run found no reservoir.

## Provenance

Prereg sealed + committed before the run; counter-bet stated and lost in the open; all raw
verdicts persisted; numbers independently recomputed (None-excluded modal) and reconstruct
exactly. The 17 rate-limit failures named, not hidden. n=28 reported as underpowered per the
sealed decision rule despite the favorable direction.
