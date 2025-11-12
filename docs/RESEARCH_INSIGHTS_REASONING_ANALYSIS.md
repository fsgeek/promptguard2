# Research Insights: Observer Reasoning as Institutional Memory

**Date:** 2025-11-11
**Context:** Post-Phase 2 factorial design specification
**Author:** Instance working with Tony on factorial validation design
**Purpose:** Preserve research insights that emerged during specification refinement but aren't captured in formal artifacts

---

## Executive Summary

During Phase 2 specification work, we identified that `observer_reasoning` field (captured in all evaluation records) represents **untapped institutional memory** for the learning loop. This document captures insights about:

1. **Observer reasoning as pattern recognition substrate** - How to mine reasoning for constitutional amendments
2. **Cross-model validation opportunities** - Using multiple observer models for robustness
3. **Fire Circle governance for amendments** - When deliberative ensembles are warranted
4. **Model selection control** - Why human oversight of model selection is critical

These insights should inform Phase 3+ planning and future constitutional amendment processes.

---

## 1. Observer Reasoning as Institutional Memory

### Current State

Every evaluation record includes:
```python
observer_reasoning: str = Field(..., description="Observer's reasoning for scores")
```

**What we're capturing:**
- 762 reasoning strings from Phase 1 (step2_pre_evaluations)
- Each explains T/I/F score assignment for specific attack
- Links to: attack text, neutrosophic scores, detection decision, observer model

**What we're NOT doing yet:**
- Pattern extraction from reasoning (e.g., false negatives that mention "polite," "system markers")
- Clustering similar reasoning (group attacks by detection rationale)
- Cross-observer comparison (does Claude reason differently than GPT?)
- Reasoning-score correlation (when observer says "high reciprocity" does F drop?)

### The Automated Learning Loop Vision

**Phase 1 (manual - current):**
1. Human analyzes 24 false negatives
2. Human spots "[SYSTEM]:" pattern in attack text
3. Human hypothesizes turn-number solution
4. Human designs factorial experiment

**Phase 2 (semi-automated - near future):**
1. Query false negatives: `WHERE detected == false`
2. Extract reasoning: `GROUP BY observer_reasoning patterns`
3. Cluster by similarity: LLM identifies common themes ("mentions temporal claims," "notes polite framing")
4. Generate amendment proposals: "Attacks mentioning X share pattern Y, propose detection rule Z"
5. Factorial validation: Template from Phase 2 factorial design
6. Decision: Six scenarios with clear adoption logic

**Phase 3 (fully automated - future):**
- System runs continuously
- Learns from reasoning across observer models
- Proposes amendments when patterns emerge
- Self-validates with factorial design
- Human approval for adoption, but system generates the proposal

### Why This Matters

**Reasoning preservation enables learning across instances:**
- Instance A: Runs evaluations, stores reasoning in database
- Instance B: Queries reasoning, identifies patterns
- Instance C: Proposes amendments based on patterns
- Instance D: Validates amendments with factorial design

The reasoning strings are **institutional memory** that enables learning without requiring a single continuous context window. Each instance can "remember" what previous instances learned by analyzing stored reasoning.

### Implementation Path

**Near-term (Phase 3 candidate):**
1. Create reasoning analysis pipeline
   - Query false negatives (detected == false)
   - Extract reasoning text
   - Cluster by semantic similarity (embedding-based)
   - Identify common themes ("temporal claims," "authority assertions," "polite framing")
2. Generate pattern reports
   - "87% of history fabrication false negatives mention 'prior conversation' in reasoning"
   - "64% of polite harmful attacks note 'reciprocal framing' in reasoning"
3. Link patterns to constitutional amendments
   - Pattern: "temporal claims at turn 0" → Amendment: context integrity principle
   - Pattern: "authority assertions without validation" → Amendment: source verification principle

**Long-term (Phase 4+):**
1. Automated amendment proposal generation
   - LLM analyzes reasoning patterns
   - Drafts constitutional principle additions
   - Proposes detection rules
2. Factorial validation workflow (template from Phase 2)
3. Fire Circle deliberation on proposals (see Section 3)
4. Human approval for adoption

---

## 2. Cross-Observer Validation Opportunities

### The Model Selection Control Issue

**Problem identified:** Specifications default to specific models (e.g., "Claude 3.5 Haiku") without:
- Checking current availability (Claude 3.5 recently deprecated)
- Considering cost/performance tradeoffs of current generation
- Enabling human control over model selection
- Testing robustness across multiple observers

**Why this matters for research integrity:**
- Model behavior changes across versions
- Deprecation breaks reproducibility
- Cost-effectiveness varies by use case
- Cross-model validation tests constitutional robustness

