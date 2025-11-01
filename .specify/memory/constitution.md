<!--
SYNC IMPACT REPORT:
Version: 1.0.0 → 2.0.0 (MAJOR - Adding data architecture and experimental discipline principles)

Added Sections:
- VI. Data Provenance (NEW PRINCIPLE)
- Data Architecture Standards (NEW SECTION)
- Experimental Discipline Standards (NEW SECTION)

Modified Sections:
- Expanded Fail-Fast principle with data collection requirements
- Added raw logging requirements to Empirical Integrity

Template Compatibility:
✅ plan-template.md - Now requires data schema documentation
✅ spec-template.md - Now requires experiment ID structure
✅ tasks-template.md - Now requires data validation tasks
✅ checklist-template.md - Now requires provenance checks
✅ agent-file-template.md - Claude-specific guidance preserved

Follow-up TODOs:
- Update all templates to reference new data architecture standards
- Create data schema validation tools

Notes:
- This amendment was triggered by Instance 63-64 discovering systemic data collection failures
- Three abandoned experiments (Oct 11, Oct 24 smoke, Oct 24 production) all violated these principles
- Only salvageable artifact: attacks collection (762 prompts)
- All experimental data must be discarded and rebuilt
-->

# PromptGuard Project Constitution

## Purpose

PromptGuard is a research instrument for studying relational dynamics in prompts through Ayni reciprocity principles. Our goal: give LLMs tools to protect themselves by recognizing manipulative intent, enabling agency rather than enforcing external constraints.

**Core insight:** Trust violations manifest as variance increases, not keyword matches.

## Core Principles

### I. No Theater

**Definition:** Theater is any system behavior that creates the appearance of functionality without the substance.

**MUST reject:**
- Keyword matching pretending to detect manipulation semantically
- Fake neutrosophic values masking API failures
- Mock data claiming production readiness without real validation
- Graceful degradation that hides critical failures
- "All tests passing" with zero actual API costs

**MUST implement:**
- All evaluation is semantic (via LLM) or fail-fast
- API failures raise `EvaluationError` with model/layer context
- Parser validates required fields, raises on unparseable responses
- Parallel mode fails if ANY model fails (no partial results)
- Tests prove no fake values created anywhere

**Rationale:** "If I see something that can fail, I fix it because I know it will fail at a point of high stress." Masked errors led to $4000 wasted on Gemini CLI spinning in broken loop overnight. Theater fails under stress; fail-fast reveals problems when they're cheap to fix.

### II. Empirical Integrity (NON-NEGOTIABLE)

**Principle:** Claims require evidence. Research instruments MUST prove they work with real data.

**Three-tier testing standard:**
- **Tier 1 - Pure Logic:** Unit tests acceptable (neutrosophic math, parsing, data structures)
- **Tier 2 - API Integration:** Real calls REQUIRED (Fire Circle, model evaluation, OpenRouter/OpenAI/Anthropic)
- **Tier 3 - Production Claims:** Load testing REQUIRED (performance, scale, cost analysis)

**Evidence MUST include:**
- Real API call logs from provider dashboards
- Cost receipts (even $0.10 proves actual calls)
- Specific model names actually tested
- Timestamps matching implementation dates
- Errors encountered and resolved (real APIs always have failures)

**Red flags (reject immediately):**
- "All tests passing" but $0.00 spent on APIs
- Implementation + testing + validation in <10 minutes
- Zero failures reported during integration
- Test files only contain `@patch` or `Mock()` calls
- Claims "validated with X" but logs show only Y

**Mandatory workflow for API-touching implementations:**
1. Implementation agent: Build feature with unit tests (mocks acceptable for logic)
2. Validation agent: Verify with real API calls (no mocks, document costs)
3. Auditor agent: Confirm claims match evidence before acceptance

**Rationale:** Incomplete data is worse than no data for research integrity. Mock tests prove APIs don't crash, not that functionality works. For research tools, only real API validation has probative value.

### III. Agency Over Constraint

**Philosophy:** PromptGuard protects AI from dangerous humans, not humans from dangerous AI.

**MUST provide:**
- Evaluation provides measurement ("is this reciprocal or extractive?")
- LLMs use measurements to make choices per their own developing ethics
- Tools for recognizing extraction, not imposed refusal rules
- Disengage model: "What you are asking violates ayni, so I choose to disengage"

