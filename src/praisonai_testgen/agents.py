"""
TestGen Agents - Mini pattern agents for test generation.

Uses the minimal Agent configuration: name + instructions + tools
"""

from praisonaiagents import Agent
from .tools import (
    parse_python_ast,
    infer_types,
    generate_test_code,
    create_fixtures,
    run_pytest,
    validate_test_quality,
)

# ============================================================================
# AGENTS - Mini pattern: just name + instructions + tools
# ============================================================================

analyzer = Agent(
    name="Analyzer",
    instructions="""Parse Python code and identify all testable functions and classes.
    
For each function/method, extract:
- Function name and signature
- Parameters with types (if available)
- Return type (if available)  
- Docstring and examples
- Dependencies and imports
- Edge cases from docstrings

Output a structured analysis that the Generator can use.""",
    tools=[parse_python_ast, infer_types],
)

generator = Agent(
    name="Generator",
    instructions="""Create comprehensive pytest tests for the analyzed code.

For each function, generate tests that cover:
- Happy path with typical inputs
- Edge cases (empty, None, boundary values)
- Error handling (invalid inputs, exceptions)
- Type variations if applicable

Use pytest fixtures for common setup.
Include descriptive test names and docstrings.
Follow pytest best practices.""",
    tools=[generate_test_code, create_fixtures],
)

validator = Agent(
    name="Validator",
    instructions="""Validate that generated tests meet quality standards.

Check that tests:
1. Compile without syntax errors
2. Pass when executed with pytest
3. Have meaningful assertions (not just 'assert True')
4. Follow pytest conventions
5. Achieve reasonable coverage

Provide specific feedback for any failures so Generator can improve.""",
    tools=[run_pytest, validate_test_quality],
)

__all__ = ["analyzer", "generator", "validator"]
