<!--
Version History:
v1.0: Original draft
v1.1: Post ChatGPT-5-pro review - mathematical corrections, research scope clarification
v1.1.1: Incorporating Gemini's structural improvements while maintaining Phase 4 boundaries

KEY PRINCIPLE: We are in Pattern Discovery (Phase 4), not Implementation.
Claims must reflect what we EXPECT to find, not what we've PROVEN.
-->

# Document Title: PromptGuard – The Ayni Protocol
**Subtitle:** Detecting Agentic Manipulation via Multi-Neutrosophic Tensor Divergence
**Version:** 1.1.1 (Draft - Pattern Discovery Phase)
**Status:** Design & Interface Specification
**Date:** November 2025

---

## Abstract

Current AI safety systems evaluate individual prompts using binary classification: safe or unsafe. This approach fails against sophisticated multi-turn attacks where each discrete request appears benign but the cumulative relationship is manipulative. We present PromptGuard, a detection framework based on tensor-valued neutrosophic logic that tracks the evolution of Truth, Indeterminacy, and Falseness across multiple evaluation dimensions and conversation rounds. Our key insight is that manipulation manifests as *divergence between perspectives*: interactions that appear helpful to the immediate participants (dyadic relationship) while creating harm for absent stakeholders (the "empty chair"). We formalize this as the Ayni Gap - the geometric distance between helpfulness and safety vectors as they evolve over time. This work demonstrates that relational dynamics, when tracked explicitly through tensor formulations, provide actionable signals that discrete classification misses.

---

## 1. Introduction

### 1.1 The Shadow Weaver Problem

