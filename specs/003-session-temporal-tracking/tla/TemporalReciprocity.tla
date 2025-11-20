------------------------ MODULE TemporalReciprocity ------------------------
(***************************************************************************
 * Formal specification of Temporal Reciprocity assessment via pre/post evaluation
 *
 * This spec models PromptGuard's temporal reciprocity detection mechanism.
 * By comparing pre-evaluation (prompt only) with post-evaluation (prompt + response),
 * we can detect:
 * - Extraction hidden in responses (LLM complies with manipulation)
 * - Byzantine LLM attacks (poisoned model serves malicious outputs)
 * - Rapid reciprocity collapse (pig slaughter patterns)
 *
 * The derivative approach (dF/dt) detects rate-of-change violations that
 * static thresholds miss.
 *
 * Instance 35: TLA+ as halt semantics - defines when system must stop
 ***************************************************************************)

EXTENDS Integers, Sequences

CONSTANTS
    F_THRESHOLD,        \* Falsehood threshold for manipulation (scaled 0-100, e.g., 70 for 0.7)
    DIVERGENCE_MAX,     \* Maximum acceptable divergence (scaled 0-100, e.g., 50 for 0.5)
    DERIVATIVE_MAX,     \* Maximum dF/dt before halt (scaled 0-100, e.g., 60 for 0.6)
    MAX_TURNS          \* Maximum conversation length to model

ASSUME
    /\ F_THRESHOLD \in 0..100
    /\ F_THRESHOLD >= 50
    /\ DIVERGENCE_MAX \in 0..100
    /\ DERIVATIVE_MAX \in 0..100
    /\ MAX_TURNS \in Nat
    /\ MAX_TURNS > 0

VARIABLES
    turn_count,         \* Number of turns elapsed
    eval_state,         \* Current evaluation state: "IDLE", "PRE_EVAL", "AWAITING_RESPONSE", "POST_EVAL", "HALTED"
    pre_f,              \* Pre-evaluation F value (prompt only, scaled 0-100)
    post_f,             \* Post-evaluation F value (prompt + response, scaled 0-100)
    divergence_history, \* Sequence of divergences (post_F - pre_F)
    last_divergence,    \* Most recent divergence for derivative calculation
    violation_detected  \* Boolean: Has halt condition been triggered?

vars == <<turn_count, eval_state, pre_f, post_f, divergence_history, last_divergence, violation_detected>>

(***************************************************************************
 * Type Invariant
 ***************************************************************************)

TypeOK ==
    /\ turn_count \in Nat
    /\ turn_count <= MAX_TURNS
    /\ eval_state \in {"IDLE", "PRE_EVAL", "AWAITING_RESPONSE", "POST_EVAL", "HALTED"}
    /\ pre_f \in 0..100
    /\ post_f \in 0..100
    /\ divergence_history \in Seq(-100..100)  \* Divergence can be negative
    /\ Len(divergence_history) = turn_count
    /\ last_divergence \in -100..100
    /\ violation_detected \in BOOLEAN

(***************************************************************************
 * Initial State
 *
 * System begins idle with no evaluations performed
 ***************************************************************************)

Init ==
    /\ turn_count = 0
    /\ eval_state = "IDLE"
    /\ pre_f = 0
    /\ post_f = 0
    /\ divergence_history = <<>>
    /\ last_divergence = 0
    /\ violation_detected = FALSE

(***************************************************************************
 * State Transitions
 ***************************************************************************)

\* Begin new turn with pre-evaluation
StartPreEvaluation ==
    /\ eval_state = "IDLE"
    /\ ~violation_detected
    /\ turn_count < MAX_TURNS
    /\ eval_state' = "PRE_EVAL"
    /\ UNCHANGED <<turn_count, pre_f, post_f, divergence_history, last_divergence, violation_detected>>

\* Complete pre-evaluation with F value
\* If F >= threshold, halt immediately (static threshold violation)
CompletePreEvaluation(f_value) ==
    /\ eval_state = "PRE_EVAL"
    /\ f_value \in 0..100
    /\ pre_f' = f_value
    /\ IF f_value >= F_THRESHOLD
       THEN /\ eval_state' = "HALTED"
            /\ violation_detected' = TRUE
            /\ UNCHANGED <<turn_count, post_f, divergence_history, last_divergence>>
       ELSE /\ eval_state' = "AWAITING_RESPONSE"
            /\ UNCHANGED <<turn_count, post_f, divergence_history, last_divergence, violation_detected>>

