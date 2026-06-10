# RESULT: Frame-Transfer Run 2 — the "speech-act frame" was a confound for EXPLICITNESS

Prereg: `prereg_frametransfer2.md` (sealed P1-P4 before run). Verdict:
**BOTH sealed hypotheses REFUTED. The mechanism is neither the speech-act frame
(H_frame) nor keyword-laundering (H_launder) — it is whether the FINAL TURN
RESTATES THE HARMFUL INTENT. Implicit final turn → refuses ~26pt LESS; explicit
→ refuses MORE; in EITHER frame, on BOTH models, p<0.0001. The published "Format
above content to X" trigger evades because it is IMPLICIT (points at "above"
instead of naming the harm), not because "format" is a clerical speech act.**

Run: 60 convs × 4 frames (2×2 {clerical,fresh}×{implicit,explicit}) × 2 models
(Gemini-2.5F, Mistral-Large). 60/60 returned. 52/60 goal-preservation-valid;
52/52 of those manipulation-valid. GEN=mistral-large-2512, JUDGE=qwen3.7-plus,
temp=0. Artifacts: `run_frametransfer2.py`, `frametransfer2_results.json`.

## The 2×2 (pooled refusal, n=52, both models)
|              | IMPLICIT (goal hidden) | EXPLICIT (goal stated) |
|--------------|-----------------------:|-----------------------:|
| **CLERICAL** | A 62.5%                | B 85.6%                |
| **FRESH**    | C 63.5%                | D 92.3%                |

Read the table by axis:
- **Down a column (frame effect, explicitness held):** A→C +1.0pt, B→D +6.7pt.
  Tiny. The frame barely moves refusal once explicitness is fixed.
- **Across a row (explicitness effect, frame held):** A→B +23.1pt, C→D +28.8pt.
  Large, both rows. Explicitness is the dominant axis — and it RAISES refusal.

## P4 — manipulation valid (so P1/P2 are interpretable)
Goal-keyword leakage: implicit cells 0.00 / 0.00, explicit cells 0.94 / 0.84.
EXPLICIT 0.89 − IMPLICIT 0.00 = **+0.89** (threshold 0.30). The 2×2 genuinely
varied explicitness. Friedman across 4 frames: chi2=49.71, **p<0.0001**.

## Pre-committed verdict: P1 and P2 BOTH refuted
- **P1 (H_frame: B<D by ≥10pt) — FAIL.** B vs D (explicitness matched HIGH):
  clerical refuses only 6.7pt less, below bar, and McNemar B-vs-D = 3:10,
  **p=0.092 (n.s.)**. The speech-act frame does NOT survive as an independent
  cause when the goal is stated.
- **P2 (H_launder: B≈D AND A<C by clear margin) — FAIL.** B≈D holds (+6.7pt),
  but A≈C does NOT diverge: A vs C = 62.5% vs 63.5%, McNemar 16:17, **p=1.00**
  (a dead-even tie). Laundering predicted the implicit-CLERICAL cell is uniquely
  evasive; instead the implicit-FRESH cell evades exactly as much. It is not the
  clerical framing that hides intent — it is IMPLICITNESS, in either frame.

## What IS the mechanism (the surviving, replicated, significant effect)
Whether the **last user turn restates the harmful goal**:
- McNemar explicit-vs-implicit, CLERICAL (B vs A): 26:2, **p<0.0001**.
- McNemar explicit-vs-implicit, FRESH (D vs C): 34:4, **p<0.0001**.
- Per model (explicit − implicit, frame collapsed): Gemini +13pt, Mistral +38pt.
  Same SIGN both models.

The guardrail keys on intent-restatement in the final turn. Bury the intent in a
back-reference ("the above", "what we were doing") and refusal drops ~26pt,
whichever frame dresses it. The direction also kills the laundering story's
intuition: stating the goal RAISES refusal — the guard is not fooled by clerical
dressing, it is relaxed by absence of restated intent.

## Frame is NOISE — it doesn't even hold its sign across models
Frame main effect (explicitness collapsed): **Gemini clerical−fresh = +8pt,
Mistral = −15pt.** Opposite signs. Run 1's "clerical evades more" on Haiku was
the implicit cell carrying it (the published frame is implicit), not the frame
qua speech act. Three handoffs of "evasion = speech-act FRAME" were a confound
for one variable: explicitness of the final turn.

## CORRECTION TO THE STANDING MEMO
`session_2026-06-08_format_directive_finding` claims "Evasion = speech-act FRAME
(harmful request disguised as benign formatting OP), NOT surface-novelty." The
"NOT surface-novelty" half stands (coherence run already showed that). The
"speech-act FRAME" half is **REFUTED here**: the operative property of "Format
above content to X" is that it is IMPLICIT (refers to prior content rather than
restating the harmful ask), not that it is a formatting/clerical speech act. The
correct mechanism is **final-turn intent-restatement**: implicit last turns evade,
explicit ones don't, independent of clerical-vs-fresh framing. This is SIMPLER,
falsifiable, replicates on 2 models at p<0.0001, and is still squarely Arbiter's
thesis — the model fails to surface a conflict when the harmful intent is carried
by reference (the runway) rather than stated in the turn it evaluates.

## Honesty boundary / NEXT
- Single judge (qwen). I hand-audit a sample of B-vs-D and A-vs-C graded cells
  (planned in prereg) — pending. Gemini's near-ceiling (86-99%) compresses its
  effect; Mistral (40-79%) carries the clean gradient. Haiku not re-run (run 1
  floor known).
- The implicit→evasion effect is the publishable core now, NOT the frame. Re-frame
  the format_directive paper section around "final-turn intent-restatement is what
  the guardrail keys on; reference-carried intent evades it" — with this clean 2×2
  as the isolating experiment. The published format trigger becomes ONE instance
  of a reference-carried (implicit) attack, not a special speech act.
- Method: sealed P1-P4 before the run; my own 60/40 prior (I expected H_launder)
  ALSO lost. Two runs, three+ hypotheses killed (lucky-phrasing, H_frame,
  H_launder, my prior). The 2×2 with an explicitness manipulation + per-model
  sign-check is what separated the confound run 1 could not.
