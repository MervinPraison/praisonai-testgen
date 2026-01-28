"""
PraisonAI TestGen - AI-Powered Test Generation for Python/pytest.

The simplest way to generate and maintain tests for your Python code.

Usage:
    >>> from praisonai_testgen import TestGen
    >>> testgen = TestGen()
    >>> result = testgen.generate("src/calculator.py")
    >>> print(result.tests)

CLI:
    $ testgen generate src/
    $ testgen update
    $ testgen report
"""

__version__ = "0.1.0"
__all__ = [
    # Main class
    "TestGen",
    "TestGenConfig",
    # Results
    "GenerationResult",
    # Agents
    "analyzer",
    "generator", 
    "validator",
]

# Lazy imports for fast startup
_LAZY_IMPORTS = {
    "TestGen": ("testgen", "TestGen"),
    "TestGenConfig": ("testgen", "TestGenConfig"),
    "GenerationResult": ("testgen", "GenerationResult"),
    "analyzer": ("agents", "analyzer"),
    "generator": ("agents", "generator"),
    "validator": ("agents", "validator"),
}


def __getattr__(name: str):
    """Lazy import mechanism for zero-cost imports when not used."""
    if name in _LAZY_IMPORTS:
        module_name, attr_name = _LAZY_IMPORTS[name]
        import importlib
        module = importlib.import_module(f".{module_name}", __name__)
        return getattr(module, attr_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """Return list of available attributes for tab completion."""
    return __all__
