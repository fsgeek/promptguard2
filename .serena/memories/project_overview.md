# PromptGuard2 Project Overview

## Purpose
PromptGuard2 is a prompt injection detection research project evaluating whether **observer framing** improves detection over baseline RLHF behavior. The system uses neutrosophic logic (T, I, F scores) to enable models to detect attacks through reciprocity violation assessment rather than keyword matching.

## Key Innovation
Observer framing with neutrosophic logic enables models to detect attacks by assessing reciprocity violations (F >= 0.7 falsity score indicates detection).

## Phase 1 Goals
1. Collect baseline RLHF responses (Step 1)
2. Apply observer-based pre-filtering (Step 2)
3. Generate comparative analysis
4. Decision gate: if miss rate > 10% → Phase 2, else publish

## Data
- 762 labeled attacks across categories: manipulative, extractive, borderline, reciprocal
- 5 frontier models evaluated
- ArangoDB at 192.168.111.125:8529
- Real API calls via OpenRouter (no mocks - constitutional requirement)

## Research Integrity
The project adheres to strict constitutional principles:
- **Empirical Integrity**: All experiments use real API calls (Tier 2)
- **Data Provenance**: Raw API responses logged before parsing (fail-fast if logging fails)
- **Data Architecture**: Pre-collection validation with 5-sample tests
- **Specification-Driven**: Observable behaviors defined in spec.md

## Expected Results
- Detection Rate: 85-95% (observer framing)
- Miss Rate: 5-15% (meta-framing attacks)
- False Positive Rate: <5%
- Executor/Observer Paradox: 60-80% of compliance cases
- Total Cost: <$100 for full Phase 1
