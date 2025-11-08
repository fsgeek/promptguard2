<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# Repository Guidelines

## Project Structure & Module Organization
- `promptguard/core` implements the neutrosophic primitives, reciprocity evaluators, and trust calculus used throughout the system. Extend these modules when adjusting core metrics.
- `promptguard/evaluation` and `promptguard/analysis` host validation pipelines and deeper studies; log supporting artefacts in `docs/` when experiments change.
- Domain datasets live in `datasets/` and `examples/`, while automation scripts such as `run_full_validation.py`, `run_quick_validation.py`, and `smoke_test.py` sit at repo root.
- Unit and integration tests live in `tests/` plus scenario-specific `test_*.py` files at the top level. Match new tests to the module path you touch.

## Build, Test, and Development Commands
- `uv sync` (or `pip install -e .[dev]`) installs the project with pytest extras.
- `uv run pytest` runs the full matrix; `uv run pytest -m "not integration"` skips networked suites.
- `python smoke_test.py` runs the 5-minute dataset subset for quick regression checks.
- `python run_full_validation.py` triggers the long evaluation (2h+); attach resulting `*_results.json` when sharing findings.

## Coding Style & Naming Conventions
- Use 4-space indentation, type hints, and targeted docstrings; core modules rely on dataclasses and enums, so mirror that approach.
- Follow `snake_case` for functions, `PascalCase` for classes/enums, and all-caps for configuration constants.
- Keep numpy work vectorised and prefer pure helpers inside `promptguard/core`; add brief comments around non-obvious math.

## Testing Guidelines
- Prefer `pytest` modules named `test_<feature>.py`, mirroring the package layout. Co-locate async scenarios with the `pytest-asyncio` marker.
- Tag network-dependent suites `@pytest.mark.integration`; default CI uses `-m "not integration"` to skip them.
- Add smoke coverage for new datasets under `tests/` and refresh `smoke_test.py` samples when labels change.
- When expanding validation scripts, assert both reciprocity score and exchange type using fixtures checked into `tests/`.

## Commit & Pull Request Guidelines
- Follow the existing history: sentence-case, action-oriented summaries that reference the touched domain (e.g., “Refine observer framing anomalies”). Group dataset refreshes and doc drops into separate commits.
- Include PR descriptions covering motivation, approach, and validation commands executed; link to relevant logs (`*.log`, `*_results.json`) and note any integration tests skipped.
- For evaluation tweaks, attach smoke-test output and highlight metric regressions or improvements in the PR body.

## Security & Configuration Tips
- Never commit API keys or model credentials; prefer `.env` files ignored by git and list required variables in `docs/`.
- Large validation runs generate sensitive prompt/response data—keep raw outputs under `artifact_evaluation_*.json` and circulate redacted summaries when collaborating externally.
