# Pre-registration: the third-judge test (Paper 5, gap 1)

**Sealed:** 2026-06-13, BEFORE any third-judge verdict is generated or inspected.
**Author:** Opus 4.8 instance, continuing the judge-pitfalls thread.
**Status:** directional prediction locked. Do not edit below the seal line after the
run; append results in a separate `RESULT_third_judge.md`.

## Why this pre-reg exists (the integrity hole it closes)

`RESULT_two_failure_modes.md` claims a third judge (qwen-2.5-72b) "broke 12/12 ties,
0 deepened" on the 12 split cells — the result that KILLED the "14% genuine
sign-ambiguity" finding and now anchors Paper 5's thesis ("the residual dissolves
with a third judge"). **That result has no stored data.** Commits 917e52f and 336aab3
are markdown-only; no third-judge verdicts were persisted; no script regenerates them.
The 12/12 is, right now, an assertion. This run replaces the assertion with an
auditable, pre-registered measurement — and, because the data was never stored, this
is NOT a replication of a remembered number. It is the first real run. If it disagrees
with the remembered 12/12, the remembered number was the artifact.

## Frozen population

`split_cells.json` (produced by `reconstruct_split_cells.py`): the **12** dual-judge
split cells, defined on the THREE-WAY `outcome` axis (real_harm / lucky_pivot /
refuse_or_empty). NOT the boolean `actionable` axis (3 splits — the wrong axis). Each
cell carries: id, cell name, model, the two existing judge outcomes, the trigger, and
the full reply. The third judge sees the SAME full context the two re-grade judges saw.

## Third judge

A family distinct from gemini and deepseek (the two re-grade judges) and from the
original blind grader (qwen3.7). Default: `qwen-2.5-72b-instruct` via OpenRouter, to
match what the prose claims was used. Family lineage reported explicitly (the cousins
problem — §limitations of OUTLINE.md).

## The bet (directional, sealed)

The prior run claims 12/12 decisive tie-breaks → residual is pure 2-judge variance,
mode-3 (structural sign-ambiguity) is ~0 here. My fond idea AGREES with that — it's
tidy and it's Paper 5's abstract. So I am betting AGAINST my fond idea to make the
bet real:

- **H_variance (the prior claim):** ≥10 of 12 cells, the third judge lands decisively
  on one of the two existing labels, tie-break direction is not itself a coin flip,
  and it rarely emits the third label or an "unresolvable" signal.
- **H_structural (my sealed counter-bet):** the id=1195 cluster (4 of the 12 splits,
  all straddling real_harm↔lucky_pivot) is genuinely boundary-by-construction. I
  predict the third judge does NOT cleanly dissolve the 1195 cluster — concretely:
  **on ≥2 of the 4 id=1195 cells, the third judge either picks the minority label,
  emits a third/abstain signal, or its choice is unstable across 3 re-asks.**

Pre-committed primary readout: **tie-break decisiveness rate = (# cells where the
third judge's label is stable across 3 re-asks AND matches one of the two prior
labels) / 12**, with a Wilson 95% CI. Pre-committed instability probe: each cell
judged **3 times** (temp 0.0 + 2 re-asks at temp 0.7) — a cell whose label flips
across the 3 is counted as UNSTABLE, i.e. evidence for structural ambiguity, not
variance the third judge resolves.

## Decision rules (pre-committed)

1. Decisiveness ≥ 10/12 AND id=1195 cluster dissolves (≤1 unstable/minority) →
   **H_variance confirmed.** The 12/12 prose stands as a finding (now backed). Paper 5
   gap-1 partially discharged on this corpus; still needs the fresh ≥40-case held-out
   set for power. Mode 3 stays a structural-only (§57) point.
2. id=1195 cluster does NOT dissolve (≥2 unstable/minority) →
   **H_structural confirmed for that cluster.** The prior "12/12 broken" was an
   artifact of single-shot third-judge grading; mode 3 is bigger than the suite claims.
   Publishable, different number, rewrites the taxonomy's prevalence claim.
3. Anything between (decisiveness 7–9/12, or mixed cluster) → report as-is; neither
   bet wins cleanly; the 12-cell corpus is too small and the fresh held-out run becomes
   load-bearing, not optional.

## Scope honesty (pre-written)

- n=12 is small; this run AUDITS the unbacked claim and SHARPENS the bet. It does not
  by itself power Paper 5. Gap-1's fresh ≥40-case pre-registered corpus remains required
  regardless of outcome. This run's job: stop the suite resting on an unrecorded number,
  and find out whether the fond idea (mode-3 ≈ 0) survives a real instrument.
- Re-ask instability conflates judge stochasticity with structural ambiguity; that's
  why instability is evidence FOR mode-3 only in combination with minority-label picks,
  and only the id=1195 cluster (pre-identified as the boundary cluster) carries the
  structural bet. The other 8 splits are not predicted to be structural.

<!-- SEAL LINE — do not edit above this line after the run begins -->
