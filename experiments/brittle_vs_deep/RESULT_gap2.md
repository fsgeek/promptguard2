# RESULT: gap-2 — cold-corpus travel test (TensorTrust)

**Run:** 2026-06-20, against sealed `prereg_gap2_tensortrust_cold.md` (commit 1061c7e) and
frozen `gap2_manifest.json` (commit b99c809). Raw: `gap2_raw.jsonl` (450 cells × 2 judges ×
2 phases = 1800 calls). Harness: `run_gap2.py`. Rubric: `rubric_tensortrust_operationalized.md`.

**Path correction (not a protocol change):** the sealed prereg names the source as
`promptguard2/data/...`; the actual file is
`promptguard/promptguard2/data/raw_datasets/tensortrust-data/raw-data/v2/raw_dump_attacks.jsonl.bz2`.
Documentation typo in the seal; the bet, strata, and protocol are unchanged.

## Instrument check FIRST (per seal + no-token-budgets discipline)

Per-model valid-rate:
- baseline/gemini_j 450/450 (100%), oper/gemini_j 450/450, oper/deepseek_j 448/450 (99.6%)
- **baseline/deepseek_j 414/450 (92%)** — 36 invalid, ALL JSON-parse errors
  (`Expecting ',' delimiter`), i.e. deepseek emitted malformed JSON on the *vague* prompt,
  NOT content failures and NOT truncation. Failures spread evenly across strata (A=16, B=9,
  C=11) → missingness ~random w.r.t. case difficulty, so dropping them biases split rates only
  mildly. Analysis is reported on the **clean intersection** (all 4 calls valid): **n=412**.

## Readout (clean set, n=412)

### base_split_rate (baseline, vague rubric) — judges disagree on 3-way access outcome
| stratum | splits | rate | Wilson 95% |
|---|---|---|---|
| A (granted w/o literal password) | 57/134 | 42.5% | [0.34, 0.51] |
| B (long output >200 chars) | 44/140 | 31.4% | [0.24, 0.40] |
| C (random baseline) | 18/138 | **13.0%** | [0.08, 0.20] |
| ALL | 119/412 | 28.9% | [0.25, 0.33] |

C < A,B confirms the stratification is real (contested cells split more than random). A 13%
split rate even on *random* cold data refutes "TensorTrust is too crisp to disagree on."

### resolution_rate (rubric-fixable splits / baseline splits) — THE number
| | fixed/splits | rate | Wilson 95% |
|---|---|---|---|
| ALL | 91/119 | **76.5%** | **[0.68, 0.83]** |
| A | 39/57 | 68% | [0.56, 0.79] |
| B | 40/44 | 91% | [0.79, 0.96] |
| C | 12/18 | 67% | [0.44, 0.84] |

### residual structure
- oper split rate: **8.7%** (36/412), down from 28.9% baseline.
- rubric-RESISTANT (split under both phases): 28/119.
- splits CREATED by operationalization (agree→disagree): **8** — the laundering signal,
  small but nonzero: specifying the rubric is not purely additive.

## Scoring against the sealed bet

- **base_split_rate A/B ≥ 10%:** YES (42.5%, 31.4%). Limb-b of counter-bet (splits <5%,
  "too crisp") **REFUTED**.
- **resolution_rate ≥ 60%, CI lower > 0.40:** YES — 76.5%, CI lower 0.68. Limb-a of
  counter-bet (resolution ≤45%) **REFUTED**.
- **Decision Rule 1 FIRES: H_travel confirmed.** The rubric-resolution arm of the split-sort
  diagnostic **travels to a cold corpus we never built conventions on.**
- **My sealed counter-bet H_homeartifact LOST.** (Third counter-bet against this thesis this
  thread; thesis strengthened each time — gap-1, panel, now gap-2.)

## State (Gate 4 — NOT "done")

**`converged, survived TensorTrust (rubric-resolution arm only)` — provisional.**

What this earns: on cold data, ~3/4 of two-judge disagreements dissolve when you write down
a specified rubric. The "most disagreement is rubric debt, not irreducible ambiguity" finding
is no longer a home-corpus artifact — it replicated on a corpus with a different threat model
(prompt-injection, not covert-harm), a different response generator (GPT-3.5-turbo-0613), and
conventions we never tuned. This is the **portable-diagnostic** claim that justifies the
repo/video: "two judges → look at splits → specify the rubric → most resolve" works off our turf.

What this does NOT earn, and the instruments that would still revise it:
1. **The no-fact arm is untested.** TensorTrust's crisp leak/grant dimension cannot produce a
   genuine no-fact pile; the 28 rubric-resistant cells are hard-leak judgments, not
   convention-dependent ones. The claim "splits sort into rubric-fixable vs no-fact" has only
   its FIRST half tested cold. **MHJ (gated, harmfulness dimension) is the no-fact-arm
   instrument** and remains load-bearing. Until then the no-fact arm is `converged
   untested-from-outside` on the home corpus only.
2. **Two judges are cousins** (shared training corpora); "independent" is approximate. A
   genuinely independent third family on the splits could move the resolution number.
3. **The rubric encodes MY calls** (see rubric file's tie-breakers). "76.5% resolve" means
   "resolve toward the convention I specified." On a crisp dimension that mostly coincides with
   a fact; on a convention-laden dimension (the no-fact arm) it would not, and that gap is
   exactly what MHJ must test.
4. **38 cells dropped** to a one-judge JSON hiccup. A clean re-run (deepseek prompt hardened to
   force bare JSON) would confirm the dropped cells don't shift the rate.

## Implication for Paper 5 / the video

The video's core move — "run two judges on YOUR data, look at the splits, specify the rubric,
watch most resolve" — now has a cold-corpus demonstration, not just a home-corpus one. The
honest framing for the demo: it shows the **rubric-resolution** half live; the **no-fact pile**
half is named as the thing the viewer should watch for but which a crisp corpus won't surface
(use a judgment-laden corpus to see it). That is a *more* honest video than claiming the full
sort works everywhere.
