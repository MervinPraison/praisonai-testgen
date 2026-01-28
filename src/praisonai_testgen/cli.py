"""
TestGen CLI - Command-line interface for test generation.

Extends testagent CLI patterns with generation commands.
"""

import typer
from typing import Optional
from pathlib import Path

app = typer.Typer(
    name="testgen",
    help="PraisonAI TestGen - AI-Powered Test Generation for Python",
    add_completion=False,
)


@app.command()
def init(
    path: str = typer.Argument(".", help="Project path to initialize"),
):
    """Initialize TestGen in a project."""
    config_dir = Path(path) / ".testgen"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "config.yaml"
    if not config_file.exists():
        config_file.write_text("""# TestGen Configuration
version: 1

project:
  test_dir: tests
  coverage_target: 80

llm:
  model: gpt-4o-mini

validation:
  threshold: 7.0
  use_cache: true

generation:
  max_tests_per_function: 10
  include_edge_cases: true
""")
    
    typer.echo(f"✓ Initialized TestGen in {path}")
    typer.echo(f"  Config: {config_file}")


@app.command()
def generate(
    target: str = typer.Argument(..., help="File or directory to generate tests for"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    function: Optional[str] = typer.Option(None, "--function", "-f", help="Specific function"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Generate tests for Python code."""
    from .testgen import TestGen
    
    # Handle function specifier
    if function:
        target = f"{target}::{function}"
    
    typer.echo(f"🔍 Analyzing {target}...")
    
    testgen = TestGen()
    result = testgen.generate(target, output_dir=output)
    
    if result.success:
        typer.echo(f"✓ Generated {len(result.tests)} tests")
        if result.test_file:
            typer.echo(f"  Output: {result.test_file}")
    else:
        typer.echo("✗ Generation failed", err=True)
        for error in result.errors:
            typer.echo(f"  Error: {error}", err=True)
        raise typer.Exit(1)


@app.command()
def update(
    since: str = typer.Option("HEAD~1", "--since", help="Git ref to compare against"),
):
    """Update tests for changed files."""
    from .testgen import TestGen
    
    typer.echo(f"🔄 Checking changes since {since}...")
    
    testgen = TestGen()
    result = testgen.update(since=since)
    
    if result.success:
        typer.echo(f"✓ Updated {len(result.tests)} tests")
    else:
        typer.echo("✗ Update failed", err=True)
        raise typer.Exit(1)


@app.command()
def report(
    risk: bool = typer.Option(False, "--risk", help="Include risk analysis"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Generate coverage report."""
    from .testgen import TestGen
    
    testgen = TestGen()
    data = testgen.report(include_risk=risk)
    
    if json_output:
        import json
        typer.echo(json.dumps(data, indent=2))
    else:
        typer.echo("📊 Coverage Report")
        typer.echo(f"  Coverage: {data.get('coverage', 'N/A')}%")


@app.command()
def validate(
    path: str = typer.Argument("tests/", help="Test directory to validate"),
):
    """Validate generated tests."""
    import subprocess
    
    typer.echo(f"🧪 Validating tests in {path}...")
    
    result = subprocess.run(
        ["pytest", path, "-v", "--tb=short"],
        capture_output=False,
    )
    
    if result.returncode == 0:
        typer.echo("✓ All tests passed")
    else:
        typer.echo("✗ Some tests failed", err=True)
        raise typer.Exit(result.returncode)


@app.command()
def version():
    """Show version information."""
    from . import __version__
    typer.echo(f"PraisonAI TestGen v{__version__}")


def main():
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
