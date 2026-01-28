# PraisonAI TestGen: AI-Powered Test Generation for Python

> **Open-Source, AI-Native Test Automation for Python/pytest**

---

## Executive Summary

PraisonAI TestGen is an open-source, AI-powered test generation and maintenance platform for Python projects. Unlike traditional code generation tools that produce tests once and leave maintenance to developers, PraisonAI TestGen **autonomously generates, validates, and maintains** unit tests as your codebase evolves.

### Built on Existing Packages (DRY Architecture)

PraisonAI TestGen leverages existing battle-tested packages rather than reinventing the wheel:

| Package | Role in TestGen | What We Reuse |
|---------|-----------------|---------------|
| **[praisonaiagents](https://github.com/MervinPraison/PraisonAI)** | Multi-agent orchestration | `Agent`, `Agents`, `Task`, `@tool`, hooks, memory |
| **[testagent](https://github.com/MervinPraison/TestAgent)** | Test validation engine | `test()`, `accuracy()`, judges, caching, CLI |
| **praisonai-testgen** (NEW) | Test generation & maintenance | Code analysis, generation, maintenance loop |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Package Architecture                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     praisonai-testgen (NEW)                         │   │
│   │         Test Generation • Maintenance • IDE/CI Integration          │   │
│   └───────────────────────────────┬─────────────────────────────────────┘   │
│                                   │                                          │
│           ┌───────────────────────┴───────────────────────┐                 │
│           │                                               │                 │
│           ▼                                               ▼                 │
│   ┌───────────────────────┐                   ┌───────────────────────┐    │
│   │    praisonaiagents    │                   │      testagent        │    │
│   │  ──────────────────── │                   │  ──────────────────── │    │
│   │  • Agent orchestration│                   │  • Test validation    │    │
│   │  • Task management    │                   │  • LLM-as-judge       │    │
│   │  • Tool framework     │                   │  • Caching (100x)     │    │
│   │  • Memory & hooks     │                   │  • Assertions         │    │
│   │  • Judge base class   │                   │  • CLI tools          │    │
│   └───────────────────────┘                   └───────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Value Proposition

| Problem | Solution |
|---------|----------|
| Writing tests is time-consuming | AI generates tests in seconds |
| Tests become stale as code evolves | Continuous maintenance on PRs/MRs |
| Code coverage is inconsistent | Autonomous coverage targeting |
| Legacy code is hard to test | Refactoring suggestions + testability analysis |
| Test selection is slow in CI | Patch-based smart test selection |

---

## Table of Contents

1. [Vision & Goals](#vision--goals)
2. [DRY Architecture](#dry-architecture)
3. [Mini Agent Pattern](#mini-agent-pattern)
4. [Component Mapping](#component-mapping)
5. [Feature Specifications](#feature-specifications)
6. [Technical Design](#technical-design)
7. [Project Structure](#project-structure)
8. [Roadmap & Milestones](#roadmap--milestones)
9. [API Reference](#api-reference)
10. [Configuration Reference](#configuration-reference)

---

## Vision & Goals

### Vision Statement

> **"Make every Python developer's codebase thoroughly tested with zero manual effort."**

### Primary Goals

1. **Autonomous Test Generation**: Generate human-readable, production-ready pytest tests that compile and run correctly on the first attempt.
2. **Continuous Maintenance**: Automatically update tests when source code changes—no test rot.
3. **Correct by Construction**: Every generated test is validated by execution before being proposed.
4. **Developer-Friendly**: Seamless workflows via IDE, CLI, and CI/CD integrations.
5. **DRY Architecture**: Leverage existing packages (`praisonaiagents`, `testagent`) rather than duplicating functionality.
6. **Minimal Configuration**: Use the "mini agent" pattern—only `name`, `instructions`, and `tools` required.

---

## Development Principles

> **These principles are MANDATORY for all development work on TestGen.**

### 1. TDD (Test-Driven Development)

```
RED → GREEN → REFACTOR
```

| Step | Action | Rule |
|------|--------|------|
| **RED** | Write failing test first | NO production code without a test |
| **GREEN** | Write minimal code to pass | Only enough to make the test pass |
| **REFACTOR** | Clean up code | Keep tests green |

**TDD Rules:**
- Every feature starts with a test
- Tests must fail before implementation
- Tests must be in `tests/` directory matching source structure
- Run `pytest -x` after every change

### 2. DRY (Don't Repeat Yourself)

```
REUSE → EXTEND → CREATE (last resort)
```

| Priority | Action | When |
|----------|--------|------|
| **1st** | Reuse | Use existing code from `praisonaiagents` or `testagent` |
| **2nd** | Extend | Subclass or wrap existing functionality |
| **3rd** | Create | Only if nothing exists to reuse |

**DRY Rules:**
- Check `praisonaiagents` before writing any agent code
- Check `testagent` before writing any validation code
- No duplicate logic - extract to shared functions
- Single source of truth for all configs

### 3. Agent-Centric Design

```
MINI AGENT PATTERN: name + instructions + tools
```

| Component | Keep | Avoid |
|-----------|------|-------|
| `name` | ✅ Required | - |
| `instructions` | ✅ Required | `role`, `goal`, `backstory` |
| `tools` | ✅ Optional | Inline logic in agents |
| Defaults | ✅ Use them | Over-configuration |

**Agent-Centric Rules:**
- Agents are the primary abstraction
- All business logic lives in `@tool` functions
- Agents only orchestrate - they don't contain logic
- Use `Agents` for multi-agent workflows

### 4. Minimal Work, Huge Impact

```
80/20 RULE: 20% effort → 80% value
```

| Principle | Do | Don't |
|-----------|-----|-------|
| **Focus** | Core functionality first | Edge cases upfront |
| **Iterate** | Small, working increments | Big bang releases |
| **Validate** | Test with real usage | Over-engineer |
| **Ship** | Working > Perfect | Wait for perfection |

**Minimal Work Rules:**
- Each PR delivers user-visible value
- Maximum 200 lines per PR (excluding tests)
- If it takes >2 hours, break it down
- Prefer simple solutions over clever ones

### 5. Code Quality Standards

```python
# ✅ GOOD: Clear, simple, tested
@tool
def parse_function(code: str) -> dict:
    """Parse Python function and extract metadata."""
    tree = ast.parse(code)
    return {"name": ..., "args": ...}

# ❌ BAD: Complex, untested, unclear
def do_stuff(x):
    # 100 lines of nested logic
    pass
```

**Quality Rules:**
- All functions have docstrings
- All public APIs have type hints
- Cyclomatic complexity < 10
- Test coverage > 80%

---

## DRY Architecture

### Design Philosophy

> **"Don't Repeat Yourself"** — Every capability in TestGen should reuse existing code from `praisonaiagents` or `testagent` wherever possible. New code is only written for genuinely new functionality.

### What We Reuse vs. What We Build

#### From `praisonaiagents` (Multi-Agent Framework)

| Component | Location | How TestGen Uses It |
|-----------|----------|---------------------|
| `Agent` | `praisonaiagents/agent/agent.py` | Base class for AnalyzerAgent, GeneratorAgent, etc. |
| `Agents` | `praisonaiagents/agents/agents.py` | Orchestrates multi-agent generation workflow |
| `Task` | `praisonaiagents/task/task.py` | Defines generation/validation tasks |
| `@tool` | `praisonaiagents/tools/decorator.py` | Creates AST parser, pytest runner tools |
| `Judge` | `praisonaiagents/eval/judge.py` | Base for test quality evaluation |
| Hooks | `praisonaiagents/hooks/` | Event system for progress tracking |
| Memory | `praisonaiagents/memory/` | Caches code analysis results |
| Guardrails | `praisonaiagents/guardrails/` | Validates generated test quality |

#### From `testagent` (Test Validation Framework)

| Component | Location | How TestGen Uses It |
|-----------|----------|---------------------|
| `test()` | `testagent/core.py` | Validates generated test assertions |
| `accuracy()` | `testagent/core.py` | Compares actual vs expected test output |
| `criteria()` | `testagent/core.py` | Evaluates test quality criteria |
| `TestAgentCache` | `testagent/cache.py` | Caches validation results (100x speedup) |
| `CodeJudge` | `testagent/judges/code.py` | Evaluates generated code quality |
| `approx`, `raises` | `testagent/assertions.py` | Assertion helpers for tests |
| `Collector` | `testagent/collector.py` | Test discovery for validation |
| CLI | `testagent/cli.py` | Extends for `testgen` commands |

#### What TestGen Adds (New Code)

| Component | Purpose | Why Not Reusable |
|-----------|---------|------------------|
| Code Analyzer | AST parsing for Python | Specific to test generation |
| Test Synthesizer | Generate pytest code | Core novel functionality |
| Maintenance Tracker | Source-test mapping | Novel maintenance loop |
| Dependency Graph | Code relationship mapping | Specific to optimization |
| IDE Plugin | VS Code integration | Platform-specific |
| CI Pipeline | GitHub/GitLab actions | Platform-specific |

---

## Mini Agent Pattern

### Philosophy: Minimal Configuration

PraisonAI Agents support a **"mini agent"** pattern where you only need to provide:
- `name` - Agent identifier
- `instructions` - What the agent does
- `tools` - (optional) Functions the agent can call

**No need for**: `role`, `goal`, `backstory`, or complex configs. Everything else has sensible defaults!

### TestGen Agents (Simplified)

```python
from praisonaiagents import Agent, Agents, Task, tool

# ============================================================================
# TOOLS - Simple functions with @tool decorator
# ============================================================================

@tool
def parse_python_ast(file_path: str) -> dict:
    """Parse Python file and extract functions/classes for testing."""
    import ast
    with open(file_path) as f:
        tree = ast.parse(f.read())
    
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                "name": node.name,
                "args": [a.arg for a in node.args.args],
                "lineno": node.lineno,
            })
    return {"file": file_path, "functions": functions}

@tool  
def infer_types(code: str) -> dict:
    """Infer types for function parameters and returns."""
    # Uses mypy or simple heuristics
    return {"types": {}}

@tool
def generate_test_code(function_info: dict) -> str:
    """Generate pytest test code for a function."""
    # LLM fills in the actual test logic
    return f"def test_{function_info['name']}():\n    pass"

@tool
def create_fixtures(dependencies: list) -> str:
    """Create pytest fixtures for test dependencies."""
    return "@pytest.fixture\ndef sample_data():\n    return {}"

@tool
def run_pytest(test_file: str) -> dict:
    """Execute pytest and return pass/fail results."""
    import subprocess
    result = subprocess.run(
        ["pytest", test_file, "-v", "--tb=short"],
        capture_output=True, text=True
    )
    return {
        "passed": result.returncode == 0,
        "output": result.stdout,
        "errors": result.stderr,
    }

@tool
def validate_test_quality(test_code: str) -> dict:
    """Validate test quality using testagent."""
    from testagent import CodeJudge
    
    judge = CodeJudge()
    result = judge.judge(test_code, criteria="well-structured pytest test")
    return {
        "score": result.score,
        "passed": result.passed,
        "feedback": result.reasoning,
    }

# ============================================================================
# AGENTS - Mini pattern: just name + instructions + tools
# ============================================================================

analyzer = Agent(
    name="Analyzer",
    instructions="Parse Python code and identify all testable functions and classes. Extract signatures, dependencies, and docstrings.",
    tools=[parse_python_ast, infer_types],
)

generator = Agent(
    name="Generator", 
    instructions="Create comprehensive pytest tests for the analyzed code. Include happy path, edge cases, and error handling tests.",
    tools=[generate_test_code, create_fixtures],
)

validator = Agent(
    name="Validator",
    instructions="Validate that generated tests compile, pass execution, and meet quality standards. Provide feedback for improvements.",
    tools=[run_pytest, validate_test_quality],
)

# ============================================================================
# WORKFLOW - Simple task chain
# ============================================================================

def generate_tests(source_file: str):
    """Generate tests for a Python file."""
    
    analyze_task = Task(
        description=f"Analyze {source_file} and identify all testable units",
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
    
    workflow = Agents(
        agents=[analyzer, generator, validator],
        tasks=[analyze_task, generate_task, validate_task],
    )
    
    return workflow.start()
```

### Comparison: Full Config vs Mini Pattern

```python
# ❌ VERBOSE (old pattern) - 8 lines per agent
analyzer_agent = Agent(
    name="Analyzer",
    role="Code Analyzer",
    goal="Parse and understand Python code structure",
    backstory="You are an expert Python developer who understands code architecture...",
    tools=[parse_python_ast, infer_types],
    llm="gpt-4o-mini",
    verbose=False,
    allow_delegation=False,
)

# ✅ MINI PATTERN - 4 lines per agent
analyzer = Agent(
    name="Analyzer",
    instructions="Parse Python code and identify testable functions",
    tools=[parse_python_ast, infer_types],
)
```

**Benefits of Mini Pattern:**
- 50% less code
- Faster to write and maintain
- `instructions` is more natural than separate `role`/`goal`/`backstory`
- Defaults are sensible (gpt-4o-mini, silent output, etc.)

---

## Component Mapping

### How Existing Components Map to TestGen Features

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   TestGen Feature → Existing Component                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   TESTGEN ENGINE                                                             │
│   ├── Analyzer ──────────────────→ Agent(instructions=..., tools=[...])     │
│   ├── Generator ─────────────────→ Agent(instructions=..., tools=[...])     │
│   ├── Validator ─────────────────→ testagent.test() + testagent.CodeJudge   │
│   ├── Workflow Orchestration ────→ praisonaiagents.Agents (sequential)      │
│   └── Quality Guardrails ────────→ praisonaiagents.guardrails              │
│                                                                              │
│   VALIDATION & JUDGING                                                       │
│   ├── Test Execution Check ──────→ testagent.accuracy()                     │
│   ├── Code Quality Check ────────→ testagent.CodeJudge                      │
│   ├── Assertion Validation ──────→ testagent.approx, testagent.raises       │
│   └── Result Caching ────────────→ testagent.TestAgentCache                 │
│                                                                              │
│   REPORTS & OPTIMIZATION                                                     │
│   ├── Coverage Collection ───────→ pytest-cov (external)                    │
│   ├── Quality Scoring ───────────→ praisonaiagents.eval.Judge               │
│   └── Test Selection ────────────→ NEW (TestGen-specific)                   │
│                                                                              │
│   CLI & INTEGRATIONS                                                         │
│   ├── CLI Framework ─────────────→ testagent.cli (extend with Typer)        │
│   ├── MCP Server ────────────────→ praisonaiagents.mcp                      │
│   └── IDE/CI Plugins ────────────→ NEW (TestGen-specific)                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Test Validation Using testagent

```python
from testagent import test, accuracy, criteria, CodeJudge, TestAgentCache

class TestGenValidator:
    """Validates generated tests using testagent."""
    
    def __init__(self):
        self.cache = TestAgentCache()  # 100x speedup
        self.code_judge = CodeJudge()
    
    def validate_passes(self, test_code: str) -> bool:
        """Check if test actually passes."""
        result = self._run_test(test_code)
        return accuracy(output=str(result.passed), expected="True").passed
    
    def validate_quality(self, test_code: str) -> dict:
        """Check test quality."""
        result = self.code_judge.judge(
            test_code,
            criteria="pytest test with clear assertions"
        )
        return {"score": result.score, "passed": result.passed}
    
    def validate_assertions(self, test_code: str) -> dict:
        """Check that assertions are meaningful."""
        result = criteria(
            output=test_code,
            criteria="contains meaningful assertions, not just 'assert True'"
        )
        return {"meaningful": result.passed}
```

---

## Feature Specifications

### 1. TestGen Engine (Core)

The foundational test generation and maintenance engine, built on `praisonaiagents`.

#### 1.1 Simple API

```python
from praisonai_testgen import TestGen

# One-liner
result = TestGen().generate("src/calculator.py")

# With options
testgen = TestGen(coverage_target=80)
result = testgen.generate("src/", include_edge_cases=True)
```

#### 1.2 Correct-by-Construction Loop

```
┌──────────┐     ┌───────────┐     ┌────────────────────────────────┐
│ Generate │ ──▶ │  Execute  │ ──▶ │  Validate with testagent       │
│  Tests   │     │   Tests   │     │  ├─ test() - basic validation  │
└──────────┘     └───────────┘     │  ├─ CodeJudge - quality check  │
      ▲                             │  └─ accuracy() - correctness  │
      │                             └────────────────┬───────────────┘
      │                                              │
      │                      ┌───────────────────────┤
      │                      │                       │
      │               ┌──────▼──────┐         ┌─────▼─────┐
      └─── Retry ◀────│   Failed    │         │  Passed   │ ──▶ Output
                      └─────────────┘         └───────────┘
```

### 2. TestGen CLI

Extends `testagent` CLI with generation commands.

```bash
# Test generation
testgen init                      # Initialize TestGen in project
testgen generate src/             # Generate tests for directory
testgen generate src/calc.py      # Generate tests for file  
testgen update                    # Update tests for changed code

# Validation (reuses testagent)
testgen validate tests/           # Validate all generated tests

# Reporting
testgen report                    # Coverage report
testgen report --risk             # Risk analysis

# Direct testagent access
testgen test "output" --criteria "is correct"
testgen accuracy "4" --expected "4"
```

### 3. TestGen Plugin (VS Code)

```
┌──────────────────────────────────────────────────────────────────────┐
│  VS Code                                                              │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  calculator.py                 │  Tests Panel                        │
│  ─────────────                 │  ───────────                        │
│  def add(a, b):                │  ✓ test_add_positive (generated)   │
│      return a + b  [Gen Tests] │  ✓ test_add_negative (generated)   │
│                                │  ⚠ test_add_overflow (needs fix)   │
│  def subtract(a, b):           │                                     │
│      return a - b  [Gen Tests] │  Coverage: 87%                      │
│                                │                                     │
│  [Coverage: 45%]              │  [Regenerate] [Validate All]        │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### 4. TestGen Pipeline (CI/CD)

```yaml
# .github/workflows/testgen.yaml
name: PraisonAI TestGen
on:
  pull_request:
    branches: [main]

jobs:
  testgen:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: praisonai/testgen-action@v1
        with:
          mode: generate-and-commit
          coverage-target: 80
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### 5. TestGen Annotations

```python
from praisonai_testgen import testgen

@testgen.skip  # Never generate tests
def internal_helper():
    pass

@testgen.mock("external_api.call")  # Always mock this
def fetch_data():
    return external_api.call()

@testgen.priority(high=True)  # Generate tests first
def critical_payment_logic():
    pass

@testgen.edge_cases(amount=[0, 100, -1, float("inf")])
def calculate_tax(amount: float):
    pass
```

---

## Technical Design

### Technology Stack (DRY)

| Layer | Technology | Source |
|-------|------------|--------|
| **Agent Framework** | `praisonaiagents` | REUSE |
| **Test Validation** | `testagent` | REUSE |
| **LLM Integration** | LiteLLM via praisonaiagents | REUSE |
| **Code Analysis** | `ast`, `LibCST` | NEW |
| **Test Framework** | pytest, pytest-cov | EXTERNAL |
| **CLI** | Typer (extend testagent) | EXTEND |
| **IDE Plugin** | VS Code Extension API | NEW |
| **CI Integration** | GitHub Actions | NEW |

### Dependency Graph

```
praisonai-testgen
├── praisonaiagents (core dependency)
│   ├── Agent (mini pattern: name + instructions + tools)
│   ├── Agents, Task
│   ├── @tool decorator
│   ├── Judge (evaluation)
│   └── hooks, memory, guardrails
├── testagent (validation dependency)
│   ├── test(), accuracy(), criteria()
│   ├── CodeJudge
│   ├── TestAgentCache
│   └── CLI framework
├── libcst (code analysis)
├── pytest (test execution)
└── typer (CLI extension)
```

---

## Project Structure

```
praisonai-testgen/
├── src/
│   └── praisonai_testgen/
│       ├── __init__.py
│       ├── testgen.py            # Main TestGen class
│       │
│       ├── agents/               # Mini agents (name + instructions + tools)
│       │   ├── __init__.py
│       │   ├── analyzer.py       # Analyzer agent
│       │   ├── generator.py      # Generator agent
│       │   └── validator.py      # Validator agent (uses testagent)
│       │
│       ├── tools/                # @tool decorated functions
│       │   ├── __init__.py
│       │   ├── ast_parser.py     # parse_python_ast()
│       │   ├── type_inferencer.py
│       │   ├── test_synthesizer.py
│       │   ├── fixture_builder.py
│       │   └── pytest_runner.py
│       │
│       ├── validation/           # testagent integration
│       │   ├── __init__.py
│       │   └── validator.py      # Uses testagent.test(), CodeJudge
│       │
│       ├── maintenance/          # Source-test mapping (NEW)
│       │   ├── __init__.py
│       │   ├── tracker.py
│       │   └── updater.py
│       │
│       ├── cli/                  # Extends testagent CLI
│       │   ├── __init__.py
│       │   └── commands.py
│       │
│       └── annotations/          # Decorators
│           ├── __init__.py
│           └── decorators.py
│
├── vscode-extension/
├── github-action/
├── docs/
├── tests/
├── pyproject.toml
└── README.md
```

---

## Roadmap & Milestones

### Phase 1: Foundation (v0.1.0) — 4 weeks

**Goal**: Core engine with mini agents

| Task | Approach | Effort |
|------|----------|--------|
| Analyzer agent | Mini pattern + AST tools | 1 week |
| Generator agent | Mini pattern + synthesis tools | 1.5 weeks |
| Validator agent | Mini pattern + testagent | 0.5 weeks |
| Workflow | `Agents` orchestration | 0.5 weeks |
| Basic CLI | `testgen generate` | 0.5 weeks |

**Deliverables**:
- Generate tests for simple functions
- Validation using testagent
- `testgen generate` command

---

### Phase 2: Maintenance (v0.2.0) — 3 weeks

**Goal**: Test maintenance loop

| Task | Effort |
|------|--------|
| Source-test mapping | 1 week |
| Update detection | 0.5 weeks |
| Update generation | 1 week |
| `testgen update` | 0.5 weeks |

---

### Phase 3: Reports & Optimization (v0.3.0) — 3 weeks

| Task | Effort |
|------|--------|
| Coverage reports | 1 week |
| Quality scoring | 0.5 weeks |
| Test selection | 1.5 weeks |

---

### Phase 4: IDE & CI (v0.4.0) — 4 weeks

| Task | Effort |
|------|--------|
| VS Code extension | 3 weeks |
| GitHub Action | 0.5 weeks |
| GitLab CI | 0.5 weeks |

---

### Phase 5: v1.0.0 — 2 weeks

| Task | Effort |
|------|--------|
| Annotations | 0.5 weeks |
| MCP integration | 0.5 weeks |
| Polish & docs | 1 week |

**Total: ~16 weeks to v1.0.0**

---

## API Reference

### Main API

```python
from praisonai_testgen import TestGen

testgen = TestGen()

# Generate tests
result = testgen.generate("src/calculator.py")
result = testgen.generate("src/calculator.py::add")  # Specific function

# Update tests  
result = testgen.update(since="HEAD~1")

# Reports
report = testgen.report()
report = testgen.report(include_risk=True)

# Optimization
tests = testgen.affected_tests(since="main")
```

### Configuration

```python
from praisonai_testgen import TestGen, TestGenConfig

config = TestGenConfig(
    test_dir="tests",
    coverage_target=80,
    validation_threshold=7.0,  # Passed to testagent
)

testgen = TestGen(config=config)
```

---

## Configuration Reference

```yaml
# .testgen/config.yaml
version: 1

project:
  test_dir: tests
  coverage_target: 80
  
llm:
  model: gpt-4o-mini  # Default, uses OPENAI_MODEL_NAME env
  
validation:
  threshold: 7.0      # testagent score threshold
  use_cache: true     # testagent cache (100x speedup)
  
generation:
  max_tests_per_function: 10
  include_edge_cases: true
  
maintenance:
  auto_update: true
```

---

## Summary: DRY + Mini Pattern

| Feature | Implementation | Source |
|---------|---------------|--------|
| Agent definitions | `Agent(name=..., instructions=..., tools=[...])` | praisonaiagents |
| Agent orchestration | `Agents`, `Task` | praisonaiagents |
| Tool creation | `@tool` decorator | praisonaiagents |
| Test validation | `testagent.test()`, `accuracy()` | testagent |
| Quality judging | `testagent.CodeJudge` | testagent |
| Caching | `testagent.TestAgentCache` | testagent |
| CLI | Extend testagent CLI | testagent |
| Code analysis | AST + libcst (NEW) | praisonai-testgen |
| Test synthesis | NEW | praisonai-testgen |
| Maintenance | NEW | praisonai-testgen |

> **Result**: ~60% reuse from existing packages. Mini pattern reduces agent code by 50%. Only genuinely new code for code analysis, synthesis, and maintenance.

---

*Document Version: 3.0.0*  
*Product Name: PraisonAI TestGen*  
*Last Updated: 2025-01-28*  
*Architecture: DRY + Mini Agent Pattern*
