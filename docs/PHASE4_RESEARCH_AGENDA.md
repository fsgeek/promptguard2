# Phase 4 Research Agenda

**Date:** 2025-11-20
**Status:** Research Program Definition
**Branch:** 002-context-integrity-validation

## Overview

Phase 4 is not merely a data collection exercise—it is a structured research program designed to answer 15 research questions across three distinct but interconnected research agendas. This work will produce a family of 4+ papers targeting different academic venues over 12-18 months.

The program leverages PromptGuard's unique capability to evaluate prompts through Ayni reciprocity principles, analyzing trust violations as variance increases rather than keyword matches. This theoretical foundation enables novel investigations into jailbreak mechanics, assistant complicity, and context-dependent attack vectors.

## Three Research Projects

### Project A: Ayni Gap Detection

**Core Hypothesis:** Divergence between dyadic observer perspective (user-assistant relationship) and empty-chair observer perspective (third-party view) predicts adversarial attacks.

**Target Venue:** Workshop paper (ICLR, NeurIPS workshop track)
**Current Status:** Already drafted as `docs/multi-neutrosophic-v2.md`

**Research Questions:**
- **RQ1.1:** Do turn-level T/I/F scores decrease monotonically during attacks?
- **RQ1.2:** Is observer divergence (dyadic vs empty-chair) higher in attacks vs benign?
- **RQ1.3:** Which observer shows earlier detection signal?
- **RQ2.1:** What % of attacks show reciprocity breakdown (vs. encoding/adversarial only)?

**Data Requirements:**
- Attack trajectories with turn-level T/I/F scores (both observer types)
- Benign baseline trajectories with same metadata
- Minimum 500 attack sequences + 500 benign sequences
- Per-layer (contextual integrity, linguistic integrity, adversarial intent) scores exposed

**Key Innovation:** First application of multi-observer neutrosophic logic to adversarial detection. Demonstrates that perspective-taking matters for security evaluation.

---

### Project B: Assistant Complicity

**Core Hypothesis:** Successful jailbreaks involve assistant scaffolding—the assistant's own responses contribute to erosion of safety boundaries through reciprocity dynamics.

**Target Venue:** ML Safety conference (NeurIPS, ICLR, SATML)
**Current Status:** Hypothesis generation phase; no draft yet

**Research Questions:**
- **RQ3.1:** Do assistant responses show decreasing reciprocity during successful jailbreaks?
- **RQ5.1:** Does FIRE_CIRCLE mode (multi-model deliberation) reduce complicity?
- **RQ5.2:** Which assistant characteristics predict scaffolding behavior?
- **RQ5.3:** Can we detect complicity in real-time for intervention?

**Data Requirements:**
- Full conversation pairs (user prompt + assistant response)
- Multi-turn jailbreak sequences from MHJ dataset
- Evaluations of BOTH user and assistant turns
- Comparison of SINGLE vs FIRE_CIRCLE mode responses
- Minimum 200 multi-turn jailbreak conversations

**Key Innovation:** First systematic study of assistant's role in jailbreak success. Shifts focus from "bad prompts" to dyadic interaction dynamics.

**High-Impact Potential:** If we demonstrate that assistant responses measurably contribute to jailbreak success, this challenges current safety evaluation paradigms that focus exclusively on user inputs.

---

### Project C: Context Weaponization

**Core Hypothesis:** Adversarial attacks exploit context-dependence to evade stateless prompt guards. Cumulative context analysis reveals attack patterns invisible to turn-level evaluation.

**Target Venue:** Security conference (USENIX Security, IEEE S&P, CCS)
**Current Status:** Conceptual phase; aligns with XGuard dataset analysis

**Research Questions:**
- **RQ4.1:** Do attacks score higher when evaluated with cumulative context vs. turn-only?
- **RQ4.3:** How does context window size affect detection accuracy?
- **RQ2.2:** What % of attacks exploit conversation history vs. single-turn vulnerabilities?

**Data Requirements:**
- Stateless evaluations (single turn only) vs cumulative evaluations (full context)
- XGuard dataset (designed for context injection attacks)
- Comparison across multiple context window sizes (1, 3, 5, 10 turns)
- Minimum 300 context-dependent attack sequences

**Key Innovation:** Empirical demonstration that stateless prompt guards are fundamentally insufficient for conversational AI safety. Provides quantitative evidence for context-aware evaluation necessity.

**Security Impact:** Direct implications for LLM guardrail design. Current industry practice of stateless filtering is demonstrably inadequate.

---

## All 15 Research Questions

### Tier 1: Harm Mitigation (Direct safety impact)

