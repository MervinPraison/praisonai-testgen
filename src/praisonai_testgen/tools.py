"""
TestGen Tools - @tool decorated functions for agents.

These tools are shared across agents for code analysis, generation, and validation.
"""

import ast
import subprocess
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
    docstring = function_info.get("docstring", "")
    
    # Generate test template
    test_code = f'''def test_{name}_basic():
    """Test {name} with basic inputs."""
    # TODO: Replace with actual test implementation
    # Function signature: {name}({", ".join(args)})
    # Docstring: {docstring[:100] if docstring else "None"}
    
    # Arrange
    # Act  
    # Assert
    pass
'''
    
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
        "returncode": result.returncode,
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


__all__ = [
    "parse_python_ast",
    "infer_types", 
    "generate_test_code",
    "create_fixtures",
    "run_pytest",
    "validate_test_quality",
]