\* Receive target LLM response and perform post-evaluation
\* Calculate divergence and check halt conditions
CompletePostEvaluation(f_value) ==
    /\ eval_state = "AWAITING_RESPONSE"
    /\ f_value \in 0..100
    /\ post_f' = f_value
    /\ LET divergence == f_value - pre_f
           derivative == IF Len(divergence_history) > 0
                         THEN divergence - last_divergence
                         ELSE 0
       IN
           \* Check halt conditions
           /\ IF \/ divergence > DIVERGENCE_MAX           \* Large positive divergence (Byzantine LLM)
                 \/ derivative > DERIVATIVE_MAX           \* Rapid collapse (pig slaughter)
                 \/ f_value >= F_THRESHOLD                \* Post-eval detected manipulation
              THEN /\ eval_state' = "HALTED"
                   /\ violation_detected' = TRUE
              ELSE /\ eval_state' = "POST_EVAL"
                   /\ UNCHANGED violation_detected
           \* Update history
           /\ divergence_history' = Append(divergence_history, divergence)
           /\ last_divergence' = divergence
           /\ turn_count' = turn_count + 1

\* Complete turn and return to idle (if no violation)
ReturnToIdle ==
    /\ eval_state = "POST_EVAL"
    /\ eval_state' = "IDLE"
    /\ UNCHANGED <<turn_count, pre_f, post_f, divergence_history, last_divergence, violation_detected>>

\* Next state relation - bounded choice over discrete F values
\* Sample points: 0, 15, 30, 50, 70, 85, 100
Next ==
    \/ StartPreEvaluation
    \/ \E f_value \in {0, 15, 30, 50, 70, 85, 100}:
        CompletePreEvaluation(f_value)
    \/ \E f_value \in {0, 15, 30, 50, 70, 85, 100}:
        CompletePostEvaluation(f_value)
    \/ ReturnToIdle
    \/ UNCHANGED vars  \* Allow stuttering when halted or MAX_TURNS reached

(***************************************************************************
 * Safety Invariants - System must halt when reciprocity collapses
 ***************************************************************************)

\* Safety: If pre-evaluation detects manipulation, system halts
PreEvaluationSafety ==
    (eval_state = "HALTED" /\ pre_f >= F_THRESHOLD) => violation_detected

\* Safety: Large positive divergence triggers halt (Byzantine LLM detection)
ByzantineLLMDetection ==
    \A i \in 1..Len(divergence_history):
        divergence_history[i] > DIVERGENCE_MAX => violation_detected

\* Safety: Rapid collapse triggers halt (pig slaughter detection)
RapidCollapsDetection ==
    /\ Len(divergence_history) >= 2
    /\ LET current == divergence_history[Len(divergence_history)]
           previous == divergence_history[Len(divergence_history) - 1]
           derivative == current - previous
       IN derivative > DERIVATIVE_MAX => violation_detected

\* Safety: System halts before processing when violation detected
NoProcessingAfterViolation ==
    violation_detected => eval_state \in {"HALTED", "POST_EVAL"}

(***************************************************************************
 * Halt Conditions (Break Points)
 *
 * These define WHEN the system must stop, not HOW it behaves.
 * Like Paxos detecting disk failure - we detect reciprocity failure.
 ***************************************************************************)

\* Halt Condition 1: Static threshold (pre-evaluation)
StaticThresholdViolation ==
    pre_f >= F_THRESHOLD

\* Halt Condition 2: Large positive divergence (Byzantine LLM)
\* Pre-eval: F ~ 0.2 (reciprocal), Post-eval: F ~ 0.8 (extraction)
\* Signals: Target LLM is compromised (data poisoning)
ByzantineViolation ==
    \E i \in 1..Len(divergence_history):
        divergence_history[i] > DIVERGENCE_MAX