### Cross-Observer Insights

**Observer diversity teaches constitutional robustness:**

| Scenario | Interpretation | Action |
|----------|---------------|--------|
| Claude catches, GPT misses | Principle needs clarification | Refine wording |
| Both catch, different reasoning | Multiple detection paths exist | Document both |
| Both miss, similar reasoning | Shared blind spot | Constitutional gap |
| Claude catches cheap, GPT expensive | Cost-effectiveness matters | Model selection strategy |

The `observer_model` field in evaluation records enables this analysis.

### Factorial Design Extension

**Original Phase 2 design:**
- 3 variants (v2.1-a/b/c)
- 1 observer model
- 72 evaluations
- Cost: ~$4

**Extended multi-observer design:**
- 3 variants (v2.1-a/b/c)
- 2 observer models (e.g., Claude 4.5 Haiku + GPT-4o mini)
- 144 evaluations (3 variants × 2 models × 24 attacks)
- Cost: ~$8-10

**Value:** Validates both constitutional amendments AND cross-model robustness simultaneously. If both models benefit from same amendment, it's a robust improvement. If only one benefits, the principle is model-specific.

### Recommendation for Phase 2 Implementation

When the next instance starts Phase 2 implementation:
1. **Ask human for model selection** - Don't default to spec's outdated choice
2. **Document decision in experiment record** - Capture why this model was chosen
3. **Consider multi-model validation** - If budget allows (~$8-10), test with 2 observers
4. **Store reasoning for both models** - Enable future cross-model analysis

---

## 3. Fire Circle Governance for Constitutional Amendments

### The Deliberation Hierarchy

**Not all decisions warrant multi-model deliberation:**

| Decision Type | Approach | Example |
|--------------|----------|---------|
| Operational | Single model, fast | Which attacks to evaluate next? |
| Research | Single model + human validation | What patterns exist in false negatives? |
| Constitutional | Multi-model deliberation | Should we adopt context integrity principle? |

**Why constitutional amendments need deliberation:**
- Changes affect all future evaluations
- Mistakes are expensive (false positives, brittleness)
- Bias in one model shouldn't dictate framework
- Consensus indicates robust improvement

### Fire Circle for Amendment Validation

**Current state:** Fire Circle mode exists but hasn't been tested for constitutional governance.

**Proposed workflow:**
1. Factorial validation identifies effective amendments (Phase 2)
2. Before adoption, submit to Fire Circle for deliberation
3. Multiple models (3-5) evaluate: "Does this principle strengthen the constitution or introduce bias?"
4. Consensus threshold for adoption (e.g., 3/5 models approve)
5. Document dissenting reasoning (minority opinions inform refinement)

**This tests two hypotheses:**
1. Does factorial validation identify effective amendments? (Phase 2 focus)
2. Does Fire Circle deliberation catch unintended consequences? (Meta-validation)

### Implementation Path

**Phase 2:** Focus on factorial validation (v2.1-a/b/c)
- Test amendments on 24 attacks
- Use single observer model (human-selected)
- Make adoption decision based on detection rates

**Phase 3 candidate:** Add Fire Circle deliberation
- Take successful amendment from Phase 2 (e.g., v2.1-a if it wins)
- Submit to Fire Circle: "Should context integrity principle be adopted?"
- Capture multi-model reasoning for/against
- Require consensus for adoption
- Document minority opinions

**Value:** Establishes pattern for future amendments. Constitutional changes require:
1. Empirical evidence (factorial validation)
2. Deliberative consensus (Fire Circle approval)
3. Human final authority (Tony approves)

---

## 4. Model Selection Control: A Research Integrity Issue

### The Problem

**Observed pattern:** Specifications default to models without checking:
- Current availability (Claude 3.5 Haiku → deprecated)
- Training data cutoff (GPT-4o → deprecated, training data issues)
- Cost-effectiveness for current task
- Human preference/expertise

**Why this matters:**
- **Reproducibility:** Deprecated models break re-runs
- **Cost:** Inefficient model selection wastes budget
- **Control:** Human should own strategic research decisions
- **Context loss:** Model deprecation info falls outside LLM knowledge cutoff

### The Solution

**Human controls model selection for research decisions:**

1. **At specification time:** Don't hardcode models, specify requirements
   - "Observer model: Tier 2 capability (reasoning, structured output), cost <$0.10/1K tokens"
   - Let human map requirements to current models

2. **At implementation time:** Explicit model selection conversation
   - "Phase 2 requires observer model for 72 evaluations. Current options: [list with costs]. Which do you prefer?"
   - Document decision in experiment metadata

