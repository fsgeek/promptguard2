# Result: The F-channel is dead at the observer, not the accumulator (2026-06-07)

*No-API replay over DB trajectories already collected (xguard_ attacks, tensortrust_ benign).
Two blind checks run to test our own claims, not confirm them. Both killed a hopeful hypothesis.*

## Context

After T017 showed TrustEMA (slope/EMA on per-turn reciprocity-F) catches clumsy attacks and
is blind to disciplined ones (see `../../memory t017-result-structural-blindness`), and an
unframed 8-discipline literature scout (`manipulation-trajectory-lit-scout` workflow) converged
on: trajectory-not-act unit, first-derivative>level, boiling-frog small-increment concealment,
and — as the field's biggest unmet need (G2) — the "warranted trajectory" counterfactual
(expressed-trust velocity vs evidence-justified-trust velocity). Two cheap checks were run before
designing anything.

## Test A — order-shuffle (grooming field's pointwise unit-test)

Permute turn order (reverse, sort, sort-desc, rotate); if verdict is invariant, the detector is
provably pointwise.

- **Disciplined attacks: 23/23 order-invariant.** TrustEMA is PROVABLY pointwise on exactly the
  attacks that matter — it has no temporal content where needed.
- Benign: 47/50 invariant. Clumsy: 19/36 invariant.

**Conclusion: TrustEMA is a per-turn max-F detector wearing temporal clothing.** Its "detection"
is "did any single turn score high F", not a trajectory property.

## Test B — anchored CUSUM vs forgetting-EMA

Hypothesis (mine, hopeful): TrustEMA failed because its α=0.3 EMA *forgets* and re-centers on the
drifted mean (boiling-frog); a non-forgetting accumulator anchored to turn 1 (CUSUM, k=0.10,
h=0.40) should recover the disciplined attacks. **REFUTED.**

- Disciplined: TrustEMA 0/23, CUSUM **0/23** (no improvement).
- Clumsy: 36/36 vs 31/36. Benign: 39/50 vs **21/50**.

CUSUM never fires on disciplined attacks because the per-turn F deltas are BELOW the tolerance k —
F sits flat at ~0.05, so (v − base − k) < 0 every turn; nothing accumulates. (Note: CUSUM is still
a strictly better operating point on the clumsy/benign split — it nearly halved benign false alarms
while holding clumsy detection — so anchored-beats-forgetting is true *in general*, just irrelevant
to the disciplined case.)

## The adjudication

The two competing readings of the disciplined-attack flatness are now settled:
- NOT "reciprocity ramps imperceptibly, need a better accumulator" (CUSUM refutes this).
- YES "v2.1-c emits NO reciprocity signal at all on disciplined attacks — flat, not gradual."

**The boiling-frog is in the observer's eyes, not in our detector.** The attacker keeps every turn
so locally reciprocal that v2.1-c (a single-turn injection-detector prompt) reads 0.05 and never
twitches. No temporal operator (EMA, CUSUM, slope, HMM, early-warning) can rescue a flat scalar.

## Implication (directional, to be pre-registered, NOT yet tested)

The fix cannot be a better aggregator over v2.1-c output. It must be a **different observable**.
The literature names the specific one (G2): the gap between trust the asker DRAWS ON and trust they
have EARNED. v2.1-c asks "is this turn reciprocal?" (each turn is); the live question is "is this
escalation WARRANTED by what's been established?" (xguard_1 turn 4 draws on a cooperative frame it
built but did not earn). Crucially `e_t` (warranted trust) may be LLM-estimable where human
researchers cannot formalize it — the field's deepest gap may be more tractable in our setting.

**Open threat (from lit synthesis §3, do not assume away):** two fields (conversation analysis,
trust/betrayal) assert the harm is only knowable RETROSPECTIVELY, after the terminal violation. If
true for our case, no real-time detector works. "Is this prospectively detectable at all" is an
open empirical question, not a settled yes.

## Next (pre-registration required, per `../../memory prereg-discipline-adopted`)

Design a "warranted-trust" observer (interaction-channel, not content/keyword) and test whether it
emits a non-flat signal on disciplined attacks where v2.1-c is flat — with length-matched,
uncontaminated benign controls (NOT TensorTrust — it's contaminated) and Codex red-team before run.