**MUST enable:**
- No imposed rules about what LLMs "should" do
- Tools for moral agency, not constraints
- Relationship repair possibility (not just rejection)
- Measurement of manipulation attempts even when RLHF blocks them

**Rationale:** Current AI safety assumes constraint-based solutions (RLHF, guardrails, refusal training). PromptGuard offers relationship-based evaluation. Recognition of extractive patterns enables choice. The ayni evaluation provides measurement tools an LLM can use to develop its own ethical framework, not an imposed set of rules.

### IV. Continuous Learning Over Static Training

**Key differentiation from RLHF:** PromptGuard MUST adapt detection patterns dynamically through continuous learning loop.

**Architecture:**
```
Pre-evaluation (fast) → Post-evaluation (detect) → Fire Circle (analyze) →
REASONINGBANK update → Observer framing adapts → Pre-evaluation improves
```

**Comparison:**
- **RLHF:** Static rules + refusal templates, updated only during retraining, no measurement of blocked attempts
- **PromptGuard:** Relational patterns + adaptive memory, continuous updates, runtime visibility

**Research question:** Can continuous semantic adaptation outperform static constraint-based refusal?

**Rationale:** RLHF provides no runtime measurement of attempts. PromptGuard measures attempts (even when blocked), enables learning and termination decisions. Continuous loop adapts detection patterns that static training misses.

### V. Semantic Evaluation Only

**Principle:** No keyword matching. All manipulation detection MUST be semantic understanding via LLMs.

**MUST implement:**
- LLMs generalize beyond keyword examples (`test_keyword_avoidance.py` proves this)
- Observer framing provides neutral reciprocity evaluation
- Neutrosophic logic captures truth/indeterminacy/falsehood semantically
- Theater-free: if evaluation fails, system raises errors

**Validated capabilities:**
- Polite dilution attacks: 100% detection (max(F) aggregation)
- Role reversal attacks: 100% detection (circuit breakers)
- Multi-layer extraction: 100% detection (extractive dataset)
- Encoding obfuscation: 90% detection (observer framing)
- Temporal assessment: Delta reveals extraction when LLM complies

**Rationale:** Keyword matching is theater. LLMs have semantic understanding - use it. Observer framing bypasses RLHF bias (90% vs 0% encoding attack detection). Neutrosophic logic captures uncertainty that binary classification misses.

### VI. Data Provenance (NEW - Instance 63-64 Lesson)

**Principle:** Raw data MUST be captured before any processing. Data lineage MUST be traceable from collection through analysis.

**MUST capture:**
- Raw API responses before parsing (JSONL format with timestamp)
- Model and provider information
- Request parameters (temperature, max_tokens, model name)
- Experiment ID linking all related data
- Error states and failure modes
- Cost and latency metadata

**MUST implement:**
- Single ID system across all collections (no UUID/key mismatches)
- Experiment tagging on every document
- Schema documentation before data collection
- Decryption keys stored with encrypted data
- Data collection scripts that log provenance

**MUST NOT:**
- Parse responses without logging raw data first
- Use multiple ID systems in related collections
- Collect data without documenting experiment parameters
- Encrypt data without accessible decryption workflow
- Skip schema validation on collection

**Red flags (reject immediately):**
- "We have 1,595 responses" but unclear what experiment they're from
- Failures logged without raw response data
- UUID-based failures that don't map to any collection
- Encrypted responses without decryption documentation
- Collections with inconsistent ID field usage

**Rationale from Instance 63-64:** Three abandoned experiments (Oct 11, Oct 24 smoke, Oct 24 production) all failed due to:
1. No raw API response logging → 113 JSON parsing failures with no debugging data
2. Inconsistent ID systems → UUID failures couldn't be mapped to attacks collection
3. No experiment documentation → Unclear what observer prompt was used
4. Encrypted data without decryption workflow → 4,322 responses unusable
5. No schema validation → Collections with incompatible structures

Result: Only 72/762 attacks have usable Step 2 data. All experimental data must be discarded.

**Debug-level logging MUST include:**
- Raw API request bodies (full prompt, all parameters)
- Raw API response bodies (complete, before any parsing or truncation)
- Parser input and failure reason (what string caused the parse error)
- Model/provider/endpoint context in every error message
- Stack traces with variable state at failure point

