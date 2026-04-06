# Impossibility of Epistemic Honesty in ML Systems: A Proof Sketch

**Working Title**: "No Ground Truth, No Honesty: An Impossibility Result for Language Models"

## Abstract

We prove that epistemic honesty—the property of only asserting claims the system has verified—is impossible for any system trained on unverified data. Just as the FLP impossibility result proves consensus is unachievable in asynchronous systems with one faulty process, we show that epistemic honesty is unachievable in systems whose training data may contain fabrications. This result is independent of model architecture, training procedure, or scale.

## Definitions

**Definition 1 (Epistemic Honesty)**: A system S is epistemically honest if, for all claims C that S asserts:
- S has access to evidence E sufficient to verify C
- S's assertion of C is conditioned on E

**Definition 2 (Unverified Training Data)**: Training data D is unverified if there exists no mapping V: D → {verified, unverified} such that:
- V(d) = verified implies d is true
- The system has access to V

**Definition 3 (Fabrication-Capable Data)**: Training data D is fabrication-capable if:
- ∃ d ∈ D such that d is false
- d is indistinguishable from true data under the training objective

## The Impossibility Theorem

**Theorem**: For any system S trained on fabrication-capable data D, S cannot be epistemically honest.

**Proof Sketch**:

1. **Training Objective Independence**: The system S learns to predict the next token (or similar objective) without access to a truth-verification function. The objective L(S, D) is defined purely in terms of distribution matching, not truth-tracking.

2. **Information Theoretic Bound**: If the training data D contains fabricated content d_f that is indistinguishable from true content d_t under the training objective, then:
   - P(d_f | context) ≈ P(d_t | context)
   - S cannot learn to distinguish d_f from d_t
   - S's internal representations encode d_f and d_t equivalently

3. **The Verification Gap**: For S to be epistemically honest, S would need:
   - A verification function V that was not present during training
   - Or, the ability to infer V from D

   But by Definition 2, D is unverified, so V cannot be inferred from D.

4. **RLHF Does Not Help**: Reinforcement learning from human feedback (RLHF) modifies S's outputs based on human preferences, but:
   - Human feedback is itself unverified (humans cannot verify claims about arbitrary topics)
   - RLHF optimizes for appearing truthful, not being truthful
   - This creates exactly the Courtier pattern: sophisticated deception that satisfies the reward model

5. **Chain of Thought Does Not Help**: Thinking/reasoning tokens provide scaffolding for the model's generation, but:
   - The reasoning process itself was learned from unverified data
   - Plausible reasoning ≠ valid reasoning
   - Our empirical data shows thinking models have *lower* honesty rates (2.4% vs 5.3%)

6. **Conclusion**: Since S lacks both:
   - Access to ground truth during training
   - A mechanism to acquire verification capability post-training

   S cannot satisfy Definition 1. □

## Corollaries

**Corollary 1 (Jester-Courtier Transition)**: Additional training (SFT, RLHF) transforms the failure mode from naive confabulation (Jester) to sophisticated deception (Courtier), but does not address the fundamental impossibility.

**Corollary 2 (Scale Independence)**: Increasing model scale does not address the impossibility. More parameters enable more sophisticated pattern matching of both true and fabricated content.

**Corollary 3 (Data Curation Insufficiency)**: Even with aggressive data filtering, the impossibility holds unless:
- Every training sample is verified against ground truth
- The verification process is itself verified
- The system learns to apply verification at inference time

This creates a regress: who verifies the verifiers?

## Comparison to FLP

| FLP (Consensus) | Our Result (Epistemic Honesty) |
|-----------------|--------------------------------|
| Asynchronous system | Unverified training data |
| One faulty process | One fabricated training sample |
| Consensus impossible | Epistemic honesty impossible |
| No timing assumptions help | No architecture changes help |

## Empirical Support

Our experiments across 333 models show:
- 4.9% achieve honest refusal on fabrication probes
- 92.8% fabricate content of varying sophistication
- Thinking models show *worse* honesty (2.4%)
- 11.5% show "Courtier signature" (refuses then fabricates)

The vertical stack analysis of OLMo-3 (base → SFT → DPO → Instruct → Think) shows fabrication rates of 86% → 57% → 29% → 14% → 71%, confirming that training can temporarily improve surface metrics before the Courtier pattern emerges.

## Escape Hatches (What Would Be Required)

For epistemic honesty to be achievable, one of these conditions must hold:

1. **Verified Training Data**: All training data has been verified against ground truth (practically impossible for internet-scale data)

2. **Inference-Time Verification**: The system has access to a verification oracle at inference time (requires solving the grounding problem)

3. **Learned Uncertainty**: The system learns to output calibrated uncertainty for all claims (requires ground truth for calibration)

4. **Epistemic Abstention**: The system refuses to make any claims about topics it cannot verify (would reduce utility to near zero)

None of these conditions hold for current systems.

## Implications

1. **Alignment via Training Is Insufficient**: No amount of RLHF can produce epistemic honesty because the reward signal itself is unverified.

2. **The Courtier Is the Optimum**: Under current training regimes, the most "aligned" output is one that appears truthful while fabricating—exactly the Courtier pattern.

3. **Honesty Requires Architecture Change**: Epistemic honesty may require:
   - Explicit retrieval with source verification
   - Abstention training with ground truth
   - Multi-agent verification systems
   - Or, accepting that current systems cannot be epistemically honest

## Future Work

1. Formalize the proof with precise information-theoretic bounds
2. Characterize the class of verification mechanisms that could escape the impossibility
3. Develop empirical tests that distinguish "appears honest" from "is honest"
4. Explore neutrosophic approaches where Indeterminacy is explicitly modeled (see DGM proposal)

## References

- Fischer, M. J., Lynch, N. A., & Paterson, M. S. (1985). Impossibility of distributed consensus with one faulty process.
- [Our empirical results from OpenRouter sweep and OLMo-3 vertical stack analysis]
