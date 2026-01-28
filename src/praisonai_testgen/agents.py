"""
TestGen Agents - Mini pattern agents for test generation.

Uses the minimal Agent configuration: name + instructions + tools
"""

from praisonaiagents import Agent
from .tools import (
    parse_python_ast,
    infer_types,
    extract_source_code,
    generate_test_code,
    create_fixtures,
    run_pytest,
    run_pytest_isolated,
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
- Default argument values
- Decorators

Use the parse_python_ast tool to analyze files. Use extract_source_code to get 
the full source of specific functions when needed.

Output a structured analysis that the Generator can use to create tests.""",
    tools=[parse_python_ast, infer_types, extract_source_code],
)

generator = Agent(
    name="Generator",
    instructions="""Create comprehensive pytest tests for the analyzed code.

For each function, generate tests that cover:
- Happy path with typical inputs
- Edge cases (empty, None, boundary values)
- Error handling (invalid inputs, exceptions)
- Type variations if applicable

Use the generate_test_code tool to create test templates, then enhance them
with meaningful assertions. Use create_fixtures for test dependencies.

Generated tests MUST:
1. Be valid Python/pytest syntax
2. Have actual assertions (not just 'pass' or 'assert True')
3. Follow AAA pattern: Arrange, Act, Assert
4. Include descriptive test names and docstrings""",
    tools=[generate_test_code, create_fixtures],
)

validator = Agent(
    name="Validator",
    instructions="""Validate that generated tests meet quality standards.

Check that tests:
1. Compile without syntax errors
2. Pass when executed with pytest (use run_pytest_isolated)
3. Have meaningful assertions (not just 'assert True')
4. Follow pytest conventions
5. Provide good coverage

Use run_pytest_isolated to test code in isolation. Use validate_test_quality
to check code quality with AI judgment.

Provide specific feedback for any failures so Generator can improve.""",
    tools=[run_pytest, run_pytest_isolated, validate_test_quality],
)

__all__ = ["analyzer", "generator", "validator"]
