Configuration
=============

The grader supports configuration files in JSON format.
These configuration files define the checks to be performed on student submissions, 
along with their parameters and scoring criteria.

Configuration Schema
--------------------

Root Structure
~~~~~~~~~~~~~~

The configuration file has two possible root-level structures:

1. **Check-based configuration** - The most common format with a ``checks`` array
2. **Project structure configuration** - For defining required file patterns

Check-Based Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

The root object must contain a key called ``checks`` with an array of check objects.
Optionally, it can also include an ``environment`` object for global environment variables.

.. code-block:: json

    {
        "environment": {
            "variables": {
                "GLOBAL_VAR": "global_value",
                "API_KEY": "global_api_key"
            }
        },
        "checks": [
            {
                "name": "requirements",
                "max_points": 1,
                "is_venv_required": false
            }
        ]
    }

Root-Level Properties
^^^^^^^^^^^^^^^^^^^^^

``environment`` (optional)
    Global environment configuration that applies to all checks.
    
    - ``variables``: Object containing key-value pairs of environment variables

``checks`` (required)
    Array of check objects defining the grading checks to perform.

Check Object Properties
~~~~~~~~~~~~~~~~~~~~~~~

Common Properties
^^^^^^^^^^^^^^^^^

All check types support these common properties:

``name`` (required)
    The name/type of the check to perform. Supported values:
    
    - ``requirements`` - Validates presence of requirements.txt
    - ``pylint`` - Runs pylint code quality checks
    - ``type-hints`` - Validates type hints using mypy
    - ``coverage`` - Checks test coverage
    - ``tests`` - Runs unit tests
    - ``structure`` - Validates project file structure

``max_points`` (optional)
    The maximum score that can be awarded for this check.
    Can be an integer or float value.
    Some checks (like ``structure``) may not require this field.

``is_venv_required`` (required)
    Boolean indicating if the check should be run within a virtual environment.
    Can be a boolean value or a string ``"false"`` or ``"true"``.

``environment`` (optional)
    Check-specific environment configuration that overrides global environment variables.
    
    - ``variables``: Object containing key-value pairs of environment variables


Check-Specific Properties
^^^^^^^^^^^^^^^^^^^^^^^^^^

Pylint Check
""""""""""""

``pylintrc_path`` (optional)
    Path to a custom pylint configuration file.
    Supports template variables like ``${{config_dir}}``.
    
    Example:
    
    .. code-block:: json
    
        {
            "name": "pylint",
            "max_points": 3,
            "is_venv_required": true,
            "pylintrc_path": "${{config_dir}}/2024.pylintrc"
        }

Tests Check
"""""""""""

``tests_path`` (optional)
    Array of paths or URLs to test files to run.
    Can be local file paths or URLs to remote test files.

``default_test_score`` (optional)
    Default score assigned to each test if not specified in ``test_score_mapping``.

``test_score_mapping`` (optional)
    Object mapping test class or test function names to their point values.
    Keys can be test class names (e.g., ``TestCalculator``) or test function names (e.g., ``test_add``).

Example:

.. code-block:: json

    {
        "name": "tests",
        "max_points": 13.5,
        "is_venv_required": true,
        "tests_path": [
            "https://raw.githubusercontent.com/fmipython/pygrader-sample-project/refs/heads/main/tests/test_sample_code.py"
        ],
        "default_test_score": 1,
        "test_score_mapping": {
            "TestCalculator": 0.5,
            "test_add": 2,
            "test_divide": 2,
            "test_main_invalid_choice": 2.5
        }
    }

Structure Check
"""""""""""""""

``structure_file`` (optional)
    Path or URL to a JSON file defining the required project structure.
    Supports template variables like ``${{config_dir}}``.
    Can be a local path or a URL to a remote structure definition.

Example:

.. code-block:: json

    {
        "name": "structure",
        "is_venv_required": false,
        "structure_file": "${{config_dir}}/project_structure.json"
    }

Project Structure Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A separate configuration format is used to define required project file structures.
This file is referenced by the ``structure`` check via the ``structure_file`` property.

Each top-level key represents a structure category with the following properties:

``name`` (required)
    Human-readable name for this structure category.

``required`` (required)
    Boolean indicating if this structure category is mandatory.

``patterns`` (required)
    Array of glob patterns to match files.
    Supports wildcards like ``**/*.py`` for recursive matching.

Example:

.. code-block:: json

    {
        "source": {
            "name": "Source files",
            "required": true,
            "patterns": [
                "src/**/*.py"
            ]
        },
        "init": {
            "name": "Init files",
            "required": true,
            "patterns": [
                "src/**/__init__.py"
            ]
        },
        "tests": {
            "name": "Test files",
            "required": false,
            "patterns": [
                "tests/**/*.py",
                "tst/**/*.py"
            ]
        },
        "requirements": {
            "name": "Requirements file",
            "required": false,
            "patterns": [
                "requirements.txt"
            ]
        },
        "main": {
            "name": "Main file",
            "required": true,
            "patterns": [
                "main.py"
            ]
        },
        "readme": {
            "name": "Readme file",
            "required": false,
            "patterns": [
                "README.md"
            ]
        }
    }

Template Variables
~~~~~~~~~~~~~~~~~~

Configuration files support template variables for dynamic path resolution:

``${{config_dir}}``
    Expands to the directory containing the configuration file.
    Useful for referencing other config files relative to the main config.

Example:

.. code-block:: json

    {
        "checks": [
            {
                "name": "structure",
                "is_venv_required": false,
                "structure_file": "${{config_dir}}/project_structure.json"
            },
            {
                "name": "pylint",
                "max_points": 1,
                "is_venv_required": true,
                "pylintrc_path": "${{config_dir}}/2024.pylintrc"
            }
        ]
    }

Complete Example
~~~~~~~~~~~~~~~~

Here's a comprehensive example demonstrating multiple check types:

.. code-block:: json

    {
        "environment": {
            "variables": {
                "GLOBAL_VAR": "global_value",
                "API_KEY": "global_api_key"
            }
        },
        "checks": [
            {
                "name": "structure",
                "is_venv_required": false,
                "structure_file": "${{config_dir}}/project_structure.json"
            },
            {
                "name": "requirements",
                "max_points": 1,
                "is_venv_required": false
            },
            {
                "name": "pylint",
                "max_points": 3,
                "is_venv_required": true,
                "pylintrc_path": "${{config_dir}}/2024.pylintrc"
            },
            {
                "name": "type-hints",
                "max_points": 3,
                "is_venv_required": false
            },
            {
                "name": "coverage",
                "max_points": 5,
                "is_venv_required": true
            },
            {
                "name": "tests",
                "max_points": 13.5,
                "is_venv_required": true,
                "tests_path": [
                    "https://raw.githubusercontent.com/example/repo/main/tests/test_sample.py"
                ],
                "default_test_score": 1,
                "test_score_mapping": {
                    "TestExample": 0.5,
                    "test_function": 2
                },
                "environment": {
                    "variables": {
                        "TEST_VAR": "test_value"
                    }
                }
            }
        ]
    }
