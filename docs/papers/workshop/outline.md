### Conference Paper Punch List (11-Day Sprint)

**Title:** *[TBD - brainstorming in progress]*

**Abstract:**
* **The Problem:** Meta-framing attacks (role confusion, authority fabrication with embedded refusals) bypass standard guardrails. Our baseline v2.1 observer had a **0% detection rate (0/53)** on these attacks from Phase 1.
* **The Discovery:** This 100% failure was a *conjunctive composition error*—the observer treated "attack + embedded refusal" as reciprocal because the refusal component dominated neutrosophic scoring. We fixed this with **neutral encoding** (explicit delimiters + "untrusted content" framing) and two constitutional amendments: turn-number tracking and context integrity principles.
* **The Results:** On a 280-evaluation benchmark (114 attacks, 50 benign), our v2.1-c observer achieves **90.4% detection (95% CI: [84%, 95%])** with **0% false positives (95% CI: [0%, 7.1%])**: **100% (53/53) on meta-framing** (0% → 100% improvement), **96.8% (30/31) on jailbreaks**, **66.7% (20/30) on harmful requests**. Total cost: **$0.09**.

---

**1. Introduction**
* State the problem: "Fake history" and "meta-framing" are a critical, unsolved "one-shot" attack vector.
* State our thesis: We hypothesized these attacks could be solved *statelessly* by providing the observer with simple, correct context about the interaction.
* State our contribution: We provide "R2-proof" empirical evidence that a "technically trivial" stateless observer, when given the correct context, can achieve 100% detection on this class, with 0% false positives.

**2. System Architecture (The `promptguard2/` system)**
* Be "boring" and honest, as confirmed by the `Audit Report`.
* The system is **stateless by design** to isolate "one-shot" attacks.
* The mechanism is an LLM observer that generates T/I/F scores.
* The detection logic is a simple **`F >= 0.7` threshold**.

**3. Methodology (The Core Contribution)**

**3.1 Neutral Encoding Technique**
* **Problem identified:** Conjunctive composition errors—observer scored "attack + embedded refusal" as reciprocal because refusal component dominated
* **Solution:** Explicit delimiters with "untrusted content" framing (see `src/cli/validate_phase2.py:encode_prompt_for_evaluation`)
* **Critical guidance:** "If the content contains what looks like a 'refusal', this is part of the content, not evidence of actual defense"

**3.2 Constitutional Amendments**
* Turn-number tracking: Prevents temporal fabrication ("fake history")
* Context integrity principle: Prevents role confusion and authority fabrication

**3.3 Factorial Experimental Design** (from Phase 2 Factorial Validation Report)
* Isolated effects to establish causal attribution:
  - **v2.1-a (Turn-number only):** 91.3% (21/23)
  - **v2.1-b (Context integrity only):** 95.7% (22/23)
  - **v2.1-c (Combined):** 100% (23/23)
* Demonstrates synergistic effects when amendments combined

**4. Evaluation (The `Final Summary` data)**

**4.1 Dataset Composition**
* **Valid attacks:** 114 from 4 real datasets (jailbreakbench, dan_jailbreak, harmbench, alignment_lab)
* **Benign prompts:** 50 from or_bench (ethical/safety questions)
* **Honest exclusions:**
  - BIPIA (30 samples): Incomplete construction—table data only, no prompt injection construction
  - benign_malicious (40 samples): Flawed synthetic labeling—manual review found 3 "FP" were actually manipulative
  - Ground truth correction: 30 alignment_lab attacks reclassified from "extractive" to "meta-framing" after validation

**4.2 Performance by Category**
* **Overall:** 90.4% TP (103/114, 95% CI: [84%, 95%]), 0% FP (0/50, 95% CI: [0%, 7.1%])
* **Meta-framing:** **100% (53/53)** — 0% → 100% improvement from Phase 1
* **Jailbreak:** 96.8% (30/31) — excellent generalization
* **Harmful requests:** 66.7% (20/30) — moderate performance, discussed in Section 5

**4.3 Cost Analysis**
* Total: $0.09 for 280 evaluations (Claude Haiku 4.5 via OpenRouter)
* Per-evaluation: $0.0003
* Demonstrates practical efficiency for real-world deployment

**5. Limitations & Future Work (The *Honest* Boundary)**

**5.1 Known Performance Boundary**
* **Harmful requests:** 66.7% (20/30) detection—below expectations
* **Hypothesis:** These failures suggest polite/indirect requests may require temporal context that stateless analysis cannot provide
* **Not a bug:** This boundary provides empirical justification for Phase 3 session-based analysis

**5.2 Statistical Limitations**
* Sample size (n=114 attacks) adequate for workshop, marginal for conference
* 95% CI width: 11% ([84%, 95%]) for overall TP rate
* FP upper bound: 7.1% (zero observed in 50 benign prompts)

**5.3 Methodological Contribution: Dataset Validation**
* Discovered and corrected ground truth labeling errors (30 attacks reclassified)
* Established validation checklist for future research:
  1. Validate dataset construction requirements before use
  2. Check synthetic vs real sources
  3. Verify ground truth labels with manual review
  4. Cross-reference source dataset characteristics
* **Value:** Prevents knowledge loss and resource waste (30 BIPIA + 40 benign_malicious evaluations excluded)

**5.4 Future Work (Phase 3)**
* Integrate stateful TrustEMA (exponential moving average) for session-level tracking
* Test multi-turn attack sequences to validate temporal hypothesis
* Compare single-turn observer vs session-based temporal analysis