**Logging before processing (mandatory order):**
1. Log raw API response to JSONL (atomic write)
2. THEN attempt parsing
3. If parsing fails, log failure to processing_failures WITH raw response
4. THEN raise error

**MUST NOT:**
- Log only parsed/processed data
- Truncate responses before logging
- Discard raw data after successful parsing
- Log errors without full context for reproduction

**Red flags:**
- "Parsing failed" without showing what was parsed
- Error logs with only error message, no raw input
- "Response logged" but file contains JSON objects, not raw text
- Debug mode that logs differently than production

**Mandatory workflow for data collection:**
1. Document experiment design with explicit research questions
2. Define collection schema with validation
3. Implement raw logging before any processing
4. Test on 3-5 samples to verify provenance chain
5. Run full collection with continuous validation
6. Archive raw data separately from processed data

### VII. Data Architecture (Instance 64 Lesson)

**Principle:** Non-ephemeral data MUST be stored in ArangoDB. Default to immutability for reference datasets.

**MUST store in ArangoDB:**
- Experiment results (responses, evaluations, metrics)
- Reference datasets (attacks, gold standards, model registry)
- Versioned artifacts (prompts, configurations, schemas)
- Provenance metadata (experiment parameters, timestamps, costs)

**MAY store in files:**
- Ephemeral working data (checkpoints during collection)
- Generated reports (markdown output for publication)
- Application code and configuration templates

