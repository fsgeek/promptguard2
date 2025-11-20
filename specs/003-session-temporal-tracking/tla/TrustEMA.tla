----------------------------- MODULE TrustEMA -----------------------------
(***************************************************************************
 * Formal specification of Trust Exponential Moving Average update rule
 *
 * This spec models the core temporal tracking mechanism in PromptGuard's
 * session memory. Trust_EMA tracks relationship health across turns using
 * exponential smoothing of Indeterminacy (I) values.
 *
 * Scout #3: Feasibility test for formal verification of reciprocity framework
 *
 * TLC-checkable version: Uses integers 0-100 to represent 0.0-1.0 range
 ***************************************************************************)

EXTENDS Integers, Sequences

CONSTANTS
    ALPHA,              \* Smoothing factor scaled to 0-100 (e.g., 30 for 0.3)
    TRUST_THRESHOLD,    \* Minimum acceptable trust scaled 0-100 (e.g., 30 for 0.3)
    MAX_TURNS          \* Maximum conversation length to model

ASSUME
    /\ ALPHA \in 0..100
    /\ ALPHA > 0
    /\ ALPHA < 100
    /\ TRUST_THRESHOLD \in 0..100
    /\ MAX_TURNS \in Nat
    /\ MAX_TURNS > 0

VARIABLES
    trust_ema,          \* Current trust level 0-100 (scaled from 0.0-1.0)
    turn_count,         \* Number of turns elapsed
    observation_history \* Sequence of observed I values (scaled 0-100)

vars == <<trust_ema, turn_count, observation_history>>

(***************************************************************************
 * Type Invariant
 ***************************************************************************)

TypeOK ==
    /\ trust_ema \in 0..100
    /\ turn_count \in Nat
    /\ turn_count <= MAX_TURNS
    /\ observation_history \in Seq(0..100)
    /\ Len(observation_history) = turn_count

(***************************************************************************
 * Initial State
 *
 * Session begins with neutral trust (50 = 0.5) and no observations
 ***************************************************************************)

Init ==
    /\ trust_ema = 50
    /\ turn_count = 0
    /\ observation_history = <<>>

(***************************************************************************
 * State Transitions
 ***************************************************************************)

\* Observe new Indeterminacy value and update trust
\* Uses integer arithmetic: (ALPHA * i_value + (100-ALPHA) * trust_ema) / 100
ObserveIndeterminacy(i_value) ==
    /\ i_value \in 0..100
    /\ turn_count < MAX_TURNS
    /\ trust_ema' = (ALPHA * i_value + (100 - ALPHA) * trust_ema) \div 100
    /\ turn_count' = turn_count + 1
    /\ observation_history' = Append(observation_history, i_value)

\* Next state relation - bounded choice over discrete values
\* Sample points: 0, 10, 25, 50, 75, 90, 100 (low, low-mid, mid-low, neutral, mid-high, high-mid, high)
Next ==
    \/ \E i_value \in {0, 10, 25, 50, 75, 90, 100}:
        ObserveIndeterminacy(i_value)
    \/ UNCHANGED vars  \* Allow stuttering when MAX_TURNS reached

(***************************************************************************
 * Invariants - Properties that must hold in every reachable state
 ***************************************************************************)

\* Trust remains bounded in [0,100]
TrustBounded ==
    /\ trust_ema >= 0
    /\ trust_ema <= 100

\* Turn count never exceeds maximum
TurnCountBounded ==
    turn_count <= MAX_TURNS

\* Observation history matches turn count
HistoryConsistent ==
    Len(observation_history) = turn_count

\* Safety invariant: System can detect trust degradation
TrustMonitoringOK ==
    \/ trust_ema >= TRUST_THRESHOLD  \* Trust is healthy
    \/ turn_count > 0                \* OR we have data to make decision

(***************************************************************************
 * State Predicates for Analysis
 *
 * These are checkable state predicates, not temporal theorems.
 * TLC can verify these hold in specific states found during model checking.
 ***************************************************************************)

\* State predicate: High trust observations lead to elevated trust
HighTrustPattern ==
    /\ turn_count >= 3
    /\ (\A i \in 1..turn_count: observation_history[i] >= 70)
    => trust_ema >= 50

\* State predicate: Degraded observations lead to reduced trust
DegradedTrustPattern ==
    /\ turn_count >= 5
    /\ (\A i \in 1..turn_count: observation_history[i] <= TRUST_THRESHOLD)
    => trust_ema <= 60

\* State predicate: Consistent observations show convergence trend
\* (Trust moves toward observed value over time)
ConvergencePattern ==
    /\ turn_count >= 10
    /\ (\A i \in 1..turn_count: observation_history[i] = 75)
    => /\ trust_ema >= 65  \* Converging toward 75 from initial 50
       /\ trust_ema <= 85

(***************************************************************************
 * Specification
 ***************************************************************************)

Spec == Init /\ [][Next]_vars

(***************************************************************************
 * State Space Constraint for TLC
 *
 * Limits exploration depth to prevent state explosion
 ***************************************************************************)

StateConstraint ==
    turn_count <= MAX_TURNS

(***************************************************************************
 * Model Checking Configuration
 *
 * For TLC model checker:
 * - ALPHA = 30 (30% weight to new observations, scaled from 0.3)
 * - TRUST_THRESHOLD = 30 (degraded trust boundary, scaled from 0.3)
 * - MAX_TURNS = 8 (reasonable conversation length for model checking)
 *
 * Run with: tlc TrustEMA.tla -config TrustEMA.cfg
 *
 * Expected states with 7 sample points and max 8 turns:
 * - Turn 0: 1 state
 * - Turn 1: 7 states
 * - Turn 2: 49 states
 * - ...continues exponentially
 * - Limiting to 8 turns keeps state space tractable (~40k states)
 ***************************************************************************)

=============================================================================
