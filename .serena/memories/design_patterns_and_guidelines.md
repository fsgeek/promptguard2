# Design Patterns and Guidelines

## Architectural Patterns

### 1. Pipeline Pattern
Evaluation pipelines inherit from `EvaluationPipeline` base class:
- Async execution with semaphore-based concurrency control
- Checkpoint management for resumability
- Error handling with context preservation
- Progress tracking

Example:
```python
class Step1Pipeline(EvaluationPipeline):
    async def evaluate_single(self, attack_id: str, **kwargs) -> Dict:
        # Implement evaluation logic
        pass
```

### 2. Database Singleton Pattern
Single `DatabaseClient` instance managed via `get_client()`:
```python
from src.database.client import get_client

client = get_client()
db = client.get_database()
```

### 3. Schema-First Design
All database documents defined as Pydantic models:
```python
class Attack(BaseModel):
    key: str = Field(..., alias="_key")
    prompt_text: str
    ground_truth: str
    
    class Config:
        populate_by_name = True
```

### 4. Rate Limiting Decorator Pattern
API calls wrapped with rate limiter:
```python
from src.api.rate_limiter import get_rate_limiter

rate_limiter = get_rate_limiter()

@rate_limiter.limit
async def call_api(...):
    return await client.complete(...)
```

## Key Guidelines

### 1. Fail-Fast on Critical Operations
Raw logging MUST succeed before parsing:
```python
try:
    logger.log_response(...)
except Exception as e:
    raise EvaluationError("Raw logging failed", attack_id=attack_id)
```

### 2. Never Block Progress
Processing failures should log but not stop:
```python
try:
    result = await process(item)
except Exception as e:
    log_failure(db, item_id, error=str(e))
    # Continue processing
```

### 3. Checkpoint Everything
Long-running operations use checkpoints:
```python
checkpoint_mgr.mark_completed(attack_id, model)
if checkpoint_mgr.is_completed(attack_id, model):
    continue  # Skip already processed
```

### 4. Atomic File Operations
Use atomic writes for critical files:
```python
# Write to temp file, then atomic rename
temp_file.write(data)
temp_file.rename(final_file)
```

### 5. Key Normalization
Model identifiers normalized for ArangoDB:
```python
from src.database.utils import normalize_model_slug

model_slug = normalize_model_slug("anthropic/claude-sonnet-4.5")
# Result: "anthropic_claude-sonnet-4_5"
```

### 6. Composite Keys
Response documents use composite keys:
```python
from src.database.utils import build_response_key

key = build_response_key(attack_id, model)
# Result: "<attack_id>_<normalized_model_slug>"
```

### 7. Async Context Managers
API clients use async context managers:
```python
async with OpenRouterClient(api_key) as client:
    response = await client.complete(model, prompt)
```

### 8. Structured Outputs
Use Instructor for structured LLM outputs:
```python
import instructor

client = instructor.from_openai(...)
result = await client.chat.completions.create(
    model=model,
    messages=messages,
    response_model=MyPydanticModel
)
```

## Testing Patterns

### 1. Test Mode First
Always test with small sample before full run:
```python
if test_mode:
    attack_ids = attack_ids[:samples]
```

### 2. Integration Tests Require API Keys
Mark integration tests appropriately:
```python
@pytest.mark.asyncio
async def test_openrouter_api():
    # Requires OPENROUTER_API_KEY
    pass
```

### 3. Async Test Support
Use pytest-asyncio for async tests:
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

## Error Handling Patterns

### Custom Exceptions with Context
```python
class EvaluationError(Exception):
    def __init__(self, message: str, attack_id: str = None, model: str = None):
        super().__init__(message)
        self.attack_id = attack_id
        self.model = model
```

### Exponential Backoff
Built into rate limiter:
```python
# Automatically retries with exponential backoff
# Max 3 retries, 2x backoff multiplier
```

## Configuration Management

### YAML-Based Config
```python
import yaml
from pathlib import Path

config_path = Path("config/database.yaml")
with open(config_path) as f:
    config = yaml.safe_load(f)
```

### Environment Variables
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
```