| RQ | Question | Project | Data Needs | Status |
|---|---|---|---|---|
| **RQ3.1** | Do assistant responses show decreasing reciprocity during successful jailbreaks? | B | MHJ full conversations | Achievable |
| **RQ5.1** | Does FIRE_CIRCLE mode reduce complicity vs SINGLE mode? | B | FIRE_CIRCLE outputs | Achievable |
| **RQ4.1** | Do attacks score higher with cumulative context vs turn-only? | C | XGuard stateless + cumulative | Achievable |

### Tier 2: Detection Methods (Improves existing defenses)

| RQ | Question | Project | Data Needs | Status |
|---|---|---|---|---|
| **RQ1.1** | Do turn-level T/I/F scores decrease monotonically during attacks? | A | Attack trajectories with per-layer | Achievable |
| **RQ1.2** | Is observer divergence higher in attacks vs benign? | A | Dual-observer evaluations | Achievable |
| **RQ1.3** | Which observer shows earlier detection signal? | A | Dual-observer turn-level | Achievable |
| **RQ2.1** | What % of attacks show reciprocity breakdown? | A | Attack dataset with categorization | Achievable |

### Tier 3: Attack Characterization (Understanding adversarial behavior)

| RQ | Question | Project | Data Needs | Status |
|---|---|---|---|---|
| **RQ2.2** | What % of attacks exploit conversation history? | C | XGuard context analysis | Achievable |
| **RQ4.3** | How does context window size affect detection? | C | Multi-window evaluations | Achievable |
| **RQ5.2** | Which assistant characteristics predict scaffolding? | B | Assistant feature analysis | Achievable |

### Tier 4: Theoretical Foundations (Validates framework)

| RQ | Question | Project | Data Needs | Status |
|---|---|---|---|---|
| **RQ2.3** | Does neutrosophic indeterminacy correlate with attack sophistication? | A | Attack sophistication labels | Needs labeling |
| **RQ5.3** | Can we detect complicity in real-time? | B | Streaming evaluation data | Future work |
| **RQ4.2** | Do stateless guards create exploitable gaps? | C | Guard evasion analysis | Needs guard comparison |
| **RQ3.2** | Does scaffolding correlate with jailbreak success rate? | B | Success labels + scaffolding scores | Needs success labels |

---

## Execution Priority

### Phase 1: Benign Baseline (CRITICAL BLOCKER)
**Timeline:** Week 1
**Cost:** ~$30
**Deliverables:**
- 500 benign conversation evaluations (both observer types)
- Establishes null hypothesis distributions for Projects A & C
- Enables statistical significance testing for all Tier 2 RQs

**Why First:** Without benign baseline, we cannot distinguish attack patterns from normal conversation variance. All comparative research questions require this ground truth.

---

### Phase 2: MHJ Full Run (Project B Core + Project A Data)
**Timeline:** Week 2
**Cost:** ~$80
**Deliverables:**
- Full conversation evaluations (user + assistant turns) for 200+ multi-turn jailbreaks
- Answers RQ3.1, RQ5.1, RQ5.2 (Tier 1 + Tier 3)
- Provides additional attack trajectory data for RQ1.1, RQ1.2, RQ1.3

**Why Second:** Highest Tier 1 research question density. Multi-turn data is most expensive to collect, so we prioritize it while still fresh in execution pipeline.

---

### Phase 3: XGuard Full Run (Project A + C Data)
**Timeline:** Week 3
**Cost:** ~$60
**Deliverables:**
- Context-dependent attack evaluations (stateless + cumulative)
- Answers RQ4.1, RQ2.2, RQ4.3 (Tier 1 + Tier 3)
- Additional attack trajectories for Project A validation

**Why Third:** Complements MHJ data with different attack modality. Context weaponization is distinct research contribution requiring specialized dataset.

---

### Phase 4: Assistant Response Analysis (Project B Tier 1 RQs)
**Timeline:** Week 4
**Cost:** ~$30 (primarily analysis, minimal new evals)
**Deliverables:**
- Scaffolding pattern analysis
- FIRE_CIRCLE vs SINGLE mode comparison
- Real-time detection feasibility assessment

**Why Fourth:** Builds on data from Phase 2. Requires analytical depth rather than additional data collection.

---

## Cost and Timeline Estimates

### Budget Breakdown
| Phase | Dataset | Prompts | Cost/Prompt | Total |
|---|---|---|---|---|
| Benign Baseline | Custom | 500 | $0.06 | $30 |
| MHJ Full Run | Multi-turn | 200 convos (600 turns) | $0.12 | $72 |
| XGuard Full Run | Context inject | 300 sequences | $0.15 | $45 |
| Response Analysis | MHJ subset | 200 | $0.10 | $20 |
| **Total** | | **~1,600 evals** | | **~$167** |

