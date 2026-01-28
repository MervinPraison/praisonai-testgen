"""Tests for TestGen tools."""

import pytest
import tempfile
from pathlib import Path


class TestParseAST:
    """Tests for parse_python_ast tool."""
    
    def test_parse_simple_function(self):
        """Test parsing a simple function."""
        from praisonai_testgen.tools import parse_python_ast
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
''')
            temp_path = f.name
        
        try:
            result = parse_python_ast(temp_path)
            
            assert "functions" in result
            assert len(result["functions"]) == 1
            
            func = result["functions"][0]
            assert func["name"] == "add"
            assert "a" in func["args"]
            assert "b" in func["args"]
        finally:
            Path(temp_path).unlink()
    
    def test_parse_class(self):
        """Test parsing a class with methods."""
        from praisonai_testgen.tools import parse_python_ast
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('''
class Calculator:
    """A simple calculator."""
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
''')
            temp_path = f.name
        
        try:
            result = parse_python_ast(temp_path)
            
            assert "classes" in result
            assert len(result["classes"]) == 1
            
            cls = result["classes"][0]
            assert cls["name"] == "Calculator"
            assert len(cls["methods"]) == 2
        finally:
            Path(temp_path).unlink()


class TestInferTypes:
    """Tests for infer_types tool."""
    
    def test_infer_annotated_types(self):
        """Test inferring types from annotations."""
        from praisonai_testgen.tools import infer_types
        
        code = '''
def add(a: int, b: int) -> int:
    return a + b
'''
        result = infer_types(code)
        
        assert "types" in result
        assert "add" in result["types"]
        assert result["types"]["add"]["return"] == "int"


class TestGenerateTestCode:
    """Tests for generate_test_code tool."""
    
    def test_generate_basic_test(self):
        """Test generating a basic test."""
        from praisonai_testgen.tools import generate_test_code
        
        func_info = {
            "name": "add",
            "args": ["a", "b"],
            "docstring": "Add two numbers",
        }
        
        result = generate_test_code(func_info)
        
        assert "def test_add_basic" in result
        assert "a, b" in result
