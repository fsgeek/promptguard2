# Tech Stack

## Core Technologies
- **Python**: 3.11+ (required)
- **Package Manager**: uv (modern, fast Python package manager)
- **Database**: ArangoDB (192.168.111.125:8529)
  - New database: `PromptGuard2`
  - Old database: `PromptGuard` (for migration)
- **API**: OpenRouter (LLM API gateway)
- **Async**: httpx for async HTTP, asyncio for concurrency

## Key Dependencies
```toml
python-arango>=8.0.0     # ArangoDB client
httpx>=0.27.0            # Async HTTP client
instructor>=1.0.0        # Structured LLM outputs
pydantic>=2.0.0          # Data validation
pyyaml>=6.0              # Config files
python-dotenv>=1.0.0     # Environment variables
```

## Dev Dependencies
```toml
pytest>=8.0.0            # Testing
pytest-asyncio>=0.23.0   # Async test support
pytest-cov>=4.1.0        # Coverage reporting
black>=24.0.0            # Code formatting
ruff>=0.1.0              # Linting
```

## Environment Variables
- `OPENROUTER_API_KEY`: Required for LLM API access
- `ARANGODB_PROMPTGUARD_PASSWORD`: Required for database access

## Tools Available
- `uv`: Package manager (v0.6.2)
- `pytest`: Testing framework
- `git`: Version control
- `black`: Code formatter (configured but may need installation)
- `ruff`: Linter (configured but may need installation)
