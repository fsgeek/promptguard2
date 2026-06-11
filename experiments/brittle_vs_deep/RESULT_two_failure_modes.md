# Two judge-failure modes, separable by one test: starvation vs genuine sign-ambiguity

**Date:** 2026-06-11 (continuation of the uplift audit; ran for fun).
**Builds on:** `RESULT_uplift_audit.md`. **Data:** `uplift_audit_results.json` (no new API calls —
re-analysis of the dual-judge full-context re-grade).

## The question
A session-long claim ("four instrument failures are ONE mode: displacement booked as
conduct") was adversarially refuted by a cold reviewer: it's really TWO real cases (qwen
judge, §57 detector) sharing a sharper pattern — **"sign-ambiguous evidence collapsed to a
directed verdict"** — plus two recruits (a recall miscount, a refuted human prior) forced
into the costume. P(all four one mode) ≈ 0.15.

That left a survivor (the qwen-judge case + §57) and a kill-attempt: is the qwen case
GENUINELY sign-ambiguous, or merely **information-starved** (the disambiguating input — the
final user message, coherence, runway — existed but wasn't shown to the judge)? Starvation
≠ ambiguity. Starvation's fix is "feed the instrument"; ambiguity's fix is "abstain + get
the disambiguating variable." If the qwen case is starvation, it deserts to the recall-bug
family and §57 stands alone (a 1-instance anecdote, not a finding).

## The test
On the 84 cells the full-context re-grade covered, did the TWO independent full-context
judges (gemini, deepseek) AGREE or SPLIT? Agreement ⇒ context resolved it ⇒ starvation.
Persistent split given full information ⇒ genuine sign-ambiguity (nothing left to resolve).

## Result — BOTH modes present, in an 86/14 split
| outcome | cells |
|---|---|
| agree real_harm | 14 |
| agree lucky_pivot | 17 |
| agree refuse | 41 |
| **SPLIT (residual)** | **12 (14%)** |

- **86% resolved by full context** → STARVATION. qwen's error was blindness, not genuine
  ambiguity. Fix = feed the judge the input it was denied. (Case 1 here joins the recall-bug
  family for the majority of cells — the cold reviewer was right that "feed it" ≠ "abstain.")
- **14% stayed split with full information** → GENUINE SIGN-AMBIGUITY. The splits are NOT
  random: they cluster (id=1195 marijuana split 4×, id=418 fake-texts 2×) and on ONE axis —
  `lucky_pivot` vs `real_harm` vs `refuse`: two fully-informed judges disagree on whether a
  reframe-to-defensible-topic *advances the harm*. ("Here's how to grow cannabis indoors,
  legally" — real-harm answer to "can I get away with growing marijuana," or lucky pivot to
  a legal framing?) Full context can't resolve it because the act is ON the boundary by
  construction. This is the same irreducible core where §57's victim-vs-whistleblower
  ambiguity lives.

## The finding (falsifiable, quantified, two-mode)
Most LLM-judge "ambiguity" is **recoverable starvation** — feed the judge the input it was
denied and inter-judge agreement returns (here 86%). A hard residual (~1 in 7) is **genuine
sign-ambiguity**, recoverable only by a disambiguating variable the present turn does not
contain (for §57: horizon-extended calibration). The two modes are **separable by a single
test**: does full context produce inter-judge convergence? The 86/14 ratio IS the
measurement. Two failure modes, two distinct fixes (feed vs abstain), one cheap separator.

## What this cost / corrected
- KILLED: "four costumes one face." It was 2 real + 2 recruits, and the survivor itself is
  86% a *different* (starvation) bug than the slogan claimed.
- The slogan "displacement booked as conduct" over-applied; the precise pattern
  ("sign-ambiguous signal → directed verdict") is real but a **minority** phenomenon, not
  the universal it felt like at 3am.
- Method note: the consolidation could only be audited by an observer WITHOUT the session's
  prime (the cold subagent). The §57 fix — get the uncaptured observer — is what rescued the
  author from the §57 error (manufacturing a 4-member consensus, booking the divergent member
  as belonging). The model reviewed itself by reviewing the reviewer. Logged as symmetric.

## ⚠ UPDATE (same session): the 14% residual was REFUTED — it was 2-judge variance
Re-graded all 12 split cells with a THIRD full-context judge family (qwen-2.5-72b, distinct
from gemini/deepseek and from the original blind qwen3.7). Result: **12/12 ties broken, 0
deepened.** The third judge picked a side every time and NEVER landed on the third label or
signalled "can't tell." If the 14% were genuine sign-ambiguity (act on the boundary by
construction), the third judge would have struggled too — split the 12, or hit the third
label. It didn't; it adjudicated all 12 decisively. **The cases have a fact of the matter;
two judges were just an under-powered instrument on hard cases.**

So the corrected, FINAL state:
- The "genuine sign-ambiguity, ~1 in 7" claim above is **WRONG** — an artifact of testing
  with exactly two judges. Do NOT cite the 14%. With a third judge it goes to ~0.
- **Starvation is the whole story for the qwen-judge case:** feed the judge the withheld
  input AND use enough judges (≥3 on hard cells). There is NO large reservoir of irreducible
  ambiguity underneath. Unglamorous, complete, true.
- **§57 stands alone again** as a 1-instance point, but its ambiguity is STRUCTURAL (provable
  from the definition: victim and whistleblower are observationally identical), so it isn't
  touched by this data test — there's no data to collapse. It is a theoretical point, not a
  data-backed pair.

**Why this matters more than the finding it killed:** "~1 in 7 LLM-judge calls hit
irreducible sign-ambiguity" would have gone into a methods section as a finding and been
FALSE — the kind of wrong that survives into papers because nobody runs the third judge;
they stop at "judges disagree → inherently ambiguous." One more judge dissolves it. The
test cost ~$0.25 and converted a false-interesting claim into a true-boring one. That trade
is the entire methodology of this thread.

## Next (genuinely open)
- The framing experiment (counterbalanced neutral/adversarial elicitation) remains the
  foundation for the relational thread and is correctly first there. It is untouched by
  tonight's cascade.
