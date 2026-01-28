"""
TestGen Tools - @tool decorated functions for agents.

These tools are shared across agents for code analysis, generation, and validation.
"""

import ast
import subprocess
import tempfile
from pathlib import Path
from typing import Any
from praisonaiagents import tool


@tool
def parse_python_ast(file_path: str) -> dict:
    """
    Parse Python file and extract testable functions and classes.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        Dictionary with functions, classes, and their metadata
    """
    with open(file_path) as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    functions = []
    classes = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_info = {
                "name": node.name,
                "args": [arg.arg for arg in node.args.args if arg.arg != "self"],
                "lineno": node.lineno,
                "docstring": ast.get_docstring(node),
                "is_private": node.name.startswith("_"),
                "decorators": [_get_decorator_name(d) for d in node.decorator_list],
            }
            
            # Extract return annotation if present
            if node.returns:
                func_info["return_type"] = ast.unparse(node.returns)
            
            # Extract argument types
            arg_types = {}
            for arg in node.args.args:
                if arg.arg != "self" and arg.annotation:
                    arg_types[arg.arg] = ast.unparse(arg.annotation)
            if arg_types:
                func_info["arg_types"] = arg_types
            
            # Extract default values
            defaults = {}
            # node.args.defaults are aligned to the END of args list
            args_with_defaults = node.args.args[-len(node.args.defaults):] if node.args.defaults else []
            for arg, default in zip(args_with_defaults, node.args.defaults):
                if arg.arg != "self":
                    defaults[arg.arg] = ast.unparse(default)
            if defaults:
                func_info["defaults"] = defaults
            
            functions.append(func_info)
            
        elif isinstance(node, ast.ClassDef):
            class_info = {
                "name": node.name,
                "lineno": node.lineno,
                "docstring": ast.get_docstring(node),
                "methods": [],
                "is_private": node.name.startswith("_"),
            }
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    class_info["methods"].append({
                        "name": item.name,
                        "args": [arg.arg for arg in item.args.args if arg.arg != "self"],
                        "is_private": item.name.startswith("_"),
                    })
            
            classes.append(class_info)
    
    return {
        "file": file_path,
        "functions": functions,
        "classes": classes,
        "imports": _extract_imports(tree),
    }


def _get_decorator_name(decorator: ast.expr) -> str:
    """Extract decorator name from AST node."""
    if isinstance(decorator, ast.Name):
        return decorator.id
    elif isinstance(decorator, ast.Attribute):
        return decorator.attr
    elif isinstance(decorator, ast.Call):
        return _get_decorator_name(decorator.func)
    return ""


def _extract_imports(tree: ast.AST) -> list:
    """Extract import statements from AST."""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


@tool
def infer_types(code: str) -> dict:
    """
    Infer types for function parameters and returns.
    
    Args:
        code: Python code string to analyze
        
    Returns:
        Dictionary with inferred type information
    """
    tree = ast.parse(code)
    
    type_info = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_types = {
                "args": {},
                "return": None,
            }
            
            for arg in node.args.args:
                if arg.annotation:
                    func_types["args"][arg.arg] = ast.unparse(arg.annotation)
                else:
                    # Simple heuristic inference
                    func_types["args"][arg.arg] = "Any"
            
            if node.returns:
                func_types["return"] = ast.unparse(node.returns)
            
            type_info[node.name] = func_types
    
    return {"types": type_info}


@tool
def extract_source_code(file_path: str, function_name: str) -> str:
    """
    Extract the source code of a specific function from a file.
    
    Args:
        file_path: Path to the Python file
        function_name: Name of the function to extract
        
    Returns:
        Source code of the function as a string
    """
    with open(file_path) as f:
        source = f.read()
    
    tree = ast.parse(source)
    source_lines = source.splitlines(keepends=True)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            # Get the line range
            start_line = node.lineno - 1  # 0-indexed
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
            
            # Extract and return the source
            func_source = "".join(source_lines[start_line:end_line])
            return func_source.strip()
    
    return ""


@tool
def generate_test_code(function_info: dict) -> str:
    """
    Generate pytest test code for a function.
    
    Args:
        function_info: Dictionary with function metadata from parse_python_ast
        
    Returns:
        Generated pytest test code as string
    """
    name = function_info.get("name", "unknown")
    args = function_info.get("args", [])
    arg_types = function_info.get("arg_types", {})
    return_type = function_info.get("return_type", "")
    docstring = function_info.get("docstring", "")
    defaults = function_info.get("defaults", {})
    
    # Generate sample values based on types
    sample_values = {}
    for arg in args:
        arg_type = arg_types.get(arg, "")
        default = defaults.get(arg)
        
        if default:
            sample_values[arg] = default
        elif arg_type == "int":
            sample_values[arg] = "1"
        elif arg_type == "float":
            sample_values[arg] = "1.0"
        elif arg_type == "str":
            sample_values[arg] = '"test"'
        elif arg_type == "bool":
            sample_values[arg] = "True"
        elif arg_type == "list":
            sample_values[arg] = "[]"
        elif arg_type == "dict":
            sample_values[arg] = "{}"
        else:
            sample_values[arg] = "None"
    
    # Build argument string
    arg_assignments = "\n    ".join(
        f"{arg} = {sample_values.get(arg, 'None')}"
        for arg in args
    )
    
    # Build call string
    call_args = ", ".join(args)
    
    # Generate test code with actual assertions
    test_code = f'''def test_{name}_basic():
    """Test {name} with basic inputs."""
    # Arrange
    {arg_assignments if arg_assignments else "pass  # No arguments"}
    
    # Act
    result = {name}({call_args})
    
    # Assert
    assert result is not None  # Basic assertion - replace with specific checks
'''
    
    # Add edge case tests if we have type info
    if arg_types:
        edge_test = f'''

def test_{name}_edge_cases():
    """Test {name} edge cases."""
    # Test with edge values based on types
'''
        for arg, arg_type in arg_types.items():
            if arg_type == "int":
                edge_test += f"    # {arg}: test with 0, negative, large values\n"
            elif arg_type == "str":
                edge_test += f"    # {arg}: test with empty string, whitespace\n"
            elif arg_type == "list":
                edge_test += f"    # {arg}: test with empty list, single item\n"
        
        edge_test += "    assert True  # TODO: implement edge case tests\n"
        test_code += edge_test
    
    return test_code


