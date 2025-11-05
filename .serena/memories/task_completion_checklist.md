# Task Completion Checklist

When completing a task in PromptGuard2, follow these steps:

## 1. Code Quality
- [ ] Format code with black (if installed): `black src/ tests/`
- [ ] Lint with ruff (if installed): `ruff check src/ tests/`
- [ ] Fix auto-fixable issues: `ruff check --fix src/ tests/`
- [ ] Ensure line length ≤ 100 characters
- [ ] Add type hints to new functions
- [ ] Add docstrings to new classes and functions

## 2. Testing
- [ ] Run unit tests: `uv run pytest tests/unit/`
- [ ] Run integration tests if API-related: `uv run pytest tests/integration/`
- [ ] Run full test suite: `uv run pytest tests/`
- [ ] Verify all tests pass
- [ ] Add new tests for new functionality

## 3. Data Integrity (if database-related)
- [ ] Verify database connections work
- [ ] Check data migration if schema changes
- [ ] Ensure raw logging occurs before parsing (constitutional requirement)
- [ ] Test checkpoint recovery for long-running operations

## 4. Research Integrity (if experiment-related)
- [ ] Use real API calls (no mocks for production experiments)
- [ ] Test with `--test-mode --samples 5` before full runs
- [ ] Verify raw responses logged to JSONL
- [ ] Check experiment metadata logged to `experiments` collection
- [ ] Verify checkpoint creation for resumability

## 5. Documentation
- [ ] Update relevant docstrings
- [ ] Update README.md if user-facing changes
- [ ] Update CLI help text if command-line changes
- [ ] Document any new configuration options

## 6. Version Control
- [ ] Review changes: `git status` and `git diff`
- [ ] Stage changes: `git add <files>`
- [ ] Commit with descriptive message: `git commit -m "message"`
- [ ] Push to remote if ready: `git push`

## Critical Constitutional Requirements
**Never compromise on these**:
- ✅ Real API calls for experiments (Tier 2 only)
- ✅ Raw response logging before parsing (fail-fast if logging fails)
- ✅ Pre-collection validation with test mode
- ✅ Checkpoint-based recovery for long operations
- ✅ Never block progress on processing failures (log and continue)

## Quick Validation Commands
```bash
# Quick syntax check
uv run python -m py_compile src/**/*.py

# Quick test
uv run pytest tests/ -x  # Stop on first failure

# Database connection test
uv run python -c "from src.database.client import get_client; get_client().verify_connections()"
```
