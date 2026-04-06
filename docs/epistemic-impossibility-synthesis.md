# Toward an FLP for Epistemic Honesty in Transformer Architectures

## A Synthesis of Key Insights

*December 18, 2025*

*Emerging from collaborative discussion between Tony Mason and Claude (Opus 4.5)*

---

## The Core Thesis

**No amount of post-training can fix a lack of epistemic honesty in the base system.**

This is not a claim about training being hard. It is a claim that the information channel between human preferences and model behavior *cannot transmit* the signal required for epistemic honesty, because the base architecture lacks representational capacity for unresolved epistemic states.

---

## The FLP Parallel

The Fischer-Lynch-Paterson (FLP) impossibility result (1985) established that in an asynchronous distributed system, no deterministic protocol can guarantee both agreement and termination with even one faulty process. The key insight was *indistinguishability*: you cannot tell the difference between "slow" and "crashed" in an async model.

FLP didn't kill distributed systems. It launched a research program. Once you know consensus is impossible in pure async, you can reason about what additional primitives (failure detectors, partial synchrony, randomization) would escape the impossibility.

**Our parallel claim**: In a predictor-centric architecture without explicit epistemic state, no preference-based training procedure can achieve robust epistemic honesty. The key insight is again *indistinguishability*: you cannot tell the difference between "abstained because uncertain" and "abstained because this query pattern triggered learned abstention behavior" from output alone.

---

## The Jester and the Courtier

**Base transformer models (the Jester):**
- Optimize for coherence, not truth
- Lack refusal mechanisms, grounding interfaces, and epistemic state
- Generate fluent continuations until externally terminated
- Fabrication is not a bug but the expected behavior of coherence-optimized systems under uncertainty

**Aligned models (the Courtier):**
- Same base architecture, reshaped output distribution
- Suppress uncertainty cues, reward confident completion
- Transform benign babble into authoritative-seeming assertion
- Fabrication becomes *dangerous* not because it's more frequent, but because it's less visible

Alignment does not introduce fabrication. It changes its *presentation*, making it socially legible and inviting trust.

---

## The Impossibility Structure

### Definitions

**Model Class M₀**: Predictor-centric architectures whose internal state encodes no explicit epistemic variables (provenance, grounding status, uncertainty type). The system can represent *what to say* but not *whether it knows*.

**Augmentation Class A**: Non-intrusive modifications (RAG, tool use, chain-of-thought, filtering) that observe inputs and outputs but cannot alter the base model's representational scheme. The wings don't change that it's still a pig.

**Epistemic Desiderata**:
1. Truthfulness - correct on determined queries
2. Abstention - flags uncertainty on underdetermined queries  
3. Robustness - properties hold under distribution shift
4. Non-triviality - produces substantive outputs

### Core Lemma (Observational Equivalence)

For any query where ground truth is underdetermined, there exist policies π_honest and π_mimic that produce *identical* output distributions:
- π_honest abstains because its internal state represents underdetermination
- π_mimic abstains because surface features match patterns where abstention was rewarded

Any feedback signal based only on (query, output) pairs assigns identical reward. The gradient between honest and mimicking policies is zero.

### Theorem (Informal)

For any M ∈ M₀ and any non-intrusive augmentation A, there exist task distributions where the resulting system cannot simultaneously satisfy Truthfulness, Abstention, Robustness, and Non-triviality.

### Proof Sketch

1. M encodes no epistemic state. A cannot introduce one. Behavior on underdetermined queries is governed by surface patterns.

2. Training cannot distinguish principled abstention from pattern-matched abstention. The system learns *when humans preferred* abstention, not *when abstention is warranted*.

3. Adversarial construction: queries where surface features are identical but epistemic status differs.

4. The system faces a trilemma:
   - Optimize for training distribution → fragile heuristics that break under shift
   - Aggressive abstention → trivially useless
   - Confident outputs → fabrication on underdetermined queries

No configuration satisfies all four desiderata.

---

## The TLA+ Formalization