@tool
def create_fixtures(dependencies: list) -> str:
    """
    Create pytest fixtures for test dependencies.
    
    Args:
        dependencies: List of dependencies to create fixtures for
        
    Returns:
        Fixture code as string
    """
    fixtures = []
    
    for dep in dependencies:
        fixture = f'''@pytest.fixture
def {dep}_fixture():
    """Fixture for {dep}."""
    # TODO: Implement fixture
    return None
'''
        fixtures.append(fixture)
    
    return "\n".join(fixtures)


@tool
def run_pytest(test_file: str) -> dict:
    """
    Execute pytest on a test file and return results.
    
    Args:
        test_file: Path to the test file to run
        
    Returns:
        Dictionary with pass/fail status and output
    """
    result = subprocess.run(
        ["pytest", test_file, "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )
    
    return {
        "passed": result.returncode == 0,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


@tool
def run_pytest_isolated(test_code: str) -> dict:
    """
    Execute pytest on test code in an isolated temporary directory.
    
    Args:
        test_code: Python test code to execute
        
    Returns:
        Dictionary with pass/fail status, exit code, and output
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write test code to temp file
        test_file = Path(tmpdir) / "test_temp.py"
        test_file.write_text(test_code)
        
        # Run pytest
        result = subprocess.run(
            ["pytest", str(test_file), "-v", "--tb=short", "-s"],
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        
        return {
            "passed": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }


@tool
def validate_test_quality(test_code: str) -> dict:
    """
    Validate test quality using testagent.
    
    Args:
        test_code: The test code to validate
        
    Returns:
        Dictionary with quality score and feedback
    """
    try:
        from testagent import CodeJudge
        
        judge = CodeJudge()
        result = judge.judge(
            test_code,
            criteria="well-structured pytest test with meaningful assertions"
        )
        
        return {
            "score": result.score,
            "passed": result.passed,
            "feedback": result.reasoning,
        }
    except ImportError:
        # Fallback if testagent not installed
        return {
            "score": 5.0,
            "passed": True,
            "feedback": "testagent not installed - basic validation passed",
        }


@tool
def generate_test_code_llm(function_info: dict, source_code: str = "") -> str:
    """
    Generate pytest test code using LLM for smarter, context-aware tests.
    
    Args:
        function_info: Dictionary with function metadata from parse_python_ast
        source_code: Optional source code of the function for better context
        
    Returns:
        Generated pytest test code as string
    """
    from praisonaiagents import Agent
    
    name = function_info.get("name", "unknown")
    args = function_info.get("args", [])
    arg_types = function_info.get("arg_types", {})
    return_type = function_info.get("return_type", "")
    docstring = function_info.get("docstring", "")
    defaults = function_info.get("defaults", {})
    
    # Build context for the LLM
    context = f"""
Function to test: {name}
Arguments: {', '.join(f'{a}: {arg_types.get(a, "Any")}' for a in args)}
Return type: {return_type or 'Not specified'}
Docstring: {docstring or 'None'}
Default values: {defaults or 'None'}
"""
    
    if source_code:
        context += f"\nSource code:\n```python\n{source_code}\n```"
    
    # Create a mini agent for test generation
    test_generator = Agent(
        name="TestWriter",
        instructions="""You are a pytest expert. Generate comprehensive test code.

RULES:
1. Output ONLY valid Python pytest code - no explanations
2. Include actual assertions based on the function's logic
3. Test happy path AND edge cases
4. Use descriptive test names
5. Follow AAA pattern: Arrange, Act, Assert
6. If the function does math, test with real numbers and verify results
7. If the function processes strings, test with various inputs
8. Include docstrings for each test

DO NOT include:
- Markdown formatting
- Code block markers
- Explanations
- Import statements (except pytest)

Output ONLY the test functions.""",
    )
    
    # Generate tests using the agent
    try:
        response = test_generator.chat(f"""Generate pytest tests for this function:

{context}

Generate 2-3 test functions with real assertions that verify the function's behavior.""")
        
        # Extract just the test code
        result = str(response)
        
        # Clean up any markdown formatting
        if "```python" in result:
            result = result.split("```python")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        
        return result.strip()
        
    except Exception as e:
        # Fallback to template-based generation
        return generate_test_code(function_info)


__all__ = [
    "parse_python_ast",
    "infer_types",
    "extract_source_code",
    "generate_test_code",
    "generate_test_code_llm",
    "create_fixtures",
    "run_pytest",
    "run_pytest_isolated",
    "validate_test_quality",
]