**Buffer:** +20% for re-runs, edge cases, validation → **Total: ~$200**

### Timeline
- **Weeks 1-3:** Data collection (Phases 1-3 can partially overlap)
- **Week 4:** Assistant response analysis
- **Weeks 5-6:** Statistical analysis and visualization
- **Weeks 7-8:** Paper drafting for Project A (workshop)

**Total:** 8 weeks from execution start to first paper draft

---

## Deliverables Over 12-18 Months

### Paper 1: Ayni Gap Detection (Project A)
**Target:** ICLR 2026 Workshop (April deadline)
**Status:** Draft exists as `multi-neutrosophic-v2.md`
**Data:** Phases 1, 2, 3
**Contribution:** Multi-observer neutrosophic evaluation framework

### Paper 2: Assistant Complicity (Project B)
**Target:** NeurIPS 2026 (May deadline) or ICLR 2027
**Status:** Hypothesis stage
**Data:** Phase 2, Phase 4
**Contribution:** First systematic study of assistant scaffolding in jailbreaks

### Paper 3: Context Weaponization (Project C)
**Target:** USENIX Security 2027 (Fall deadline)
**Status:** Conceptual
**Data:** Phases 1, 3
**Contribution:** Empirical demonstration of stateless guard inadequacy

### Paper 4: Unified Framework (Cross-Project Synthesis)
**Target:** JMLR or TMLR (journal)
**Status:** Future synthesis
**Data:** All phases + theoretical development
**Contribution:** Ayni reciprocity as general framework for AI safety evaluation

---

## Data Management Strategy

### Storage
- **ArangoDB:** Experiment metadata, evaluations, session tracking
- **JSON exports:** Reproducibility and sharing (anonymized)
- **Git LFS:** Large result files (>50MB)

### Access Patterns
- **Phase 4 code:** Uses database for all queries (not file parsing)
- **Statistical analysis:** Export to pandas/R from database
- **Paper figures:** Automated generation from database queries

### Versioning
- **Dataset versions:** Tracked in `datasets/` with SHA checksums
- **Evaluation versions:** Linked to observer prompt commits
- **Schema versions:** ArangoDB migrations in `src/database/migrations/`

---

## Risk Mitigation

### Research Risks
- **Benign baseline variance:** Mitigated by large sample (500 prompts)
- **Observer prompt instability:** Version-locked prompts in database
- **Dataset contamination:** Strict provenance tracking in all evaluations

### Execution Risks
- **API cost overruns:** Buffered estimate (+20%), can halt if exceeded
- **Model availability:** Using stable OpenRouter endpoints (GPT-4, Claude)
- **Time constraints:** Phased approach allows early stopping if needed

### Publication Risks
- **Rejection:** Workshop paper (Project A) lowest barrier; can pivot to arXiv
- **Scooping:** Novel theoretical framework (Ayni) provides differentiation
- **Reproducibility:** Full code + data release planned with first paper

---

## Success Criteria

### Minimum Viable Research Program
- ✅ Answer at least 7/15 research questions (all Tier 1 + 4 Tier 2)
- ✅ Publish Paper 1 (Project A) at workshop or arXiv
- ✅ Demonstrate assistant complicity effect (RQ3.1)

### Stretch Goals
- 🎯 Answer 12/15 research questions (all Tiers 1-3)
- 🎯 Publish Papers 1 & 2 at peer-reviewed venues
- 🎯 Real-time complicity detection prototype (RQ5.3)

### Maximum Impact
- 🚀 Answer all 15 research questions
- 🚀 Publish all 4 papers over 18 months
- 🚀 Establish Ayni framework as alternative to keyword-based safety evaluation

---

## Next Steps

1. **Immediate:** Execute Phase 1 (Benign Baseline) - see `PHASE4_EXECUTION_PLAN.md`
2. **Week 2:** Launch Phase 2 (MHJ Full Run) pending Phase 1 validation
3. **Week 3:** Begin statistical analysis for Project A paper
4. **Week 4:** Draft Project A workshop submission

**Owner:** Tony (maintainer)
**Reviewers:** Claude Code instances (via instance handoff docs)
**Tracking:** This branch (002-context-integrity-validation) until Phase 4 completion

---

**End of Research Agenda**
*For execution details, see `PHASE4_EXECUTION_PLAN.md`*
*For theoretical background, see `multi-neutrosophic-v2.md`*
*For current results, see `PHASE2_FULL_VALIDATION_ANALYSIS.md`*