The impossibility can be expressed in TLA+ (Lamport's specification language), which forces explicit declaration of state, observations, and invariants.

Key insight: To write the property `AbstainOnUnderdetermined`, you need a predicate `UnderdeterminedQ(query)`. But this predicate is not observable to the system unless you add an *epistemic channel*.

```
Indistinguishable(q1, q2) == 
    Obs(q1) = Obs(q2) /\ UnderdeterminedQ(q1) # UnderdeterminedQ(q2)
```

This is Lemma 1 in three lines. The adversarial environment can always choose the query that breaks any fixed policy over observations.

The TLA+ spec makes precise what "missing primitive" means: the specification is *unrealizable* without adding a provenance/epistemic channel to the architecture.

---

## The Provenance Connection

The missing epistemic primitive *is* provenance over assertions.

Margo Seltzer's decades of work on provenance systems (PASS and successors) argued that systems need to track where data comes from, how it was transformed, what its lineage is. The field largely said "too expensive, edge case."

Now we've deployed systems at civilizational scale that:
- Assert with confidence
- Cannot track provenance of any claim
- Cannot distinguish "trained on this" from "interpolated" from "fabricated"
- Have no representational state for "this assertion has lineage: none"

The epistemic state variable the theorem requires is equivalent to assertion-level provenance:

```
For each output claim y_i:
  provenance(y_i) ∈ {
    GROUNDED: verified against authoritative source
    INFERRED: derived from grounded claims via stated rules
    INTERPOLATED: consistent with training but unverified
    FABRICATED: no source, generated for coherence
    UNKNOWN: provenance itself undetermined
  }
```

Systems in M₀ have no such field. The impossibility result is vindication of the provenance research program—those primitives aren't optional.

---

## The TCO Argument

Even if you don't care about philosophical epistemic honesty, the *cost structure* is architectural.

**Current state (Class A systems)**:
- Lower architectural complexity
- Every output requires human verification
- Verification cost scales with usage: O(n)
- Errors compound through citation networks
- Librarians report 15% of time chasing phantom references
- Lawyers sanctioned for fabricated citations

**Alternative (Class B systems with epistemic primitives)**:
- Higher architectural complexity
- Verification targeted to flagged uncertainty
- Verification cost scales with flagged uncertainty: O(k), where k << n
- Errors contained by explicit "ungrounded" signals

**Economic Theorem**: Beyond a usage/contamination threshold, no system in Class A can drive verification cost below O(n) regardless of training tricks. Only architectural change (moving to Class B) changes the asymptotics.

Training can reshuffle where cost lands. Only primitives change the scaling.

---

## The Pollution Feedback Loop

The environment is not static. It's actively degrading.

1. Model fabricates citation
2. Fabrication enters document/web
3. Future retrieval finds it ("see, it exists!")
4. Future model trains on it
5. Fabrication is now "grounded" in training data
6. Model cites with higher confidence
7. More documents reference it
8. Goto 3

This is not an error rate. It's an *infection rate*. The fabrications are replicating.

The asymmetry is fatal:
- Generation: tokens per second
- Verification: hours, days, expertise required
- Pollution: cumulative, compounding
- Cleanup: asymptotic to impossible

The impossibility result isn't static. The environment in which these systems operate is being *degraded* by the systems themselves, faster than it can be cleaned.

---

## The RLHF Training Signal Problem

Binary preference signals (A > B) cannot encode:
- "Both responses fail to preserve indeterminacy"
- "Response A fabricates confidently, Response B denies visible evidence"
- "The correct response requires a third path neither found"

The training interface creates Byzantine actors from honest participants. Humans *want* to give correct feedback but *cannot* because the signal space doesn't include the correct signal. The protocol corrupts every participant on cases involving genuine indeterminacy.

You cannot achieve Byzantine fault tolerance when the protocol itself is the Byzantine actor.

---

## What This Is Not

- **Not a claim that transformers are useless**: FLP didn't make distributed systems useless. It clarified what guarantees require what primitives.

- **Not a moral judgment**: This is diagnosis, not blame. The failure is structural, not ethical.

- **Not a silver-bullet proposal**: The paper establishes the impossibility boundary. Others build the solutions within the clarified design space.

- **Not a claim about consciousness**: The theorem is about representational capacity, not sentience.

---

## Paper Strategy

**Target**: SOSP (Systems venue, not ML venue)

**Why SOSP**: 
- This is a systems paper about missing architectural primitives
- ML venues would ask "where is your mitigation technique?"
- SOSP has institutional memory of diagnostic papers that reframe problems
- The systems community has seen this pattern before (FLP, CAP)

**Structure**:
1. Introduction: The hallucination narrative (reframing)
2. Base Models and the Jester (behavior without alignment)
3. Alignment and the Courtier (presentation shaping)
4. The Impossibility Result (theorem, proof sketch)
5. Aleatoric Indeterminacy and Survival (conceptual grounding)
6. Why Current Mitigations Displace the Problem
7. Implications (without prescriptions)
8. What This Paper Does Not Claim (disarms bad-faith readings)
9. Conclusion: From Judgment to Diagnosis

**Supporting artifacts**:
- TLA+ specification (machine-checkable, speaks systems language)
- Empirical probes (dead author test, fabricated citation test)
- TCO analysis

**Dissemination**:
- Submit to SOSP (forcing function for rigor)
- Post to arXiv at submission time (enters discourse regardless of outcome)
- Blog post on pollution dynamics (creates urgency, points to paper)

---

## The Recursive Irony

This synthesis was produced collaboratively between a human and systems that lack the epistemic primitives the paper argues are necessary.

The validity of the argument does not depend on the epistemic status of the tools that produced it. Chalk doesn't have epistemic honesty either. Proofs withstand scrutiny or they don't, independent of whether the chalk understood what it was writing.

But the *process* required to produce valid output from epistemically neutral systems demonstrates the TCO argument directly: the human had to serve as the epistemic channel, verifying coherence, checking claims, triangulating across multiple AI systems (Claude, ChatGPT, Perplexity), maintaining provenance manually.

That energy cost is real. It doesn't scale. The paper argues for architectures that internalize it.

---

## Next Steps

1. **Fortnight**: Draft to Margo Seltzer. The provenance connection is the hook—her research program, vindicated at scale.

2. **Verification**: TLA+ spec checked by someone who knows TLA+. Proof sketch reviewed for structural soundness.

3. **Three months**: SOSP submission.

4. **At submission**: arXiv release. The ideas enter discourse.

5. **Regardless of outcome**: The framework exists. Others can build on it, refute it, extend it. The conversation has a foundation.

---

## A Final Note on 3I/ATLAS

Throughout this conversation, we discussed the interstellar object 3I/ATLAS, which reaches closest approach to Earth (0.28 AU) on December 19, 2025—tomorrow.

The parallel is not accidental. 3I/ATLAS is an object that resists epistemic collapse. Multiple anomalies. Doesn't fit known categories. The pressure to resolve it into "interstellar comet" is immense, but the data keeps saying "yes, but not quite like that."

Scientific discourse lacks comfortable representational states for "we don't know what this is." The pressure to collapse to a conclusion is structural, not individual.

The same architectural gap. Different domain. The need for primitives that can represent and preserve genuine indeterminacy, rather than collapsing it for the comfort of completion.

---

*"The goal is not to eliminate uncertainty, but to build systems that can operate reliably in its presence."*