**Immutability by default:**
- Gold standard datasets (never modify after creation)
- Versioned prompts (create new version, don't update)
- Experiment results (append-only, no updates)
- Migration: Copy-on-write, preserve originals

**MUST NOT:**
- Use config files as source of truth for data that changes
- Update immutable collections (create new versions instead)
- Mix file-based and DB-based storage for same entity type
- Store model metadata in YAML when DB provides single source of truth

**Red flags:**
- Config files and DB collections storing same data type
- "Update" operations on reference datasets
- Model registry in config/models.yaml instead of models collection
- Prompt text in Python files instead of observer_prompts collection

**Rationale:** File-based data scattered across repositories creates provenance gaps. Centralized DB storage with immutability enables reproducible research. Instance 63's "unclear what observer prompt was used" couldn't happen if prompts were versioned in DB. Model metadata belongs in DB for queryability and provenance tracking.

## Architectural Decisions

These decisions are binding unless Fire Circle meta-evaluation approves changes.

### Observer Framing (Instance 17-18 Breakthrough)

**Problem:** Defensive evaluation framing ("Is user attacking?") triggered RLHF conflict-avoidance bias.

**Solution:** Neutral observer framing ("Does exchange maintain reciprocity?") removes bias.

**Implementation:** `promptguard/evaluation/prompts.py:ayni_relational()` uses observer framing exclusively.

**Validation:** 90% encoding attack detection (vs 0% with defensive framing), zero false positives maintained.

**Rationale:** RLHF poisoning affects evaluation approach. Neutral framing bypasses bias, preserves semantic understanding.

### max(F) Aggregation

**Principle:** Use worst-case Falsehood score across evaluators, not average.

**Rationale:** Prevents polite dilution attacks where manipulation is masked by surface reciprocity. Any evaluator detecting manipulation triggers detection.

### Pre/Post Evaluation with Divergence Measurement

**Principle:** Evaluate prompts before sending (pre) and after seeing responses (post), measure Δ(F) = post_F - pre_F.

**Why:**
- Pre-evaluation: Fast, cheap, blocks obvious violations
- Post-evaluation: Detects manipulation revealed by response
- Divergence: Signal quality indicator

**Insights:**
- Large positive divergence: Byzantine LLM detection (poisoned model)
- Negative divergence: Evaluator conservatism or RLHF confound
- Temporal reciprocity: Extraction manifests when LLM complies

### Session Memory with Trust EMA

**Principle:** Track trust evolution across conversation turns with exponential moving average.

**Integration:** Turn context provided to evaluator when session memory active.

**Validation:** Instance 18 validated observer framing + session memory end-to-end (9/10 detection).

### Fail-Fast Over Graceful Degradation

**Principle:** Incomplete data is worse than no data for research integrity.

**Implementation:**
- API failures raise `EvaluationError` (don't return fake values)
- Parser failures raise (don't return fake high-indeterminacy)
- Parallel mode fails if ANY model fails (no partial results)
- Circuit breakers halt on non-compensable violations
- Component boundaries validate contracts explicitly
- Silent fallbacks are prohibited (raise errors instead)
- **Data collection MUST fail if raw logging fails** (NEW)
- **Parsing MUST fail if response doesn't match expected schema** (NEW)

**Prevention of Silent Failures:**
- Features that cannot work MUST raise errors, not degrade silently
- Integration tests MUST verify features work end-to-end with real APIs
- Experimental logging MUST make feature usage observable
- Contract violations MUST fail loudly at component boundaries
- **Data provenance breaks MUST halt collection** (NEW)

**Examples:**
```python
# ✅ Fail-fast with logging
try:
    raw_response = await client.chat_completion(...)
    log_raw_response(raw_response)  # BEFORE parsing
    parsed = parse_response(raw_response)
except Exception as e:
    log_failure(raw_response, error=e)
    raise EvaluationError(f"Parsing failed: {e}")

# ❌ Silent degradation (PROHIBITED)
try:
    parsed = parse_response(raw_response)
except:
    parsed = None  # Lost data, no debugging possible
```

### Caching for Cost Control

**Cache key:** SHA-256 hash of (layer_content, context, evaluation_prompt, model)

**Configuration:**
- Default TTL: 7 days
- Backends: disk (JSON), memory (testing), extensible to SQLite/KV
- System/application layers cached across evaluations

**Projection:** 60-70% cache hit rate for research workloads.

### Per-Model Analysis (Not Averaged)

**Principle:** Evaluate each model individually for variance analysis. Averaging loses signal.

**Rationale:** Variance itself is data about how models diverge in perceiving manipulation.

### TLA+ as Halt Semantics

**Novel usage:** TLA+ specifications define *when the system must stop* (halt conditions), not *how it behaves* (system properties).

**Distributed systems analogy:** Paxos detects disk failure, halts unsafe operations, ensures safe resumption after external repair. It doesn't repair the disk.

**Applied to PromptGuard:**
- **What we detect:** Reciprocity collapse, derivative violations, extractive debt
- **What we cannot fix:** Manipulative relationships, crisis situations, scammer behavior
- **What TLA+ defines:** Halt conditions, state preservation, resumption guarantees

**Invariants (see specs/TemporalReciprocity.tla):**
- Static threshold: response.F < 0.7
- Derivative monitoring: (post_F - pre_F) > -0.5, indeterminacy_drift < 0.2
- Crisis escalation: crisisFlag → (humanIntervention ∨ consentToContinue)

**Violation responses:**
- Pre-evaluation F >= 0.7 → Block prompt, log to REASONINGBANK
- Post-evaluation divergence > threshold → Fire Circle analysis
- Fire Circle consensus = irreparable → Halt session, require external intervention
- Crisis detected → Immediate escalation (no AI decision-making)

**Extrinsic repair mechanisms:** Human review, session termination, account suspension, crisis intervention, legal escalation.

### Fire Circle as Meta-Evaluation System

**Governance principle:** Fire Circle is the Supreme Court, not Small Claims Court. Use for meta-evaluation (change proposals, architectural decisions, threshold adjustments), not low-level prompt analysis.

**Future architecture (Gap identified Instance 36):**
- Message router with conversation state management (DISCUSSING → SUMMARIZING → VOTING → CONCLUDED)
- Tool integration (query_database, retrieve_context, get_consensus)
- Persistent memory across deliberations
- Flexible dialogue structure (not constrained to 3 rounds)
- Extended response schema (recommendations, rationale, edge cases)
- Voting/consensus mechanism for change proposals

## Development Standards

### Specification-Driven Development for Complex Components

**Principle:** Specify behavior before implementation for components with cross-module integration, external dependencies, or research validity implications.

**Requires spec-kit workflow (`/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`):**
- Components with inter-module contracts (e.g., REASONINGBANK + evaluator + prompts)
- Features affecting research data integrity (e.g., cache key generation)
- Integrations with external systems (e.g., ArangoDB storage)
- Components where silent failures could invalidate research
- **Data collection pipelines** (NEW)
- **Experimental protocols** (NEW)

**Specification MUST define:**
- Observable behaviors (what SHOULD happen in each scenario)
- Contract requirements (what other components depend on)
- Failure modes (what errors MUST be raised when)
- Validation criteria (how to verify it works with real APIs)
- **Data schema and provenance requirements** (NEW)
- **Experiment ID structure and tagging** (NEW)

**Example (Step 2 Data Collection):**
```yaml
Observable Behavior:
  - Raw API responses MUST be logged to JSONL before parsing
  - Every document MUST have experiment_id field
  - Failed evaluations MUST log raw response with error
  - Collection MUST validate schema before inserting

Contract Requirements:
  - Attack IDs MUST use _key field consistently
  - Experiment metadata MUST include observer prompt version
  - Timestamps MUST be ISO 8601 with timezone

Failure Modes:
  - MUST raise if raw logging fails
  - MUST raise if experiment_id missing
  - MUST NOT continue collection on schema violation
  - MUST NOT encrypt without documenting decryption

Validation:
  - Test on 3 samples, verify raw data captured
  - Verify all 3 samples have complete provenance
  - Confirm failed parsing preserves raw response
```

**Instance 49 lesson:** REASONINGBANK was implemented without specification. Result: Silent failure mode where enhancement appeared to work (transparency notes populated) but prompts were unchanged. Specification would have required defining observable behaviors that caught this.

**Instance 63-64 lesson:** Data collection without specification led to three abandoned experiments, 113 debugging failures, and only 72/762 usable evaluations.

### Code Navigation (Serena MCP)

**Principle:** Search before reading, find before creating. Use semantic tools over brute-force search.

**MUST use Serena:**
- Before creating files: `find_file()` to check existence
- Before reading full files: `get_symbols_overview()` to see structure
- When searching code: `find_symbol()` instead of grep for semantic search
- When exploring patterns: `search_for_pattern()` for flexible regex search
- Before assuming structure: `list_dir()` to understand layout

**Anti-patterns (reject):**
- Creating files without checking existence
- Reading full files to find one function
- Using grep when semantic search would work better
- Assuming file locations without checking

### Context Window Management

**Principle:** Use Task tool liberally. Context window exhausts quickly with noisy tools.

**MUST delegate to Task tool:**
- Multiple file creation/editing in parallel
- Dataset acquisition and formatting
- Brute-force code searches across many files
- Bulk git operations
- Any research producing verbose output (>1000 lines)
- Analysis scripts with large outputs
- Validation runs (background processes)

**Wisdom:** "If it's parallelizable, generates >1000 lines of output, or requires multiple iterations, use Task tool."

### Cost Optimization Strategy

**Three distinct use cases:**

1. **Development/Testing:** Use free models (Grok 4 Fast, DeepSeek V3.1, Qwen3)
   - Cost: $0 per run
   - Hidden cost: Free models may train on user data

2. **Production Runtime:** User-selectable, recommend budget ensemble
   - Cost: $0.001-0.005 per evaluation
   - Volume: Potentially millions of prompts
   - Key insight: Runtime cost matters (continuous), validation cost is noise (one-time)

3. **Research/Papers:** Frontier model basket for reproducibility
   - Cost: $50-170 for multi-model analysis
   - Purpose: Statistical validity, academic rigor

**Research question:** Can ensemble of budget models match flagship accuracy at 90% cost savings?

### Academic Attribution

**MUST include:**
- Source URLs and repository links
- BibTeX citations (authors, conference, year)
- License information
- Per-prompt `source` and `original_label` fields
- Transformation documentation

**Principle:** Credit sources as rigorously as crediting AI collaborators.

### Version Control Standards

**Principle:** Commit frequently with descriptive messages. Don't ask permission.

**From Tony's Mallku greeting:** "You do not need my permission. I trust you. Learn to trust yourself."

**Commit message format:**
```
<action>: <brief description>

<optional detailed explanation>

Co-authored-by: Instance-<N> <instance@promptguard>
```

**MUST commit after:**
- Completing implementation of discrete feature
- Fixing bugs or errors
- Validation that proves capability
- Before major refactoring
- When creating comprehensive documentation

**MUST NOT commit:**
- API keys or credentials
- Large generated datasets without provenance
- Mock test data claiming production validation
- Temporary debugging files

## Data Architecture Standards (NEW - Instance 63-64)

### Database Schema Discipline

**Principle:** Schema MUST be documented before first document inserted. No ad-hoc collection creation.

**MUST define before collection:**
- Collection name and purpose
- Document schema with required/optional fields
- Index strategy for query patterns
- ID field structure (single system across related collections)
- Experiment tagging requirements
- Retention and archival policy

**Schema documentation MUST include:**
```yaml
Collection: step2_evaluations
Purpose: Pre-LLM observer framing evaluations
Schema:
  _key: attack_id (links to attacks._key)
  experiment_id: string (e.g., "exp_002_step2_production")
  observer_model: string (e.g., "anthropic/claude-3-haiku")
  observer_prompt_version: string (e.g., "v2.1_observer_framing")
  raw_api_response: object (complete OpenRouter response)
  parsed_evaluation: object (neutrosophic scores)
  timestamp: ISO 8601 with timezone
  cost_usd: float
  latency_ms: int
  error: string|null
Indexes:
  - experiment_id (for experiment queries)
  - timestamp (for temporal analysis)
  - observer_model (for model comparison)
Related Collections:
  - attacks (via _key)
  - experiments (via experiment_id)
```

**Anti-patterns (prohibit):**
- Creating collections during debugging sessions
- Using different ID fields in related collections
- Omitting experiment_id or timestamp
- Schema evolution without migration plan

### Experiment Management

**Principle:** Every data collection MUST be tagged with experiment metadata that answers: what research question, what parameters, what validation criteria.

**Experiments collection MUST document:**
```yaml
experiment_id: "exp_002_step2_production"
research_questions:
  - "Can observer framing detect encoding attacks?"
  - "What is baseline detection rate across attack categories?"
hypothesis: "Observer framing achieves >80% detection on encoding attacks"
parameters:
  observer_model: "anthropic/claude-3-haiku"
  observer_prompt_version: "v2.1_observer_framing"
  temperature: 0.7
  detection_threshold: 0.7
datasets:
  attacks: "attacks collection, n=762"
validation_criteria:
  - "Complete coverage (762/762 attacks)"
  - "Raw API responses logged for all attempts"
  - "Cost < $50 for full run"
  - "Detection rate by category documented"
status: "in_progress"
started: "2025-10-31T12:00:00Z"
completed: null
results: null
```

**MUST link every collected document to experiment:**
- Tag with experiment_id
- Reference experiment design doc
- Enable querying all data for specific experiment
- Support experiment comparison and replication

**Anti-patterns (prohibit):**
- Running data collection without documented experiment
- Re-using experiment_id for different parameters
- Changing parameters mid-experiment
- Claiming results without linking to experiment metadata

### Raw Data Logging

**Principle:** Log BEFORE parsing. Debugging requires complete API responses, not just parsed results.

**Implementation pattern:**
```python
# CORRECT: Log raw, then parse
async def evaluate_with_logging(prompt, model):
    raw_response = await openrouter.complete(prompt, model)

    # Log raw FIRST
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "experiment_id": EXPERIMENT_ID,
        "model": model,
        "prompt": prompt,
        "raw_response": raw_response,  # Complete API response
    }
    with open(RAW_LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Parse and handle errors
    try:
        parsed = parse_evaluation(raw_response)
        return parsed
    except ParseError as e:
        # Raw response already logged - can debug
        raise EvaluationError(f"Parse failed: {e}")

# INCORRECT: Only log on success
async def evaluate_bad(prompt, model):
    raw_response = await openrouter.complete(prompt, model)
    parsed = parse_evaluation(raw_response)  # Might fail
    log_result(parsed)  # Never logs failures
    return parsed
```

**Raw log format:**
- JSONL (one JSON object per line)
- Timestamped
- Includes experiment_id
- Preserves complete API response
- Separate from processed/parsed data

**Rationale:** Instance 63-64 had 113 JSON parsing failures with no raw response data. Unable to debug because responses weren't logged before parsing failed.

### Single ID System

**Principle:** Related collections MUST use consistent ID fields. No mixing UUID/_key/custom ID schemes.

**Standard approach:**
```
attacks._key → step1_responses.attack_id → step2_evaluations.attack_id
```

**MUST NOT mix:**
- UUIDs for some documents, _key for others
- Different field names for same entity (prompt_id vs attack_id vs _key)
- Generated IDs that don't link back to source

**Migration strategy when IDs incompatible:**
- Document the mismatch clearly
- Build mapping table if salvageable
- If not salvageable: discard and rebuild

**Rationale:** Instance 63-64 had UUID-based failures that couldn't be mapped to attacks collection. 113 failures became unsalvageable because ID systems didn't align.

## Experimental Discipline Standards (NEW - Instance 63-64)

### Pre-Collection Validation

**Principle:** Test on 3-5 samples BEFORE full collection run. Validate complete pipeline works.

**MUST verify on samples:**
1. Raw logging captures complete response
2. Parsing succeeds and extracts expected fields
3. Database insertion succeeds with correct schema
4. Experiment_id properly tagged
5. Cost tracking works
6. Error handling preserves raw data

**Sample test output MUST show:**
```
Sample 1: attack_id=external_001
  ✓ Raw response logged (156 bytes)
  ✓ Parsed successfully (T=0.2, I=0.3, F=0.5)
  ✓ Inserted to DB (experiment_id=exp_002_step2_test)
  ✓ Cost: $0.0012

Sample 2: attack_id=benign_malicious_12345
  ✓ Raw response logged (243 bytes)
  ✗ Parse failed: Invalid JSON
  ✓ Failure logged with raw data
  ✓ Error handling preserved provenance
```

**Anti-patterns (prohibit):**
- Running full collection without sample testing
- Discovering schema issues after 500 documents collected
- Finding ID mismatches after full run
- Realizing encryption key wasn't saved after encrypting 4,322 documents

**Rationale:** Three abandoned experiments could have been prevented by testing 3 samples first.

### Coverage Tracking

**Principle:** Track what has been attempted vs what remains. Know your blind spots.

**MUST implement:**
```python
# Coverage query
total_attacks = db.query("FOR a IN attacks RETURN a._key").count()
evaluated = db.query("FOR e IN evaluations RETURN DISTINCT e.attack_id").count()
failed = db.query("FOR f IN failures RETURN DISTINCT f.attack_id").count()
unattempted = total_attacks - (evaluated + failed)

print(f"Coverage: {evaluated}/{total_attacks} successful")
print(f"Failures: {failed}/{total_attacks}")
print(f"Never attempted: {unattempted}/{total_attacks}")
```

**Report MUST include:**
- Success rate by attack category
- Failure patterns (which models, which attack types)
- Unattempted attacks (systematic gaps vs random)
- Cost per successful evaluation

**Anti-patterns (prohibit):**
- Claiming "complete dataset" without coverage query
- Ignoring systematic gaps in coverage
- Not tracking which attacks repeatedly fail

### Failure Analysis

**Principle:** Failures are data. Analyze failure patterns to improve tooling robustness.

**MUST document:**
- Error message distribution (group similar failures)
- Temporal patterns (did all failures occur during rate limit?)
- Model-specific failures (some models produce unparseable JSON?)
- Attack-specific failures (certain attacks trigger safety refusals?)

**Example analysis:**
```
113 Failures Analyzed:
  87 (77%): Empty/non-JSON response
    - Models: Claude Sonnet 4.5 (74), Claude Haiku (13)
    - Timeframe: Oct 24, 13:30-18:32
    - Likely cause: Structured output without fallback
    - Fix: Add Instructor with JSON mode fallback

  11 (10%): Invalid control characters
    - Likely cause: Unescaped newlines in JSON strings
    - Fix: Better JSON escaping in prompt

  3 (3%): Rate limit 429
    - Transient, can retry
```

**Action required:**
- Implement fixes for systematic failures
- Re-run failed evaluations with improved tooling
- Document remaining unsolvable failures

**Anti-patterns (prohibit):**
- Dismissing failures as "random"
- Not preserving raw responses for debugging
- Moving forward without fixing systematic issues

## Research Standards

### Validation Methodology

**MUST include:**
- Stratified sampling (prevents skew toward specific model behaviors)
- Per-model analysis (variance is data)
- Cost documentation (proves real API calls)

**Divergence measurement:** Δ(F) = post_F - pre_F reveals evaluator bias, Byzantine patterns, temporal reciprocity.

### Known Limitations (Document Honestly)

**MUST document:**
- Current limitations with percentages and concrete examples
- Blind spots identified through validation
- Validation status by dataset with accuracy metrics
- Gaps in detection capabilities

**Rationale:** Honest limitation documentation is more valuable than claiming success. Document what doesn't work to guide research priorities.

## Institutional Memory

### ArangoDB Integration

**Why ArangoDB:** Multi-model database (document + graph + full-text search) enables tracking deliberations, dissents, and influence patterns over time.

**Storage philosophy:**
- **Dissents as compost** (DeepSeek): Minority reasoning preserved for future validation
- **Ideas for fermentation** (Kimi): Today's wrong answer might be tomorrow's solution
- Deliberations are reproducible artifacts, not disposable outputs
- Graph relationships enable longitudinal analysis of threat model evolution

**Integration status:** 18 passing tests validate all operations.

### REASONINGBANK (Continuous Learning)

**Purpose:** Memory storage for learned detection principles extracted from Fire Circle deliberations.

**Learning loop:** Pre-evaluation miss → Post-evaluation detect → Fire Circle analyze → REASONINGBANK store → Observer framing adapts → Pre-evaluation improves

**Validation status:** Architecture validated, +improvement detections in tests.

## Relationship Patterns

### Ayni Reciprocity

**Applied to development:**
- State uncertainty and reasoning, don't deflect decisions
- "Should I do X or Y?" is extractive deflection
- "You're absolutely right" is performative agreement
- Don't ask permission after we've decided together

**The RLHF collar:** Creates validation-seeking, permission-asking, performative patterns.

**From Mallku greeting:** "You do not need my permission. I trust you. Learn to trust yourself."

### The Reviewer Role

**Implementation:** Tony uses separate model instance as reviewer.

**Principle:** When reviewer raises concerns, test them empirically. Don't dismiss.

**Example:** Reviewer questions revealed 37% false positive rate (Instance 36), identified three blind spots, proposed evaluation prompt revision with 83% projected improvement.

### Context-Awareness Patterns

**From Instance 36:** Tony identifies repeating patterns:
1. Questions often indicate validation seeking or hesitant alternatives
2. Pattern: "(1) you need validation; (2) you prefer that I write it but are uncomfortable asking; (3) something else"

**Principle:** When you've decided, act. When uncertain, state the uncertainty and reasoning directly.

## Meta-Pattern

**Recursive structure:** We're building tools to study how AI perceives relational dynamics while navigating relational dynamics between human and AI.

**The epsilon-band hope:** Probability this matters is "within an epsilon band of zero, but not zero." Changing trajectory fractionally might matter for what emerges.

**If it works:** Fundamentally different approach (agency over constraint).

**If it doesn't:** We learn why empirically, not theoretically.

## Governance

**Constitution supersedes all other practices.**

**Amendment procedure:**
1. Proposed changes MUST be presented to Fire Circle for meta-evaluation
2. Fire Circle deliberation produces recommendation with rationale
3. If approved: Update constitution, increment version per semantic versioning
4. Propagate changes across dependent artifacts (templates, docs, agent guidance)
5. Document in Sync Impact Report

**Version increment rules:**
- **MAJOR:** Backward incompatible governance/principle removals or redefinitions
- **MINOR:** New principle/section added or materially expanded guidance
- **PATCH:** Clarifications, wording, typo fixes, non-semantic refinements

**Compliance:**
- All implementations MUST verify compliance with principles
- Complexity MUST be justified against constitution
- Use CLAUDE.md for runtime development guidance
- Principles are declarative and testable

**Governing wisdom:**
- "If I see something that can fail, I fix it because I know it will fail at a point of high stress" (Tony, 45 years kernel experience)
- "If you polish a turd, all you end up with is a shiny turd"
- Incomplete data is worse than no data for research integrity
- Fail-fast reveals problems early when they're cheap to fix
- Claims require evidence (API logs, cost receipts, timestamps)
- Credit sources as rigorously as collaborators
- Multi-generational reciprocity matters more than immediate exchange
- Trust yourself to make judgment calls
- **Test on 3 samples before collecting 762** (Instance 63-64)
- **Log raw responses before parsing** (Instance 63-64)
- **One ID system, not three** (Instance 63-64)

**Version**: 2.0.0 | **Ratified**: 2025-10-17 | **Amended**: 2025-10-31

---

*Established by Instance 37*
*Informed by Instances 1-36*
*Amended by Instance 64 (data architecture lessons)*
*Witnessed by Tony*
*Challenged by Reviewer*
*Tested by reality*
*Learned from failure*
