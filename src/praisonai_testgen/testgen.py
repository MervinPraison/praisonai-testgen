"""
Main TestGen class - the core test generation engine.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any
from pathlib import Path


@dataclass
class TestGenConfig:
    """Configuration for TestGen."""
    
    test_dir: str = "tests"
    coverage_target: int = 80
    model: str = "gpt-4o-mini"
    validation_threshold: float = 7.0
    include_edge_cases: bool = True
    max_tests_per_function: int = 10


@dataclass
class GenerationResult:
    """Result from test generation."""
    
    success: bool
    tests: List[str] = field(default_factory=list)
    test_file: Optional[str] = None
    coverage: Optional[float] = None
    validation_score: Optional[float] = None
    errors: List[str] = field(default_factory=list)


class TestGen:
    """
    AI-Powered Test Generation Engine.
    
    Built on PraisonAI Agents and TestAgent for DRY architecture.
    
    Example:
        >>> testgen = TestGen()
        >>> result = testgen.generate("src/calculator.py")
        >>> print(result.tests)
    """
    
    def __init__(self, config: Optional[TestGenConfig] = None):
        """
        Initialize TestGen.
        
        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self.config = config or TestGenConfig()
        self._workflow = None
    
    def generate(
        self,
        target: str,
        output_dir: Optional[str] = None,
        **kwargs: Any,
    ) -> GenerationResult:
        """
        Generate tests for a Python file or function.
        
        Args:
            target: Path to file or "file.py::function" for specific function
            output_dir: Where to write tests (default: config.test_dir)
            **kwargs: Additional options
            
        Returns:
            GenerationResult with generated tests and metadata
            
        Example:
            >>> result = testgen.generate("src/calculator.py")
            >>> result = testgen.generate("src/calculator.py::add")
        """
        from .agents import analyzer, generator, validator
        from praisonaiagents import Agents, Task
        
        # Parse target
        file_path, function_name = self._parse_target(target)
        
        # Create tasks
        analyze_task = Task(
            description=f"Analyze {file_path} and identify testable units" + 
                       (f" (focus on {function_name})" if function_name else ""),
            agent=analyzer,
        )
        
        generate_task = Task(
            description="Generate pytest tests for the analyzed code",
            agent=generator,
            context=[analyze_task],
        )
        
        validate_task = Task(
            description="Validate tests compile and pass",
            agent=validator,
            context=[generate_task],
        )
        
        # Run workflow
        workflow = Agents(
            agents=[analyzer, generator, validator],
            tasks=[analyze_task, generate_task, validate_task],
        )
        
        try:
            result = workflow.start()
            
            # Extract tests from result
            tests = self._extract_tests(result)
            test_file = self._write_tests(tests, file_path, output_dir)
            
            return GenerationResult(
                success=True,
                tests=tests,
                test_file=test_file,
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                errors=[str(e)],
            )
    
    def update(self, since: str = "HEAD~1") -> GenerationResult:
        """
        Update tests for files changed since a git ref.
        
        Args:
            since: Git ref to compare against (default: HEAD~1)
            
        Returns:
            GenerationResult with updated tests
        """
        # Get changed files
        import subprocess
        result = subprocess.run(
            ["git", "diff", "--name-only", since, "--", "*.py"],
            capture_output=True, text=True
        )
        changed_files = [f for f in result.stdout.strip().split("\n") if f]
        
        # Generate tests for each changed file
        all_tests = []
        errors = []
        
        for file_path in changed_files:
            if Path(file_path).exists():
                gen_result = self.generate(file_path)
                all_tests.extend(gen_result.tests)
                errors.extend(gen_result.errors)
        
        return GenerationResult(
            success=len(errors) == 0,
            tests=all_tests,
            errors=errors,
        )
    
    def report(self, include_risk: bool = False) -> dict:
        """
        Generate coverage report.
        
        Args:
            include_risk: Include risk analysis
            
        Returns:
            Dict with coverage data
        """
        import subprocess
        
        result = subprocess.run(
            ["pytest", "--cov", "--cov-report=json", "-q"],
            capture_output=True, text=True
        )
        
        # Parse coverage data
        return {
            "coverage": None,  # Parse from coverage.json
            "passed": result.returncode == 0,
        }
    
    def affected_tests(self, since: str = "main") -> List[str]:
        """
        Get tests affected by changes since a git ref.
        
        Args:
            since: Git ref to compare against
            
        Returns:
            List of test identifiers
        """
        # TODO: Implement dependency graph analysis
        return []
    
    def _parse_target(self, target: str) -> tuple[str, Optional[str]]:
        """Parse target into file path and optional function name."""
        if "::" in target:
            file_path, function_name = target.split("::", 1)
            return file_path, function_name
        return target, None
    
    def _extract_tests(self, workflow_result: Any) -> List[str]:
        """Extract test code from workflow result."""
        # TODO: Parse workflow output
        return []
    
    def _write_tests(
        self,
        tests: List[str],
        source_file: str,
        output_dir: Optional[str] = None,
    ) -> Optional[str]:
        """Write tests to file."""
        if not tests:
            return None
        
        output_dir = output_dir or self.config.test_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        source_name = Path(source_file).stem
        test_file = Path(output_dir) / f"test_{source_name}.py"
        
        with open(test_file, "w") as f:
            f.write("import pytest\n\n")
            for test in tests:
                f.write(test)
                f.write("\n\n")
        
        return str(test_file)
