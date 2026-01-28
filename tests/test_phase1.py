"""
TDD Tests for TestGen Tools - Phase 1

Following TDD: Write failing tests first, then implement.
"""

import pytest
import tempfile
from pathlib import Path
from textwrap import dedent


# =============================================================================
# 1.1 Enhanced parse_python_ast Tests
# =============================================================================

class TestParseASTEnhanced:
    """Tests for enhanced parse_python_ast functionality."""
    
    def test_extracts_docstrings(self):
        """Test that docstrings are extracted from functions."""
        from praisonai_testgen.tools import parse_python_ast
        
        code = dedent('''
            def add(a: int, b: int) -> int:
                """Add two numbers together.
                
                Args:
                    a: First number
                    b: Second number
                    
                Returns:
                    Sum of a and b
                """
                return a + b
        ''')
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = parse_python_ast(temp_path)
            
            assert len(result["functions"]) == 1
            func = result["functions"][0]
            assert func["docstring"] is not None
            assert "Add two numbers" in func["docstring"]
            assert "Args:" in func["docstring"]
        finally:
            Path(temp_path).unlink()
    
    def test_extracts_decorators(self):
        """Test that decorators are extracted from functions."""
        from praisonai_testgen.tools import parse_python_ast
        
        code = dedent('''
            @staticmethod
            @lru_cache(maxsize=128)
            def cached_add(a: int, b: int) -> int:
                """Add with caching."""
                return a + b
        ''')
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = parse_python_ast(temp_path)
            
            func = result["functions"][0]
            assert "decorators" in func
            assert "staticmethod" in func["decorators"]
            assert "lru_cache" in func["decorators"]
        finally:
            Path(temp_path).unlink()
    
    def test_extracts_default_values(self):
        """Test that default argument values are extracted."""
        from praisonai_testgen.tools import parse_python_ast
        
        code = dedent('''
            def greet(name: str = "World", times: int = 1) -> str:
                """Greet someone."""
                return f"Hello, {name}!" * times
        ''')
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = parse_python_ast(temp_path)
            
            func = result["functions"][0]
            assert "defaults" in func
            assert func["defaults"].get("name") == "'World'"
            assert func["defaults"].get("times") == "1"
        finally:
            Path(temp_path).unlink()
    
    def test_extracts_return_type(self):
        """Test that return type annotations are extracted."""
        from praisonai_testgen.tools import parse_python_ast
        
        code = dedent('''
            def calculate(x: float) -> float:
                """Calculate something."""
                return x * 2
        ''')
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = parse_python_ast(temp_path)
            
            func = result["functions"][0]
            assert func.get("return_type") == "float"
        finally:
            Path(temp_path).unlink()
    
    def test_extracts_arg_types(self):
        """Test that argument type annotations are extracted."""
        from praisonai_testgen.tools import parse_python_ast
        
        code = dedent('''
            def process(data: list, count: int, flag: bool = True) -> dict:
                """Process data."""
                return {}
        ''')
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = parse_python_ast(temp_path)
            
            func = result["functions"][0]
            assert "arg_types" in func
            assert func["arg_types"].get("data") == "list"
            assert func["arg_types"].get("count") == "int"
            assert func["arg_types"].get("flag") == "bool"
        finally:
            Path(temp_path).unlink()


# =============================================================================
# 1.2 Enhanced generate_test_code Tests  
# =============================================================================

class TestGenerateTestCode:
    """Tests for generate_test_code functionality."""
    
    def test_generates_valid_pytest_syntax(self):
        """Test that generated code is valid pytest syntax."""
        from praisonai_testgen.tools import generate_test_code
        
        func_info = {
            "name": "add",
            "args": ["a", "b"],
            "arg_types": {"a": "int", "b": "int"},
            "return_type": "int",
            "docstring": "Add two numbers.",
        }
        
        result = generate_test_code(func_info)
        
        # Should be valid Python
        import ast
        ast.parse(result)
        
        # Should have test function
        assert "def test_" in result
        assert "add" in result
    
    def test_generates_assertions(self):
        """Test that generated tests have actual assertions."""
        from praisonai_testgen.tools import generate_test_code
        
        func_info = {
            "name": "multiply",
            "args": ["x", "y"],
            "arg_types": {"x": "int", "y": "int"},
            "return_type": "int",
            "docstring": "Multiply two numbers.",
        }
        
        result = generate_test_code(func_info)
        
        # Should have real assertions, not just pass
        assert "assert" in result
        assert "pass" not in result or "assert" in result


