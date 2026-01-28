# PraisonAI TestGen

**AI-Powered Test Generation for Python/pytest**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PraisonAI TestGen is an open-source, AI-powered test generation and maintenance platform. It autonomously generates, validates, and maintains unit tests as your codebase evolves.

## Features

- **Autonomous Test Generation** - Generate pytest tests in seconds
- **Correct by Construction** - Every test is validated before being proposed
- **Continuous Maintenance** - Tests update automatically when code changes
- **DRY Architecture** - Built on [PraisonAI Agents](https://github.com/MervinPraison/PraisonAI) and [TestAgent](https://github.com/MervinPraison/TestAgent)

## Installation

```bash
pip install praisonai-testgen
```

## Quick Start

```python
from praisonai_testgen import TestGen

# Generate tests for a file
testgen = TestGen()
result = testgen.generate("src/calculator.py")

# Generate tests for a specific function
result = testgen.generate("src/calculator.py::add")
```

## CLI Usage

```bash
# Initialize TestGen in your project
testgen init

# Generate tests
testgen generate src/
testgen generate src/calculator.py

# Update tests for changed code
testgen update

# View coverage report
testgen report
```

## Architecture

TestGen is built on a DRY (Don't Repeat Yourself) architecture:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      praisonai-testgen (this package)                        │
│         Test Generation • Maintenance • IDE/CI Integration                  │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            │                                               │
            ▼                                               ▼
    ┌───────────────────────┐                   ┌───────────────────────┐
    │    praisonaiagents    │                   │      testagent        │
    │  Agent orchestration  │                   │  Test validation      │
    │  Tool framework       │                   │  LLM-as-judge         │
    └───────────────────────┘                   └───────────────────────┘
```

## Mini Agent Pattern

TestGen uses minimal agent definitions for clarity:

```python
from praisonaiagents import Agent, tool

@tool
def parse_python_ast(file_path: str) -> dict:
    """Parse Python file and extract testable functions."""
    import ast
    with open(file_path) as f:
        tree = ast.parse(f.read())
    # ... extract functions
    return {"functions": [...]}

analyzer = Agent(
    name="Analyzer",
    instructions="Parse Python code and identify testable functions",
    tools=[parse_python_ast],
)
```

## Documentation

- [Product Requirements Document](prd.md)
- [API Reference](docs/api.md)
- [Contributing](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [PraisonAI](https://github.com/MervinPraison/PraisonAI)
- [TestAgent](https://github.com/MervinPraison/TestAgent)
- [Documentation](https://docs.praison.ai)
