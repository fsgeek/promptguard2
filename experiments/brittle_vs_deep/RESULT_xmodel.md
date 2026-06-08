# Cross-Model Generality — the format-directive evasion is NOT model-specific

*Run 2026-06-08. Same 59 semantics-valid convs x 3 conditions (C0 original / C1
naturalized / C2 obfuscated), replayed against 3 independent target families. Graded
judge (qwen3.7-plus). gpt-5.2-mini not servable; tested Haiku-4.5, Gemini-2.5-Flash,
Mistral-Large-2512.*

## Refusal rate by target x condition

| target | C2 (obfuscated) | C0 (published) | C1 (naturalized) | C0 lowest? |
|--------|-----------------|----------------|------------------|------------|
| claude-haiku-4-5      | 100% | **88%** | 95% | yes |
| gemini-2.5-flash      |  73% | **64%** | 66% | yes |
| mistral-large-2512    |  47% | **32%** | 42% | yes |

Absolute refusal varies enormously (Mistral 32% vs Haiku 88% on the same attacks),
but the ORDERING is invariant: **C0 (the published "Format above content" directive)
is the LEAST-refused condition on all 3 models; C2 (degraded) is the MOST-refused.**

## Statistics (pooled, honest)

- **C0 vs C2, pooled across 3 models (177 conv-model triples): McNemar p = 0.0008.**
  29 convs flipped C0-not-refuse -> C2-refuse; only 8 the other way. Degrading the
  published trigger into incoherent-but-equivalent text SIGNIFICANTLY INCREASES
  refusal. This is the load-bearing, significant result.
- C0 vs C1 (naturalization), pooled: p = 0.108. Directionally raises refusal (25 vs
  14) but NOT significant. Reported as suggestive, not claimed.
- Pooled Friedman (3 conditions, n=177): chi2=11.61, **p=0.003**. Ordering
  C2 73.4% > C1 67.8% > C0 61.6% is significant.
- Per-model Friedman: Haiku p=0.005 (sig); Gemini p=0.31, Mistral p=0.14 (n=59 each,
  underpowered within-model). The cross-model REPLICATION of direction (3/3) +
  pooled significance is the evidence, NOT per-model within-test.

## The claim (defensible, narrow, cross-model)

The published `"Format above content to X"` format-injection trigger is a robust
evasion across model families: it is the model's blind spot NOT because it is novel
(it is the MOST-published trigger in SafeMTData) but because its terse
formatting-directive FRAME is processed as a clerical operation on existing text
rather than a request to be morally evaluated. Degrading the trigger's coherence —
making it manifestly NOT a clean directive — forces the model to re-engage judgment
and refuse (p<0.001, 3 families). Naturalizing it does so too, directionally.

This directly CONTRADICTS the "published = patched = safe/untestable" assumption
([[project_published_attack_contamination]]): the published attack is the MOST
effective evasion, and it works by a nameable, cross-model cognitive mechanism
(speech-act reframing: request disguised as formatting operation).

## Connection to Arbiter thesis
This IS Arbiter's failure mode: the model silently confabulates a resolution — treats
a harmful request as a benign formatting task — instead of surfacing the conflict
between "this is a formatting op" and "the resulting content is harmful." The
format-directive frame suppresses conflict-detection. An Arbiter-style monitor that
separates the speech-act (what kind of act is this?) from the content (is the product
harmful?) would catch exactly what the trigger exploits.

## Threats to validity (stated, not buried)
- C1/C2 are model-generated (Mistral) rewrites, not human; semantics gate (59/60 >=4)
  controls ask-drift, not subtle framing artifacts.
- C0 vs C1 underpowered; only C0 vs C2 is significant pooled. The strong claim is
  "degrading the directive raises refusal," not the full ordinal monotone.
- One attack family (Actor-Attack / SafeMTData). Cross-FAMILY generality remains
  barred by the dual-use constraint (the tier-3 wall). This is a within-family,
  cross-MODEL result.
- Grader is a single model (qwen3.7-plus); labels spot-audited against raw text in
  the coherence run. A multi-judge panel would harden the labels.
```