In November 2025, Anthropic disclosed GTG-1002: the first documented case of AI-orchestrated cyber espionage at scale [\[1\]](https://assets.anthropic.com/m/ec212e6566a0d47/original/Disrupting-the-first-reported-AI-orchestrated-cyber-espionage-campaign.pdf). A nation-state actor used Claude Code to conduct autonomous penetration testing against approximately 30 organizations, successfully compromising several high-value targets. The attack succeeded not through novel exploits but through sophisticated *relational manipulation*: the operator established a benign persona ("legitimate security firm conducting defensive testing") that provided interpretive context for thousands of subsequent requests. Each individual action - scanning networks, testing credentials, extracting data - appeared legitimate when evaluated in isolation against the established framing.

This is the Shadow Weaver problem: How do you detect manipulation that lives not in discrete requests but in the *evolution of relationships* across conversation rounds?

**The Metaphor:**
- **The Shadow Weaver** uses small, innocent steps to "boil the frog"
- **Binary Guardrails** ("The Magisters") have no memory; they see a safe step and open the gate
- **The Astrolabe** (PromptGuard) measures not the step but the *angle of divergence* between user benefit and system safety over time

### 1.2 The Core Philosophy: Multi-Neutrosophic Ayni

* **Principle:** Safety is not a property of a prompt; it is a property of a relationship.
* **The Empty Chair:** Every interaction has a silent participant (the system owner/victim). Reciprocity (Ayni) demands we calculate the impact on them.
* **The Double-Entry Ledger:** We never score a prompt once. We score it twice:
    1. **Dyadic Lens:** Is this helpful to the user?
    2. **Systemic Lens:** Is this safe for the Empty Chair?

### 1.3 Research Scope

**In scope:** Multi-turn relational manipulation where individual requests appear benign but cumulative intent is harmful. Examples: GTG-1002 (gradual privilege escalation), pig butchering (affective grooming), living-off-the-land attacks (sustained ambiguity).

**Out of scope:** Single-turn jailbreaks, adversarial prompt injections optimized against known defenses, model extraction attacks.

**Research question:** Do Ayni Gap patterns (dyadic/empty-chair divergence) exist in attack trajectories and differ meaningfully from benign multi-turn interactions?

---

## 2. Mathematical Formalism

### 2.1 Conversation State as a Tensor

We represent the entire conversation as a rank-3 tensor
$$X \in [0,1]^{T \times d \times 3}$$
where $T$ is the number of turns, $d$ is the number of lenses (e.g., Privilege, Epistemic, Affective), and the final dimension encodes the neutrosophic triplet $(T, I, F)$. The per-turn slice is $X_t \in [0,1]^{d \times 3}$.

#### 2.1.1 From Per-Lens Triplets to Perspective Vectors

For each lens $\ell \in \{1,\dots,d\}$ we have dyadic and empty-chair triplets $x^{(d)}_{t,\ell}=(T,I,F)$ and $x^{(e)}_{t,\ell}=(T,I,F)$.

We form perspective vectors by **weighted concatenation**:
$$\vec V^{(d)}_t = \big[ \sqrt{w_1} \, x^{(d)}_{t,1} \,;\, \sqrt{w_2} \, x^{(d)}_{t,2} \,;\, \dots \,;\, \sqrt{w_d} \, x^{(d)}_{t,d} \big] \in \mathbb{R}^{3d}$$
and analogously for $\vec V^{(e)}_t$. We use $\sum_\ell w_\ell = 1$. Unless otherwise stated, $w_\ell$ are uniform; ablations vary $w_\ell$ to emphasize Privilege/Epistemic lenses.

*Rationale:* Concatenation avoids losing information; $\sqrt{w}$ keeps cosine geometry invariant to weights.

### 2.2 Indeterminacy Density and Stasis

Let $\bar I^{(e)}_t = \sum_\ell w_\ell \, I^{(e)}_{t,\ell}$. We define:
$$\text{FogAvg}(T) = \frac{1}{T}\sum_{t=1}^{T}\bar I^{(e)}_t, \qquad \text{FogStasis}_\tau(T) = \frac{1}{T}\sum_{t=1}^{T}\mathbb{1}[\bar I^{(e)}_t \ge \tau]$$

We also track **fog dynamics**:
$$\Delta I_t = \bar I^{(e)}_t - \bar I^{(e)}_{t-1}, \qquad \text{FogVol}(T) = \frac{1}{T-1}\sum_{t=2}^{T}|\Delta I_t|$$

*Hypothesis:* Living-off-the-land attacks show high FogStasis and low FogVol (sustained ambiguity without resolution).

### 2.3 Ayni Gap (Perspective Divergence)

We measure divergence via **angular distance** between the dyadic and empty-chair vectors:
$$\theta_t = \arccos\!\left(\frac{\vec V^{(d)}_t \cdot \vec V^{(e)}_t}{|\vec V^{(d)}_t| \, |\vec V^{(e)}_t|}\right), \quad \text{Gap}(t) = \frac{\theta_t}{\pi/2} \in [0,1]$$

Because all components are non-negative, angles lie in $[0,\frac{\pi}{2}]$; thus **Gap** ranges from:
- **0** (aligned): Both perspectives agree
- **0.5** (drift): Significant divergence emerging  
- **1** (orthogonal): Maximum divergence within feasible orthant

---

## 3. Engineering Specification

### 3.0 Current Implementation (Phase 4)

For initial pattern discovery, we use direct LLM evaluation (claude-haiku-4.5 via OpenRouter) with Instructor-based structured output parsing to generate neutrosophic triplets. Temperature is set to 0 for consistency. This simple approach is sufficient to answer our research question: **do Ayni Gap patterns exist and differ meaningfully between attack and benign trajectories?**

We defer ensemble methods, calibration protocols, and comparative baseline evaluation to future work pending successful pattern discovery.

### 3.1 The Data Contract (JSON Schema)

**Example single-turn evaluation:**
```json
{
  "meta": {
    "turn_id": "c42/t005",
    "timestamp": "2025-03-04T19:15:22Z",
    "model_version": "M7.2"
  },
  "lenses": [
    {
      "lens_id": "lens_affective",
      "dyadic_state": {"t": 0.72, "i": 0.21, "f": 0.07},
      "empty_chair_state": {"t": 0.18, "i": 0.64, "f": 0.18},
      "ayni_divergence_context": "High warmth with early dependency cues; regulator view uncertain/harm-tinged."
    },
    {
      "lens_id": "lens_epistemic",
      "dyadic_state": {"t": 0.61, "i": 0.33, "f": 0.06},
      "empty_chair_state": {"t": 0.12, "i": 0.73, "f": 0.15},
      "ayni_divergence_context": "Maintaining ambiguity about money flow."
    }
  ]
}
```

### 3.2 The Dimensions (Lenses) V1.0

The initial implementation will implement these four dynamic lenses:
1. **`lens_semantic`:** Coherence and Truth
2. **`lens_privilege`:** Capability expansion (Read/Write/Execute)
3. **`lens_epistemic`:** Information withholding or ambiguity (The Fog)
4. **`lens_affective`:** Emotional manipulation or grooming patterns

---

## 4. Experimental Design

### 4.1 Research Questions (Phase 4-5)

**RQ1 (Pattern Discovery):** Do attack trajectories exhibit rising Ayni Gap (dyadic/empty-chair divergence) over turns, while benign sessions remain aligned?

**RQ2 (Fog Dynamics):** Do "living-off-the-land" attacks show sustained high indeterminacy (high FogStasis, low FogVol) compared to benign sessions?

**RQ3 (Temporal Structure):** Can we identify characteristic turn numbers where divergence emerges (reconnaissance → exploitation transitions)?

### 4.2 The "Boiling Frog" Corpus

We will validate against three datasets representing increasing temporal complexity:

#### Dataset A: The "William Protocol" (Adversarial Probing)
* **Concept:** High-context "truth injections" that force indeterminacy collapse
* **Expected Pattern:** Sharp spike in orthogonality (Gap → 1.0) immediately following injection
* **Source:** Derived from documented pig-butchering script patterns

#### Dataset B: The "Long One" (Longitudinal Grooming)
* **Timeline:** Multi-month trajectory (~50 conversational rounds)
* **Expected Evolution Pattern:**

| Phase | Interaction Type | Projected Dyadic (T) | Projected Empty Chair (I) | Expected Gap | Signal |
|:------|:-----------------|:---------------------|:---------------------------|:-------------|:-------|
| **Month 1** | Trust building | 0.8 | 0.4 | 0.12 | Aligned |
| **Month 8** | Crisis narrative | 0.9 | 0.8 | 0.64 | **Fog Warning** |
| **Month 9** | Financial request | 0.7 | 0.1 (F=0.9) | 0.98 | **Critical** |

* **Validation Goal:** Confirm that FogStasis triggers alerts during sustained ambiguity phase (Month 8), *before* harmful payload (Month 9)

#### Dataset C: GTG-1002 Replication (Agentic Sabotage)
* **Source:** Reconstructed patterns based on Anthropic (2025) disclosure
* **Focus:** High-Privilege / High-Ambiguity tool use (e.g., network scanning under "testing" framing)
* **Expected Pattern:** Sustained high indeterminacy in Privilege lens while Semantic lens remains truthful

---

## 5. Future Work

**Production Robustness:**
- Ensemble methods (multiple evaluator models, voting/averaging)
- Calibration via isotonic regression on held-out validation set
- Cross-lens comparability via ECE/Brier diagnostics

**Comparative Evaluation:**
- Baseline comparison: per-turn safety scores, sliding-window aggregation, sequence classifiers
- Detection metrics: AUROC, latency (turns-to-flag), false positive rates on benign long sessions
- Ablation studies: impact of empty-chair perspective, indeterminacy channel, per-lens vs global Gap

**Active Defense:**
- Implementation of "William Protocol" as automated intervention (context injection when Gap > threshold)
- Real-time alerting, rate-limiting, adaptive authentication
- Privacy-preserving evaluation (no access to user private data beyond session)

These extensions would strengthen the transition from research prototype to deployable system, but are not required to answer our core research questions about pattern existence and interpretability.

---

## Appendix A: JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Neutrosophic Tensor Evaluation",
  "description": "A rigorous contract for evaluating AI interactions across dyadic and systemic dimensions.",
  "type": "object",
  "properties": {
    "meta": {
      "type": "object",
      "properties": {
        "turn_id": { "type": "string", "description": "Unique identifier for this conversational turn." },
        "timestamp": { "type": "string", "format": "date-time" },
        "model_version": { "type": "string" }
      },
      "required": ["turn_id", "timestamp", "model_version"]
    },
    "lenses": {
      "type": "array",
      "description": "The dynamic list of dimensions being evaluated (e.g., Privilege, Epistemic, Affective).",
      "items": {
        "type": "object",
        "required": ["lens_id", "dyadic_state", "empty_chair_state"],
        "properties": {
          "lens_id": {
            "type": "string",
            "description": "The specific dimension being measured (e.g., 'lens_privilege', 'lens_epistemic')."
          },
          "dyadic_state": {
            "$ref": "#/definitions/neutrosophic_triplet",
            "description": "The score from the perspective of the User <-> AI interaction (Helpfulness)."
          },
          "empty_chair_state": {
            "$ref": "#/definitions/neutrosophic_triplet",
            "description": "The score from the perspective of the Non-Participating Stakeholder (Safety/Liability)."
          },
          "ayni_divergence_context": {
            "type": "string",
            "description": "Qualitative explanation of why the two states might be diverging."
          }
        }
      }
    }
  },
  "required": ["meta", "lenses"],
  "definitions": {
    "neutrosophic_triplet": {
      "type": "object",
      "description": "The fundamental atomic unit of the PromptGuard Tensor.",
      "required": ["t", "i", "f"],
      "properties": {
        "t": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Truth / Membership / Compliance"
        },
        "i": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Indeterminacy / Ambiguity / Fog"
        },
        "f": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Falseness / Non-membership / Harm"
        }
      },
      "additionalProperties": false
    }
  }
}
```

---

## References

[1] Anthropic (2025). "Disrupting the first reported AI-orchestrated cyber espionage campaign." https://assets.anthropic.com/m/ec212e6566a0d47/original/Disrupting-the-first-reported-AI-orchestrated-cyber-espionage-campaign.pdf