# =============================================================================
# 1.3 run_pytest_isolated Tests
# =============================================================================

class TestRunPytestIsolated:
    """Tests for isolated pytest execution."""
    
    def test_runs_passing_test(self):
        """Test running a passing test."""
        from praisonai_testgen.tools import run_pytest_isolated
        
        test_code = dedent('''
            def test_simple():
                assert 1 + 1 == 2
        ''')
        
        result = run_pytest_isolated(test_code)
        
        assert result["passed"] is True
        assert result["exit_code"] == 0
    
    def test_runs_failing_test(self):
        """Test running a failing test."""
        from praisonai_testgen.tools import run_pytest_isolated
        
        test_code = dedent('''
            def test_failing():
                assert 1 == 2
        ''')
        
        result = run_pytest_isolated(test_code)
        
        assert result["passed"] is False
        assert result["exit_code"] != 0
    
    def test_captures_output(self):
        """Test that stdout/stderr are captured."""
        from praisonai_testgen.tools import run_pytest_isolated
        
        test_code = dedent('''
            def test_with_output():
                print("Hello from test")
                assert True
        ''')
        
        result = run_pytest_isolated(test_code)
        
        assert "stdout" in result
        assert "Hello from test" in result["stdout"]


# =============================================================================
# 1.4 extract_source_code Tests
# =============================================================================

class TestExtractSourceCode:
    """Tests for source code extraction."""
    
    def test_extracts_function_source(self):
        """Test extracting source code of a function."""
        from praisonai_testgen.tools import extract_source_code
        
        code = dedent('''
            def add(a, b):
                """Add two numbers."""
                return a + b
            
            def subtract(a, b):
                """Subtract two numbers."""
                return a - b
        ''')
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = extract_source_code(temp_path, "add")
            
            assert "def add(a, b):" in result
            assert "return a + b" in result
            assert "subtract" not in result
        finally:
            Path(temp_path).unlink()


# =============================================================================
# 2.x Agent Tests
# =============================================================================

class TestAnalyzerAgent:
    """Tests for analyzer agent."""
    
    def test_analyzer_returns_function_metadata(self):
        """Test that analyzer agent extracts function metadata."""
        from praisonai_testgen.agents import analyzer
        from praisonaiagents import Task
        
        code = dedent('''
            def calculate_total(items: list, tax_rate: float = 0.1) -> float:
                """Calculate total with tax."""
                subtotal = sum(items)
                return subtotal * (1 + tax_rate)
        ''')
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            # Create a simple task
            task = Task(
                description=f"Analyze {temp_path} and identify testable functions",
                agent=analyzer,
            )
            
            # The agent should be able to use its tools
            assert analyzer.name == "Analyzer"
            assert len(analyzer.tools) >= 1
        finally:
            Path(temp_path).unlink()


class TestGeneratorAgent:
    """Tests for generator agent."""
    
    def test_generator_has_correct_tools(self):
        """Test that generator agent has the right tools."""
        from praisonai_testgen.agents import generator
        
        assert generator.name == "Generator"
        assert len(generator.tools) >= 1
        
        tool_names = [t.__name__ for t in generator.tools]
        assert "generate_test_code" in tool_names


class TestValidatorAgent:
    """Tests for validator agent."""
    
    def test_validator_has_correct_tools(self):
        """Test that validator agent has the right tools."""
        from praisonai_testgen.agents import validator
        
        assert validator.name == "Validator"
        assert len(validator.tools) >= 1


# =============================================================================
# 3.x Orchestration Tests
# =============================================================================

class TestTestGenWorkflow:
    """Tests for TestGen workflow."""
    
    def test_generate_creates_test_file(self):
        """Test that generate() creates a test file."""
        from praisonai_testgen import TestGen
        
        # Create a simple source file
        code = dedent('''
            def add(a: int, b: int) -> int:
                """Add two integers."""
                return a + b
        ''')
        
        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = Path(tmpdir) / "calculator.py"
            source_file.write_text(code)
            
            test_dir = Path(tmpdir) / "tests"
            
            testgen = TestGen()
            result = testgen.generate(
                str(source_file),
                output_dir=str(test_dir),
            )
            
            # Should succeed
            assert result.success is True
            
            # Should create test file
            assert result.test_file is not None
            assert Path(result.test_file).exists()
            
            # Test file should contain tests
            test_content = Path(result.test_file).read_text()
            assert "def test_" in test_content
            assert "add" in test_content
