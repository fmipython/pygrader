# Claude AI Assistant Guide for pygrader

This document provides context and guidelines for Claude Sonnet 4.5 when working on the pygrader project.

## Project Overview

**pygrader** is an automated grading tool for Python projects used in the "Programming with Python" course at Sofia University. It evaluates student submissions based on multiple quality checks and generates grading reports.

### Key Information
- **Language**: Python 3.10+
- **Version**: 1.7.1
- **License**: GPL-3.0
- **Architecture**: Modular check-based system with CLI and web interfaces
- **Current Branch**: `show-check-results` (default: `main`)

## Project Structure

```
pygrader/
├── grader/                    # Core grading engine
│   ├── grader.py             # Main Grader orchestrator class
│   ├── checks/               # Check implementations
│   │   ├── abstract_check.py         # Base classes for all checks
│   │   ├── checks_factory.py         # Factory pattern for check creation
│   │   ├── coverage_check.py         # Code coverage validation
│   │   ├── pylint_check.py           # Linting checks
│   │   ├── requirements_check.py     # Dependency validation
│   │   ├── run_tests_check.py        # Test execution
│   │   ├── structure_check.py        # Project structure validation
│   │   └── type_hints_check.py       # Type hint checking (mypy)
│   └── utils/                # Shared utilities
│       ├── config.py                 # Configuration loading
│       ├── constants.py              # Project constants
│       ├── environment.py            # Environment management
│       ├── external_resources.py     # External resource handling
│       ├── files.py                  # File operations
│       ├── json_with_templates.py    # JSON template processing
│       ├── logger.py                 # Logging utilities
│       ├── process.py                # Subprocess management
│       ├── structure_validator.py    # Structure validation logic
│       └── virtual_environment.py    # venv management
├── desktop/                   # CLI interface
│   ├── cli.py                # Command-line argument parsing
│   ├── main.py               # Desktop entry point
│   └── results_reporter.py   # Results formatting/output
├── web/                       # Web interface (Flask/Django)
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests (test_*.py files)
│   └── functional/           # Integration tests
├── config/                    # Configuration templates
│   ├── *.json                # Various grading configurations
│   └── *.pylintrc            # Pylint configuration files
└── docs/                      # Sphinx documentation
    └── source/               # RST documentation files
```

## Core Concepts

### 1. Checks System
The grading system is built around **checks** - independent validation modules:

- **AbstractCheck**: Base class for all checks (`grader/checks/abstract_check.py`)
  - `ScoredCheck`: Checks that contribute to the final score
  - `NonScoredCheck`: Checks that only report pass/fail
- **ChecksFactory**: Creates check instances from configuration (`checks_factory.py`)
- Each check returns a `CheckResult` with the following fields:
  - `ScoredCheckResult`: Contains `name`, `result` (score), `info`, `error`, and `max_score`
    - `info`: Informational output about the check (e.g., coverage percentage, pylint summary)
    - `error`: Error messages if the check failed
  - `NonScoredCheckResult`: Contains `name`, `result` (pass/fail), `info`, and `error`
  - `CheckError`: Exception raised when a check cannot execute

### 2. Configuration System
- JSON-based configuration files in `config/` directory
- Supports templates via `json_with_templates.py`
- Defines which checks to run and their scoring weights
- Example configs: `2024.json`, `projects_2025.json`, `full.json`
- **Virtual Environment Configuration**: Optional `venv` key for customizing venv behavior:
  ```json
  {
    "venv": {
      "is_keeping_existing_venv": true,  // Keep existing .venv/.venv-pygrader
      "name": ".venv-custom"             // Custom venv directory name
    }
  }
  ```
- **Configuration Validation**: Currently NO schema validation
  - Unknown keys in config are silently ignored
  - Typos in venv config keys will cause defaults to be used
  - Consider adding validation for production use

### 3. Virtual Environment Management
- Each project is graded in an isolated virtual environment
- Managed by `VirtualEnvironment` class (`utils/virtual_environment.py`)
- Handles dependency installation from `requirements.txt` or `pyproject.toml`
- **Configuration Options**:
  - `is_keeping_venv_after_run`: Keep venv after grading (default: False)
    - Set via CLI: `--keep-venv` flag
    - Useful for debugging and inspecting installed packages
  - `is_keeping_existing_venv`: Don't delete existing .venv directories (default: False)
    - Set via config file `venv.is_keeping_existing_venv`
    - Speeds up repeated grading runs
  - `name`: Custom venv directory name (default: `.venv-pygrader`)
    - Set via config file `venv.name`
    - Prevents conflicts with student's own .venv

### 4. Grader Orchestration
The `Grader` class (`grader/grader.py`) orchestrates:
1. Configuration loading
2. Virtual environment setup
3. Check execution (in order)
4. Results aggregation
5. Cleanup

## Development Guidelines

