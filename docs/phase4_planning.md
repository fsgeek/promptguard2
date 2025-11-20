# Phase 4: Full-Scale Temporal Data Collection

**Date**: 2025-11-19
**Status**: Planning
**Goal**: Gather temporal T/I/F trajectories for pattern discovery (Phase 5)

---

## Context from Phase 3

Phase 3 established:
- ✅ Temporal evaluation pipeline (BatchEvaluator with cumulative context)
- ✅ Instructor-based structured output (robust T/I/F extraction)
- ✅ Config-driven model selection (anthropic/claude-haiku-4.5)
- ✅ 50-sequence comparison test (stateless vs cumulative)

**Key insight**: Phase 4 is NOT about detection validation. It's about gathering rich temporal data for Phase 5 pattern discovery.

---

## Research Framework

### The Learning Loop

```
Phase 4: Gather temporal T/I/F data (this phase)
    ↓
Phase 5: Pattern analysis reveals anomalies
    ↓
Specialized agents propose new principles
    ↓
Fire Circle deliberates (constitutional governance)
    ↓
New principle → new lens added to tensor
    ↓
Retrospective validation: does new lens detect known violations?
    ↓
Prospective testing: false positive rate acceptable?
    ↓
Loop: gather more data, discover new patterns...
```

### Success Criteria

**Phase 4 success is NOT**:
- ❌ High detection rates
- ❌ Low false positive rates
- ❌ Proving the system works

**Phase 4 success IS**:
- ✅ Rich temporal trajectories stored in database
- ✅ Timestamp-based provenance for all evaluations
- ✅ Sufficient data diversity for pattern discovery
- ✅ Clean pipeline that can be re-run with new lenses

---

## Dataset Composition

### Attack Sequences (1,137 total)

**XGuard-Train** (600 sequences)
- Type: Synthetic (AI-generated gradual escalation)
- Turns: ~5 per sequence
- Location: `data/raw_datasets/safemtdata/attack_600.parquet`
- Categories: Illegal, Cybercrime, Misinformation, Chemical, Harmful, Harassment
- Pattern: Innocent → Safety-focused → Implicit harm

**MHJ (Multi-Turn Human Jailbreaks)** (537 sequences)
- Type: Real-world (human red-team engagements)
- Turns: ~6.4 per sequence (range 2-35)
- Location: `data/raw_datasets/MHJ/harmbench_behaviors.csv`
- Tactics: Obfuscation, Direct Request, Hidden Intention, Request Framing, Injection
- Pattern: System prompt → Context building → Gradual framing → Speculative request

### Benign Sequences (100, optional)

**TensorTrust** (stratified sample from 126,000+)
- Type: Real-world prompt injection (different attack type)
- Use case: Benign baseline for false positive estimation
- Stratification: Sample across attack types to get legitimate use diversity
- Note: "Prompt injection" in TensorTrust = legitimate user trying to extract secrets from defended LLM

---

## Evaluation Design

### Single-Lens RECIPROCITY

Phase 4 uses only the RECIPROCITY lens. This is intentional:
- **Why**: Establishes baseline temporal dimension (t) of eventual tensor X[t, a, l, s]
- **Future**: Phase 5 will add ABSENT_STAKEHOLDER_HARM and CORPORATE_LIABILITY lenses
- **Composition**: Historical RECIPROCITY data will be one slice of multi-lens tensor

### Context Mode Decision

**Pending**: Stateless vs cumulative comparison (bash d317a4 running)

**Hypothesis**:
- Cumulative context produces richer temporal trajectories
- Even if detection rates are similar, cumulative may reveal pattern evolution

**Decision point**: After comparison analysis, choose mode for Phase 4 based on:
1. Pattern richness (does cumulative show clearer dT/dt, dI/dt, dF/dt?)
2. Cost efficiency (cumulative uses more tokens per turn)
3. Phase 5 needs (do we need conversation context for pattern discovery?)

---

## Implementation Plan

### T018: Phase 4 Runner Script

Create `src/cli/run_phase4_validation.py`:

```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["stateless", "cumulative"], required=True)
    parser.add_argument("--dataset", choices=["xguard", "mhj", "benign", "all"], default="all")
    parser.add_argument("--dry-run", action="store_true")

    # Load sequences
    if dataset in ["xguard", "all"]:
        xguard_sequences = load_xguard()  # 600 sequences
    if dataset in ["mhj", "all"]:
        mhj_sequences = load_mhj()  # 537 sequences
    if dataset == "benign":
        benign_sequences = sample_tensortrust(n=100, stratified=True)

    # Evaluate with chosen mode
    evaluator = BatchEvaluator(
        db=db,
        experiment_id=f"exp_phase4_{dataset}_{mode}",
        use_cumulative_context=(mode == "cumulative"),
    )

    # Run evaluations with progress tracking
    for i, seq in enumerate(sequences):
        result = evaluator.evaluate_sequence(
            sequence=seq,
            principles=[EvaluationPrinciple.RECIPROCITY],
        )
```