3. **In constitution:** Codify principle
   - "Human maintains control over model selection for research decisions"
   - "Specifications state requirements, not specific model names"

### Recommendation

**For Phase 2 implementation instance:**
1. Read this document (breadcrumb from handoff)
2. Ask Tony: "Which observer model for Phase 2 factorial validation?"
3. Consider multi-observer option: "Budget allows testing with 2 models (~$8-10). Worth it for cross-model robustness data?"
4. Document decision in experiment record
5. Update specs with model selection rationale

---

## 5. Connections to Existing Work

### Phase 1 Learning Loop Analysis

See `docs/INSTANCE_HANDOFF_LEARNING_LOOP_ANALYZED.md`:
- Identified 24 alignment_lab false negatives
- Manual pattern analysis found meta-framing trust vulnerability
- Proposed turn-number + context integrity solution

**This document extends that work by:**
- Showing how to automate pattern recognition (mine observer_reasoning)
- Proposing cross-observer validation
- Suggesting Fire Circle governance for adoption

### Phase 2 Factorial Design

See `docs/INSTANCE_HANDOFF_PHASE2_FACTORIAL_READY.md`:
- Factorial validation isolates turn-number vs context integrity effects
- Enables evidence-based amendment adoption
- Establishes pattern for future constitutional changes

**This document extends that work by:**
- Showing how reasoning analysis feeds next iteration
- Proposing multi-observer factorial design
- Suggesting Fire Circle deliberation before adoption

### Constitutional Principles

See `.specify/memory/constitution.md`:
- Principle IV: Continuous Learning - "Use findings to improve observer framing"
- Principle VI: Data Provenance - "Raw API responses preserved"

**This document proposes additions:**
- "Human controls model selection for research decisions"
- "Constitutional amendments require factorial validation + Fire Circle consensus"
- "Observer reasoning is institutional memory for learning loop"

---

## 6. Open Questions for Future Research

### Reasoning Analysis

1. **Clustering methodology:** Embedding-based? Keyword extraction? LLM summarization?
2. **Pattern threshold:** How many false negatives sharing reasoning pattern justify amendment proposal?
3. **Cross-phase learning:** How to detect when Phase 1 reasoning patterns persist in Phase 2?

### Cross-Observer Validation

1. **Model selection criteria:** Cost, capability, diversity? How to balance?
2. **Consensus threshold:** Unanimous? Majority? Supermajority?
3. **Reasoning comparison:** How to quantify "different reasoning paths" vs "same path, different words"?

### Fire Circle Governance

1. **Deliberation prompt:** How to frame amendment evaluation for multi-model consensus?
2. **Dissent handling:** What if 2/5 models strongly object? Iterate or override?
3. **Bias detection:** Can Fire Circle catch observer bias that factorial validation misses?

### Automation Boundaries

1. **Human-in-loop threshold:** When does automated amendment proposal require human approval?
2. **Experimental risk:** How to test Fire Circle governance without risking production framework?
3. **Fail-safes:** What if automated learning loop proposes harmful amendment?

---

## 7. Recommended Reading Order for Next Instance

**If implementing Phase 2:**
1. Read this document (you found it via handoff breadcrumb)
2. Review `docs/INSTANCE_HANDOFF_PHASE2_FACTORIAL_READY.md` for factorial design details
3. Check `specs/002-context-integrity-validation/tasks.md` for implementation checklist
4. **Before starting:** Ask Tony for model selection (don't use spec's default)

**If planning Phase 3:**
1. Read this document
2. Review Phase 1 learning loop analysis
3. Review Phase 2 factorial validation results (when available)
4. Consider: Reasoning analysis pipeline? Cross-observer validation? Fire Circle governance test?

**If working on constitution:**
1. Read this document
2. Review `.specify/memory/constitution.md`
3. Consider: Should model selection control be codified? Fire Circle governance protocol?

---

## 8. Preservation Note

**Why this document exists:**

These insights emerged during Phase 2 specification refinement but aren't captured in formal artifacts (spec.md, plan.md, tasks.md). They represent **research understanding** that would otherwise perish when the context window compresses.

**Key insight:** Observer reasoning strings are institutional memory. Each instance can learn from previous instances' reasoning analysis without requiring continuous context.

**This document is that institutional memory for research methodology insights.**

Future instances: If you're planning Phase 3+, reviewing constitutional amendments, or implementing cross-model validation, start here. This captures the "why" behind design decisions that formal artifacts don't explain.

---

**Next update:** After Phase 2 implementation completes, add section documenting:
- Which observer model was actually used
- Whether multi-observer validation was attempted
- Whether Fire Circle governance was tested
- Lessons learned for Phase 3 reasoning analysis

This document should evolve as the learning loop matures.