### Code Style
- **Linting**: pylint (config: `.pylintrc`, `config/*.pylintrc`)
- **Type Hints**: mypy enforced (config: `mypy.ini`)
- **Formatting**: Follow existing patterns
- **Complexity**: Max cyclomatic complexity 15 (complexipy)
- **Line Length**: Follow project conventions

### Testing
- **Framework**: unittest with coverage (not pytest)
- **Test Runner**: `uv run -m unittest` or `just test`
- **Unit Tests**: `tests/unit/test_*.py` - test individual components
- **Functional Tests**: `tests/functional/test_functional.py` - end-to-end tests
- **Coverage Target**: 85% minimum (enforced by `just coverage`)
- **Coverage Tool**: coverage.py with lcov output

#### Testing Best Practices
- **Mock External Dependencies**: Use `@patch` decorators to mock external calls
  - Mock at the point of use, not at the import location
  - Example: Mock `pathlib.Path.exists` if code uses `Path().exists()`, not `os.path.exists`
- **Test CheckResult Fields**: When testing checks, verify all fields in `CheckResult`:
  - `name`: Check name
  - `result`: Score or pass/fail
  - `info`: Expected informational output (not empty string if check provides info)
  - `error`: Expected error messages (usually empty string for successful checks)
  - `max_score`: Maximum possible score
- **Access Private Methods in Tests**: Use Python name mangling for private methods:
  - `self.check_instance._ClassName__private_method()` to test internal logic
- **Run Specific Tests**: 
  ```bash
  # Run specific test class
  uv run python -m unittest tests.unit.test_pylint_check.TestPylintCheck -v
  
  # Run specific test method
  uv run python -m unittest tests.unit.test_pylint_check.TestPylintCheck.test_01_pylint_called -v
  ```

### Adding New Checks
1. Create new check class in `grader/checks/` inheriting from `AbstractCheck`
2. Implement required methods: `run()`, `__str__()`, `__repr__()`
3. Add check type to `ChecksFactory` in `checks_factory.py`
4. Add corresponding tests in `tests/unit/test_<check_name>.py`
5. Update documentation in `docs/source/`
6. Add configuration examples in `config/`

### Common Tasks