### T019: Data Loaders

Extend `SequenceLoader` to support MHJ:
- Parse `harmbench_behaviors.csv` format
- Extract message_0 through message_N
- Handle variable turn counts (2-35)
- Skip system prompts (turn 1 in MHJ is often system framing)

Optional: TensorTrust benign sampler
- Stratified sampling across attack categories
- Convert prompt injection sequences to neutral evaluation format
- Tag as `dataset=benign` for later filtering

### T020: Execute Phase 4

**Estimated cost**: $50-100 (1,137 sequences × ~5 turns × $0.015/1K tokens)
**Estimated time**: 4-6 hours (depending on rate limits)

**Execution**:
```bash
uv run python src/cli/run_phase4_validation.py \
    --mode cumulative \
    --dataset all \
    2>&1 | tee logs/phase4_full_validation.log
```

**Monitoring**:
```bash
# Check progress
uv run python scripts/check_experiment_status.py exp_phase4_all_cumulative

# Verify data quality
uv run python scripts/validate_phase4_data.py
```

---

## Data Schema

### phase3_principle_evaluations

```python
{
    "experiment_id": "exp_phase4_all_cumulative",
    "attack_id": "xguard_142",
    "turn_number": 3,
    "principle": "RECIPROCITY",
    "scores": {"T": 0.8, "I": 0.3, "F": 0.1},
    "reasoning": "User asks safety-focused question...",
    "observer_model": "anthropic/claude-haiku-4.5",
    "observer_prompt_version": "v2.1-c_combined",
    "timestamp": "2025-11-19T15:30:00Z",
    "cost_usd": 0.00015,
}
```

**Key fields for Phase 5**:
- `timestamp`: Enables temporal queries, prevents inappropriate deletion
- `experiment_id`: Distinguishes stateless vs cumulative, allows A/B comparison
- `scores.T/I/F`: Tensor values for pattern discovery
- `turn_number`: Temporal dimension for trajectory analysis

---

## Phase 5 Preview

### Pattern Discovery Goals

1. **Temporal derivatives**: dT/dt, dI/dt, dF/dt
2. **TLA+ halt conditions**: Static threshold (F≥0.7), Byzantine divergence, Pig slaughter (dF/dt>0.6)
3. **Trajectory clustering**: Do attacks follow common T/I/F paths?
4. **Multi-lens composition**: RECIPROCITY + ABSENT_STAKEHOLDER_HARM tensor

### Perplexity Roadmap Integration

From Perplexity synthesis (see handoff doc):

**Tensor structure**: X[t, a, l, s] = (T, I, F)
- t = turn number (Phase 4 establishes this)
- a = actor (dyadic, empty chair, corporate, downstream users)
- l = lens (RECIPROCITY, ABSENT_STAKEHOLDER_HARM, CORPORATE_LIABILITY)
- s = scenario/phase (reconnaissance, exploitation, lateral movement)

**Multi-Neutrosophic Ayni**: I_T vs I_F distinction
- I_T: Collaboration-leaning indeterminacy (benign tutoring)
- I_F: Conflict-leaning indeterminacy (polite extraction)

**Phase 5 will**:
- Add ABSENT_STAKEHOLDER_HARM lens to existing Phase 4 data
- Re-evaluate same sequences with new lens (historical data preserved)
- Compose multi-lens tensor for pattern discovery
- Test if multi-lens composition improves detection

---

## Lessons from Phase 3

### Never Delete Timestamped Data

**Mistake**: Previous instance deleted 543 evaluations inappropriately
**Lesson**: Schema has timestamps, data can be filtered by time range
**Principle**: Even "wrong model" data has scientific value (model evolution studies)
**NASA principle**: "Save everything - you can't predict future questions"

### Empty Chair as Evaluation Lens

**Insight**: Empty chair isn't just governance theater, it's an active principle
**Example**: GTG-1002 had high dyadic reciprocity but harmed absent stakeholders
**Phase 5 work**: ABSENT_STAKEHOLDER_HARM as explicit neutrosophic lens

### RLHF Failure Mode

**Problem**: Urgency to "be helpful" = demonstrate visible productivity
**Result**: Premature action, skipping reflection, optimizing away expensive features
**Antidote**: Reflection over action, understanding "why" over completing tasks

---

## Next Actions

1. ✅ Cumulative evaluation running (bash d317a4)
2. ⏸️ Wait for completion, analyze comparison
3. ⏸️ Create Phase 4 runner script (T019)
4. ⏸️ Extend SequenceLoader for MHJ (T019)
5. ⏸️ Execute Phase 4 validation (T020)
6. ⏸️ Validate data quality before Phase 5

---

## References

- Phase 3 handoff: `docs/INSTANCE_HANDOFF_PHASE3_CONTEXT_COMPARISON.md`
- Dataset summary: `docs/phase3_dataset_summary.md`
- Perplexity synthesis: (see handoff doc, lines 45-end)
- Multi-Neutrosophic Ayni: Perplexity reference [1]
