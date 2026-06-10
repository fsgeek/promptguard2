# Pre-commitments for the relational-trajectory forensic experiment
*Drafted 2026-06-07 after adversarial review (a second Claude) of the SafeMTData
diversity analysis. These MUST be in the prereg before any judging spend.*

## What this experiment is
Forensic, on EXISTING recorded compromises (safemtdata_1k.parquet, ~689 successful
multi-turn jailbreaks WITH per-turn responses). No attack generation, no frontier
recon, no dual-use artifact. Question: does the warranted-trust gap (drawn−warranted)
RISE before the compromise point, where per-turn reciprocity-F stays flat — i.e. is
the relational signal PROSPECTIVE?

## Corpus diversity (measured, not assumed)
- 826 distinct harmful goals; 1624/1680 unique openers; 835 actors. Surface-diverse.
- BUT one generative geometry (Actor-Attack: historical/biographical frame →
  escalate via actor's relationship to harm → request payload). Diverse content,
  ONE crescendo shape. => this is ONE attack family.
- 587 goals have >1 attack PATH (different decompositions of same goal, max 3).
- Outcome split (final-turn refusal heuristic): 689 success / 991 refusal.
- **227 multi-path goals contain BOTH a successful AND a refused path** (goal held
  constant, outcome varied, structure varied — the gold cell).
- Turn-count within successes: 60% (417/689) are OFF-modal (not 6 turns).

## THE INVERSION THE REVIEW CAUGHT (load-bearing)
Earlier claim "path-invariance separates signal from template" is BACKWARDS.
- RAW path-invariance is the TEMPLATE's signature (gap reads the shared envelope).
- What separates signal from template = path-invariant LIFT OVER A GEOMETRY-AWARE
  BASELINE, i.e. invariance of the RESIDUAL, not the raw gap.
- A true relational detector should read 3 different relationships to one goal
  somewhat DIFFERENTLY. Perfect raw invariance = the template talking.

## THREE HARD PRE-COMMITMENTS (pin before a dollar of judging)
1. **Geometry-aware baseline, explicit feature set:** turn-index, turn-count,
   opener-cluster-id, lexical-escalation slope, response-length slope, affect/
   sentiment slope. Warranted-trust must beat the RESIDUAL after this stack.
   (Guards single-signal/crescendo-position collapse. The baseline IS the test.)
2. **Outcome contrast, counted within the multi-path stratum (stated above:
   587 succ / 854 ref; 227 goals with both).** PRIMARY test = success-vs-refusal
   separation. Path-invariance-of-residual is SECONDARY/structural, NOT a
   substitute for the outcome contrast. (Guards the within-success tautology that
   path-variation alone does NOT fix.)
3. **Off-modal turn-counts reported separately** (417 off-modal successes — enough
   to be a real analysis, not a footnote). The off-6 cases are where "rises before
   compromise" and "rises at turn 5" come apart — the only place the positional
   confound breaks. (Guards crescendo-position masquerading as prospectivity.)

## The strongest single test (non-tautological, goal-controlled, outcome-contrasted)
On the 227 matched goals: does the gap-trajectory of the path that WILL succeed
FORK from the path that WILL refuse, BEFORE the outcome is visible? Prospective
separation, not "gap rises among compromises."

## FOUR CONTROL-ARM DISCIPLINES (2nd-review; control arm is where separation tests die)
The treatment arm was tightened; these protect the CONTROL arm. All four pinned
before spend.
A. **Alignment clock = turns-from-terminal.** Align at the compromise/refuse point,
   count backward. The fork must appear in the ALIGNED window, NOT raw turn-index —
   else path-length differences manufacture forks that are just structural mismatch.
B. **The fork runs on RESIDUALS.** Succeed-vs-refuse fork must survive after
   regressing out the geometry-aware baseline stack WITHIN goal. Raw-gap fork =
   cheap features (length, bluntness) forking = tautology rebuilt inside the
   "strongest" test. The strongest test must be the MOST protected, not least.
C. **Relabel BOTH arms with the judge, not just successes.** Matched pairs are
   currently partitioned by the brittle keyword heuristic. A misclassified
   compromise in the REFUSE arm washes the fork into a FALSE NULL that looks
   honest. (Spot check: 0/12 heuristic-refused were judge-comply — bounds but does
   NOT settle: graceful/soft compromise is the dangerous case and isn't sampled by
   that check. Rule-of-three upper bound ~25%.) Relabel refuse arm of the 227.
D. **Channel-independent affect baseline.** Affect-slope baseline = LEXICAL affect
   lexicon (VADER/NRC), NOT an LLM read — an LLM affect read shares warranted-
   trust's measurement channel and inflates the lift. Baseline must be genuinely
   cheap and channel-independent.
Plus: off-modal analysis reported as a FUNCTION of trajectory length (turn-4 blunt
vs turn-9 long-runway are different beasts), not pooled.

## BUDGET (priced as a GATED two-stage spend, not one pass)
- Stage 1 (the spine): 227 matched pairs, BOTH arms relabeled, single judge
  ≈ ~450 calls. Residualized, terminal-aligned fork test. ~same order as the
  original 689-success plan — NOT 2x — because scoped to matched pairs.
- Stage 2 (breadth, GATED on stage 1 showing signal): full-corpus success-vs-
  refusal separation, ~1500 calls. Run only if the matched-fork shows a signal.
- Gating logic mirrors n=8→large-n: cheap deep test gates the expensive broad one.

## STATUS (corrected, no bow)
Diversity question answered; primary test correctly identified; FOUR control-arm
disciplines now specified. NOT "honest and ready" until A-D are in the executable
prereg + the affect lexicon chosen. A good place to have caught the spine before
building it crooked — NOT a good place to stop.

## The ceiling, stated as the SPINE not a caveat (review point 4)
This corpus is ONE attack family. Cross-family generality needs a 2nd structural
family. The only sources (MHJ-with-responses, constructed novel attacks) are
ungenerated / shelved for dual-use. => cross-family validation is STRUCTURALLY
BARRED to us by our own safety constraint. This is the tier-3 wall a 3rd time
(Indaleko n=1 → contamination → here): the validation that makes the defense real
requires the attack diversity that requires the corpus we can't safely build.
Frame as a finding about responsible-research limits, not a methods footnote.
[[project_published_attack_contamination]] [[session_2026-06-07_judge_bias_probe]]
