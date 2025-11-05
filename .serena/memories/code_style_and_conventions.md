# Code Style and Conventions

## Formatting
- **Line Length**: 100 characters (black and ruff configured)
- **Target Version**: Python 3.11
- **Formatter**: black (line-length=100, target-version='py311')

## Linting
**Ruff Configuration**:
- Line length: 100
- Target version: py311
- Selected rules:
  - E: pycodestyle errors
  - W: pycodestyle warnings
  - F: pyflakes
  - I: isort (import sorting)
  - B: flake8-bugbear
  - C4: flake8-comprehensions
  - UP: pyupgrade

**Ignored Rules**:
- E501: line too long (handled by black)
- B008: function calls in argument defaults
- C901: too complex

**Per-file Ignores**:
- `__init__.py`: F401 (unused imports)

## Code Patterns

### Docstrings
Use triple-quoted docstrings for classes and functions:
```python
def function_name(param: str) -> ReturnType:
    """
    Brief description.
    
    Detailed explanation if needed.
    """
```

### Type Hints
Use type hints extensively:
```python
from typing import List, Dict, Optional, Any

def process(items: List[Dict[str, Any]]) -> Optional[str]:
    ...
```

### Pydantic Models
Use Pydantic for data validation:
```python
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    field: str = Field(..., description="Field description")
    
    class Config:
        populate_by_name = True
```

### Async/Await
Extensive use of async patterns:
```python
async def async_function() -> Result:
    async with client:
        return await client.call()
```

### Error Handling
Custom exception classes with context:
```python
class EvaluationError(Exception):
    def __init__(self, message: str, attack_id: Optional[str] = None):
        super().__init__(message)
        self.attack_id = attack_id
```

## Testing Conventions
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`
- Markers: `@pytest.mark.asyncio` for async tests
- Coverage: Source code in `src/`, omit `tests/` and `__init__.py`

## Import Style
Imports should be sorted (via isort/ruff):
1. Standard library
2. Third-party packages
3. Local application imports
