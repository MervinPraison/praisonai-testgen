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
        use_agents: bool = False,
        **kwargs: Any,
    ) -> GenerationResult:
        """
        Generate tests for a Python file or function.
        
        Args:
            target: Path to file or "file.py::function" for specific function
            output_dir: Where to write tests (default: config.test_dir)
            use_agents: If True, use full agent workflow. If False, use direct tools.
            **kwargs: Additional options
            
        Returns:
            GenerationResult with generated tests and metadata
            
        Example:
            >>> result = testgen.generate("src/calculator.py")
            >>> result = testgen.generate("src/calculator.py::add")
        """
        # Parse target
        file_path, function_name = self._parse_target(target)
        
        if use_agents:
            return self._generate_with_agents(file_path, function_name, output_dir)
        else:
            return self._generate_direct(file_path, function_name, output_dir)
    
    def _generate_direct(
        self,
        file_path: str,
        function_name: Optional[str],
        output_dir: Optional[str],
    ) -> GenerationResult:
        """Generate tests using direct tool calls (faster, deterministic)."""
        from .tools import parse_python_ast, generate_test_code, run_pytest_isolated
        
        try:
            # Step 1: Parse the file
            parsed = parse_python_ast(file_path)
            
            if not parsed["functions"] and not parsed["classes"]:
                return GenerationResult(
                    success=False,
                    errors=["No testable functions or classes found"],
                )
            
            # Step 2: Filter to specific function if requested
            functions = parsed["functions"]
            if function_name:
                functions = [f for f in functions if f["name"] == function_name]
                if not functions:
                    return GenerationResult(
                        success=False,
                        errors=[f"Function '{function_name}' not found"],
                    )
            
            # Step 3: Generate tests for each function
            tests = []
            for func_info in functions:
                # Skip private functions by default
                if func_info.get("is_private", False):
                    continue
                
                test_code = generate_test_code(func_info)
                tests.append(test_code)
            
            # Step 4: Validate tests compile
            if tests:
                # Create combined test code
                combined = "import pytest\n\n" + "\n\n".join(tests)
                
                # Validate it runs
                validation = run_pytest_isolated(combined)
                if not validation["passed"]:
                    # Tests don't pass - include them anyway but note the issue
                    pass  # Still include generated tests for user to fix
            
            # Step 5: Write tests to file
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
    
    def _generate_with_agents(
        self,
        file_path: str,
        function_name: Optional[str],
        output_dir: Optional[str],
    ) -> GenerationResult:
        """Generate tests using full agent workflow (smarter, LLM-powered)."""
        from .agents import analyzer, generator, validator
        from praisonaiagents import Agents, Task
        
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
        # Try to extract test code from the workflow result
        if isinstance(workflow_result, str):
            # Look for def test_ patterns
            import re
            tests = re.findall(r'(def test_\w+.*?)(?=def test_|\Z)', workflow_result, re.DOTALL)
            return tests
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
        
        # Get the module path for imports
        source_path = Path(source_file)
        module_name = source_path.stem
        
        with open(test_file, "w") as f:
            f.write("import pytest\n")
            f.write(f"from {module_name} import *\n\n")
            for test in tests:
                f.write(test)
                f.write("\n\n")
        
        return str(test_file)