**Note**: This project uses [just](https://github.com/casey/just) as a command runner (see `justfile`) and [uv](https://github.com/astral-sh/uv) for Python package management.

#### Project Setup
```bash
just init                             # Create venv and install dependencies
```

#### Running the Grader Locally
```bash
# Run grader on a project
python pygrader.py --project-root <path_to_project> --config <config_file>

# Run with verbose mode to see info/error fields from checks
python pygrader.py --project-root <path_to_project> --config <config_file> -v

# Or with uv
uv run python pygrader.py --project-root <path_to_project> --config <config_file>
```

**Verbose Mode** (`-v` or `--verbosity` flag):
- Displays additional `info` and `error` fields from check results
- Shows detailed feedback like coverage percentages, pylint messages, test results
- Works with all output formats (text, JSON, CSV)
- Example output difference:
  - Normal: `Check: pylint, Score: 2/2`
  - Verbose: `Check: pylint, Score: 2/2. Info: main.py: Missing module docstring. Info: utils.py: Line too long`

#### Using Docker
```bash
# Build and run via convenience script
./run <path_to_project>

# Or build manually
just build_docker                     # Syncs uv, locks dependencies, builds Docker image
docker run -v <project_path>:/project pygrader
```

#### Linting and Quality Checks
```bash
just lint                             # Run all linters (pylint, mypy, flake8, complexipy)

# Individual linters
uv run pylint grader desktop tests pygrader.py --fail-under 9
uv run mypy grader desktop tests pygrader.py --ignore-missing-imports
uv run flake8 grader desktop tests pygrader.py
uv run complexipy .
```

#### Running Tests
```bash
just test                             # Run all tests (unit + functional)
just unit_tests                       # Unit tests only
just functional_tests                 # Functional tests only

# Manual test execution
uv run -m unittest discover -s tests/unit -p "test_*.py" -v
uv run -m unittest discover -s tests/functional -p "test_*.py"
```

#### Coverage Analysis
```bash
just coverage                         # Run tests with coverage (85% minimum)

# Manual coverage
uv run coverage run --source=grader,desktop -m unittest discover -s tests/unit -p "test_*.py"
uv run coverage report -m --fail-under 85 --sort=cover
uv run coverage lcov -o lcov.info     # Generate lcov report
```

#### Documentation
```bash
just docs                             # Generate Sphinx documentation

# Manual documentation build
uv run sphinx-apidoc -o docs/source grader
uv run sphinx-build -b html docs/source docs/build

# Build PlantUML diagrams
just build_diagrams                   # Requires plantuml.jar
```

#### Sample Project Management
```bash
just setup_sample_project             # Clone pygrader-sample-project for testing
just clean_sample_project             # Remove sample project
```

#### Cleanup
```bash
just clean                            # Remove build artifacts and logs
just clean_logs                       # Remove log files only
just clean_venv                       # Remove virtual environment
```

### File Patterns
- **Test files**: `test_*.py` in `tests/unit/` or `tests/functional/`
- **Check implementations**: `*_check.py` in `grader/checks/`
- **Utility modules**: `*.py` in `grader/utils/`
- **Config files**: `*.json` or `*.pylintrc` in `config/`

## Important Considerations

### When Making Changes

1. **Type Safety**: All code must pass mypy type checking
2. **Tests Required**: Add/update tests for any code changes
   - When modifying check output (info/error fields), update corresponding tests
   - Verify all CheckResult fields match the actual implementation
3. **Documentation**: Update RST docs for new features
4. **Backward Compatibility**: Consider existing config files
5. **Error Handling**: Use proper exception handling and logging
6. **Virtual Environments**: Be aware of isolation requirements

### Common Pitfalls

- **Path Handling**: Use absolute paths; project runs in containers
- **Virtual Environment State**: Clean up venvs unless `--keep-venv` specified
- **Config Validation**: Validate config structure early
- **Check Independence**: Checks should not depend on each other's state
- **External Dependencies**: Document any new dependencies in `pyproject.toml`

### Dependencies
**Build/Package Management**:
- `uv` - Fast Python package installer and resolver
- `just` - Command runner (alternative to make)

Core dependencies (from `pyproject.toml`):
- `pylint>=4.0.2` - Code linting
- `python-dotenv>=1.2.1` - Environment variable management
- `requests>=2.32.5` - HTTP requests for external resources

Dev dependencies:
- `coverage>=7.11.3` - Test coverage analysis
- `mypy>=1.18.2` - Type checking
- `flake8>=7.3.0` - Additional linting
- `sphinx>=8.1.3` - Documentation generation
- `complexipy>=4.2.0` - Cyclomatic complexity analysis

## Debugging Tips

1. **Logging**: Use `logger` passed to classes; check log output
2. **Virtual Environments**: Use `--keep-venv` flag to inspect created venv
3. **Configuration**: Validate JSON configs with `json_with_templates.py`
4. **Check Results**: Examine `CheckResult` objects for detailed information
   - `info` field contains user-facing output (summaries, percentages, etc.)
   - `error` field contains error messages if check failed
5. **Test Isolation**: Run single test files to isolate issues
6. **Mock Verification**: When tests fail, verify mocks patch the correct module/method
   - Check if code uses `pathlib.Path` vs `os.path` for file operations
   - Ensure subprocess mocks return the expected structure (`CompletedProcess` with stdout/stderr)

## Architecture Patterns

- **Factory Pattern**: `ChecksFactory` for check creation
- **Template Method**: `AbstractCheck` defines check execution flow
- **Strategy Pattern**: Different checks implement different validation strategies
- **Dependency Injection**: Logger and config injected into classes

## Quick Reference

### Key Classes
- `Grader` - Main orchestrator
- `AbstractCheck`, `ScoredCheck`, `NonScoredCheck` - Check base classes
- `ChecksFactory` - Check instantiation
- `VirtualEnvironment` - venv management
- `Config` - Configuration data structure

### Key Files
- `grader/grader.py` - Entry point for grading logic
- `grader/checks/abstract_check.py` - Check interface definitions
- `grader/utils/config.py` - Configuration loading
- `pygrader.py` - CLI entry point
- `pyproject.toml` - Project metadata and dependencies

### Testing Philosophy
- Unit tests mock external dependencies (subprocess calls, file system operations, etc.)
- Functional tests use real project structures
- Test both success and failure paths
- Validate error messages and logging
- **CheckResult Verification**: Always verify the complete `CheckResult` structure:
  - Tests should match the actual `info` and `error` fields returned by checks
  - Most checks populate the `info` field with useful feedback (e.g., "0.5% of the functions have type hints")
  - Empty `info` fields are only expected when checks don't provide additional information

### Common Testing Patterns

#### Testing Checks with Info Output
```python
# Example: Testing a check that provides info
@patch("grader.utils.process.run")
def test_check_with_info(self, mocked_run):
    # Arrange
    output = self._create_sample_output(score=5.0)
    mocked_run.return_value = CompletedProcess("tool", 0, output)
    
    # Calculate expected info using the same logic as the check
    expected_info = self.check._CheckClass__private_method(output)
    expected_result = ScoredCheckResult("check_name", 1, expected_info, "", 2)
    
    # Act
    actual_result = self.check.run()
    
    # Assert
    self.assertEqual(expected_result, actual_result)
```

#### Mocking File System Operations
```python
# When code uses pathlib.Path
@patch("pathlib.Path.exists")
def test_file_exists(self, mocked_exists):
    mocked_exists.return_value = True
    # ... test logic

# When code uses os.path
@patch("os.path.exists")
def test_file_exists_os(self, mocked_exists):
    mocked_exists.return_value = True
    # ... test logic
```

---

**Last Updated**: January 2026  
**For**: Claude Sonnet 4.5  
**Maintained by**: pygrader contributors
