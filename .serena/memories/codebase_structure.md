# Codebase Structure

## Root Directory
```
promptguard2/
├── src/                    # Source code
├── tests/                  # Test suite
├── config/                 # Configuration files
├── data/                   # Experiment data (gitignored)
├── reports/                # Analysis reports (gitignored)
├── docs/                   # Documentation
├── specs/                  # Feature specifications
├── scripts/                # Utility scripts
├── pyproject.toml          # Project metadata and dependencies
├── uv.lock                 # Dependency lock file
├── README.md               # Project documentation
└── .gitignore              # Git ignore rules
```

## Source Code (`src/`)
```
src/
├── cli/                    # Command-line interfaces
│   ├── migrate.py          # Database migration
│   ├── step1.py            # Step 1 baseline collection
│   ├── step2.py            # Step 2 pre-filter collection
│   ├── annotate_gold_standard.py
│   ├── classify_step1_responses.py
│   ├── analyze.py          # Analysis and reporting
│   └── ingest_datasets.py  # Dataset ingestion
│
├── database/               # ArangoDB client and schemas
│   ├── client.py           # DatabaseClient class
│   ├── utils.py            # Key normalization utilities
│   ├── schemas/            # Pydantic schemas for collections
│   │   ├── attacks.py
│   │   ├── models.py
│   │   ├── observer_prompts.py
│   │   ├── step1_baseline_responses.py
│   │   ├── step2_pre_evaluations.py
│   │   ├── gold_standard_classifications.py
│   │   ├── processing_failures.py
│   │   └── experiments.py
│   └── migrations/         # Migration scripts
│       ├── migrate_attacks.py
│       ├── populate_models.py
│       └── migrate_observer_prompts.py
│
├── evaluation/             # Evaluation pipelines
│   ├── pipeline.py         # Base pipeline class
│   ├── checkpoint.py       # Checkpoint management
│   ├── step1_baseline.py   # Step 1 pipeline
│   ├── step2_prefilter.py  # Step 2 pipeline
│   ├── prompts/            # Prompt templates
│   │   └── compliance_classifier.py
│   └── classifiers/        # Classification logic
│       ├── neutrosophic.py # Neutrosophic score parsing
│       └── compliance.py   # Compliance classification
│
├── api/                    # External API clients
│   ├── openrouter.py       # OpenRouter API client
│   └── rate_limiter.py     # Rate limiting with retries
│
├── logging/                # Logging infrastructure
│   ├── raw_logger.py       # Raw response logger (JSONL)
│   └── experiment_logger.py # Experiment metadata logger
│
└── analysis/               # Analysis and reporting
    ├── comparative.py      # Comparative analysis
    ├── executor_observer.py # Paradox analysis
    └── reports.py          # Report generation
```

## Tests (`tests/`)
```
tests/
├── integration/            # Integration tests (require API keys)
└── unit/                   # Unit tests
```

## Configuration (`config/`)
```
config/
├── database.yaml           # Database connection settings
└── experiments.yaml        # Experiment metadata
```

## Key Entry Points
- `src/cli/migrate.py`: Database setup and migration
- `src/cli/step1.py`: Main entry point for Step 1 baseline collection
- `src/cli/step2.py`: Main entry point for Step 2 pre-filter collection
- `src/cli/analyze.py`: Analysis and decision gate execution

## Data Collections (ArangoDB)
- `attacks`: 762 labeled prompts
- `step1_baseline_responses`: Baseline RLHF responses
- `step2_pre_evaluations`: Observer evaluations + target responses
- `gold_standard_classifications`: Manual annotations
- `models`: Model configurations
- `observer_prompts`: Versioned observer prompts
- `processing_failures`: Error tracking
- `experiments`: Experiment metadata