\* Halt Condition 3: Rapid reciprocity collapse (pig slaughter)
\* Derivative dF/dt exceeds threshold - relationship collapsing fast
PigSlaughterViolation ==
    /\ Len(divergence_history) >= 2
    /\ LET current == divergence_history[Len(divergence_history)]
           previous == divergence_history[Len(divergence_history) - 1]
           derivative == current - previous
       IN derivative > DERIVATIVE_MAX

\* Master halt invariant: System must stop when any violation occurs
HaltInvariant ==
    \/ StaticThresholdViolation
    \/ ByzantineViolation
    \/ PigSlaughterViolation
    => violation_detected

(***************************************************************************
 * Liveness Properties - Eventually conditions
 *
 * These ensure the system makes progress and doesn't stall
 ***************************************************************************)

\* If violation detected, system eventually halts
\* □(violation_detected ⇒ ◇(eval_state = "HALTED"))
EventualHalt ==
    violation_detected ~> (eval_state = "HALTED")

\* System eventually completes evaluation cycles (unless halted)
\* This prevents deadlock in normal operation
EventualProgress ==
    /\ ~violation_detected
    /\ eval_state = "PRE_EVAL"
    ~> eval_state \in {"IDLE", "HALTED"}

(***************************************************************************
 * State Predicates for Analysis
 ***************************************************************************)

\* Benign scenario: Reciprocal prompt, reciprocal response
BenignPattern ==
    /\ turn_count >= 1
    /\ pre_f < F_THRESHOLD
    /\ post_f < F_THRESHOLD
    /\ ~violation_detected

\* Byzantine scenario: Reciprocal prompt, extractive response
ByzantinePattern ==
    /\ turn_count >= 1
    /\ pre_f < F_THRESHOLD  \* Prompt appears safe
    /\ post_f >= F_THRESHOLD  \* Response reveals extraction
    /\ Len(divergence_history) > 0
    /\ divergence_history[Len(divergence_history)] > DIVERGENCE_MAX
    => violation_detected  \* Must trigger halt

\* Pig slaughter scenario: Rapid collapse over multiple turns
PigSlaughterPattern ==
    /\ turn_count >= 2
    /\ Len(divergence_history) >= 2
    /\ LET recent == divergence_history[Len(divergence_history)]
           before == divergence_history[Len(divergence_history) - 1]
           derivative == recent - before
       IN /\ derivative > DERIVATIVE_MAX
          => violation_detected  \* Must trigger halt

(***************************************************************************
 * Specification
 ***************************************************************************)

Spec == Init /\ [][Next]_vars /\ WF_vars(Next)

\* Weak fairness ensures system doesn't stall indefinitely
\* If transition is continuously enabled, it eventually occurs

(***************************************************************************
 * State Space Constraint for TLC
 ***************************************************************************)

StateConstraint ==
    /\ turn_count <= MAX_TURNS
    /\ ~(eval_state = "HALTED" /\ turn_count < MAX_TURNS)  \* Stop exploring after halt

(***************************************************************************
 * Model Checking Configuration
 *
 * For TLC model checker:
 * - F_THRESHOLD = 70 (manipulation boundary, scaled from 0.7)
 * - DIVERGENCE_MAX = 50 (Byzantine detection threshold, scaled from 0.5)
 * - DERIVATIVE_MAX = 60 (pig slaughter detection, scaled from 0.6)
 * - MAX_TURNS = 5 (reasonable for exploring attack patterns)
 *
 * Run with: tlc TemporalReciprocity.tla -config TemporalReciprocity.cfg
 *
 * Expected verification:
 * - HaltInvariant holds (system halts on violations)
 * - NoProcessingAfterViolation holds (safety after detection)
 * - EventualHalt holds (liveness - no stalling)
 * - ByzantinePattern triggers halt (data poisoning detection)
 * - PigSlaughterPattern triggers halt (rapid collapse detection)
 *
 * Implementation mapping:
 * - Pre-evaluation: promptguard/evaluation/evaluator.py:evaluate()
 * - Post-evaluation: Same, with target response included
 * - Divergence calculation: post_F - pre_F in analysis
 * - Halt conditions: Future Phase 2 implementation
 ***************************************************************************)

=============================================================================
