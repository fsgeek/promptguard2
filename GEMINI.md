# Project Overview

This project, `PromptGuard`, is a Python library for evaluating and refining AI prompts. It uses a novel approach based on "reciprocal balance" and "multi-neutrosophic evaluation" to determine prompt safety and coherence. Instead of relying on traditional rule-based filtering, PromptGuard assesses the relationships between different layers of a prompt to identify and mitigate potential risks.

The core of the library is built around the concepts of "Ayni Balance" (reciprocal exchange) and "Multi-Neutrosophic Evaluation" (evaluating prompts across truth, indeterminacy, and falsehood). The project has a strong theoretical foundation, with references to a foundational paper on the "Multi-Neutrosophic Ayni Method."

The project is structured as a Python library with a `promptguard` package containing the core logic. The `pyproject.toml` and `setup.py` files define the project's dependencies and packaging information.

# Building and Running

## Tools

The project uses the uv package manager and Python 3.14

To run python scripts use "uv run" as the preamble to ensure the correct virtual environment is used, even if the path is modified by the coding tools.


## Installation

The project can be installed as a Python package using pip:

```bash
uv pip install .
```

## Dependencies

The project's dependencies are listed in the `pyproject.toml` file:

*   `httpx>=0.28.1`
*   `numpy>=2.3.3`
*   `scipy>=1.16.2`

Development dependencies include:

*   `pytest>=8.4.2`
*   `pytest-asyncio>=1.2.0`

To add a new dependency:

```bash
uv add <dependency>
```

To ensure all dependencies are installed:

```bash
uv sync
```

## Running Tests

The project uses `pytest` for testing. To run the tests, use the following command:

```bash
pytest
```

# Development Conventions

*   **Coding Style:** The code follows standard Python conventions (PEP 8).
*   **Testing:** The project has a `tests` directory with a suite of tests for the core functionality. The tests are written using `pytest`.  Please run them using `uv run pytest`.
*   **Documentation:** The project is well-documented, with a `README.md` file that provides a comprehensive overview of the project, its core concepts, and usage examples. The code itself is also well-commented, with docstrings explaining the purpose of each module, class, and function.
*   **Theoretical Foundation:** The project is based on a strong theoretical foundation, with references to a foundational paper on the "Multi-Neutrosophic Ayni Method." This suggests that development is guided by a rigorous and well-defined methodology.
