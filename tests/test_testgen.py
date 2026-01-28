"""Tests for PraisonAI TestGen."""

import pytest
from praisonai_testgen import TestGen, TestGenConfig


class TestTestGenConfig:
    """Tests for TestGenConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = TestGenConfig()
        
        assert config.test_dir == "tests"
        assert config.coverage_target == 80
        assert config.model == "gpt-4o-mini"
        assert config.validation_threshold == 7.0
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = TestGenConfig(
            test_dir="custom_tests",
            coverage_target=90,
            model="gpt-4o",
        )
        
        assert config.test_dir == "custom_tests"
        assert config.coverage_target == 90
        assert config.model == "gpt-4o"


class TestTestGen:
    """Tests for TestGen class."""
    
    def test_init_default(self):
        """Test default initialization."""
        testgen = TestGen()
        
        assert testgen.config is not None
        assert testgen.config.test_dir == "tests"
    
    def test_init_with_config(self):
        """Test initialization with custom config."""
        config = TestGenConfig(coverage_target=95)
        testgen = TestGen(config=config)
        
        assert testgen.config.coverage_target == 95
    
    def test_parse_target_file_only(self):
        """Test parsing file-only target."""
        testgen = TestGen()
        file_path, function_name = testgen._parse_target("src/calc.py")
        
        assert file_path == "src/calc.py"
        assert function_name is None
    
    def test_parse_target_with_function(self):
        """Test parsing target with function specifier."""
        testgen = TestGen()
        file_path, function_name = testgen._parse_target("src/calc.py::add")
        
        assert file_path == "src/calc.py"
        assert function_name == "add"
