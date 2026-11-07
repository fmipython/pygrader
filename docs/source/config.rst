Configuration
=============

The grader supports configuration files in JSON format.
These configuration files define the checks to be performed on student submissions, 
along with their parameters and scoring criteria.

The file passed via ``--config`` can be a local path, an ``http``/``https``/``ftp`` URL,
or a ``cove://`` URI pointing to a JSON item (requires the ``COVE_API_KEY`` environment variable).

Configuration Schema
--------------------

There are two kinds of JSON files:

1. **Grading configuration** - The file passed via ``--config``, with a ``checks`` array
2. **Project structure configuration** - A separate file referenced by the ``structure`` check

Grading Configuration
~~~~~~~~~~~~~~~~~~~~~

The root object must contain a key called ``checks`` with an array of check objects.
Optionally, it can also include ``environment`` and ``venv`` objects.
Unknown root-level keys are silently ignored, so double-check spelling.

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

``venv`` (optional)
    Configuration for the virtual environment used by checks that require one.

    - ``is_keeping_existing_venv``: Boolean. If ``true``, an existing venv directory in the
      project is reused instead of being deleted and recreated. Default: ``false``.
    - ``name``: Custom name for the virtual environment directory, to avoid conflicts with a
      student's own ``.venv``. Default: ``.venv-pygrader``.

    Any other key inside ``venv`` makes the run fail. The venv is only created if at least one
    check has ``is_venv_required`` set to ``true``.

    Example:

    .. code-block:: json

        {
            "venv": {
                "is_keeping_existing_venv": true,
                "name": ".venv-custom"
            },
            "checks": [
                {
                    "name": "coverage",
                    "max_points": 5,
                    "is_venv_required": true
                }
            ]
        }

Check Object Properties
~~~~~~~~~~~~~~~~~~~~~~~

Common Properties
^^^^^^^^^^^^^^^^^

All check types support these common properties. Any key not listed here or under the
check's own section is rejected and makes the run fail.

``name`` (required)
    The name/type of the check to perform. Supported values:
    
    - ``requirements`` - Validates presence of requirements.txt
    - ``pylint`` - Runs pylint code quality checks
    - ``type-hints`` - Validates type hints using mypy
    - ``coverage`` - Checks test coverage
    - ``tests`` - Runs unit tests
    - ``structure`` - Validates project file structure
    - ``spec`` - Grades the project against a markdown specification using an LLM

``max_points`` (required for all checks except ``structure``)
    The maximum score that can be awarded for this check.
    Can be an integer or float value.
    The ``structure`` check is pass/fail and does not accept this field.

``is_venv_required`` (required)
    Boolean indicating if the check should be run within a virtual environment.
    Must be a JSON boolean (``true``/``false``). Strings are not parsed - ``"false"``
    is a non-empty string and is treated as ``true``.

``environment`` (optional)
    Check-specific environment configuration that overrides global environment variables.

    - ``variables``: Object containing key-value pairs of environment variables

``assets`` (optional)
    Array of resource sources available to the check.
    Each entry can be a local path, a URL, or a ``cove://`` URI, and is exposed to the
    check as a ``Resource`` object via the check's ``assets`` property.
    Cove URIs require the ``COVE_API_KEY`` environment variable.

    Example:

    .. code-block:: json

        {
            "name": "coverage",
            "max_points": 5,
            "is_venv_required": true,
            "assets": [
                "${{config_dir}}/reference_data.json",
                "cove://fmi-python/some-asset"
            ]
        }

Check-Specific Properties
^^^^^^^^^^^^^^^^^^^^^^^^^^

Requirements Check
""""""""""""""""""

``is_checking_install`` (optional)
    Boolean indicating whether to also verify that the dependencies listed in
    ``requirements.txt`` can actually be installed, in addition to checking that the file
    is present. Default: ``false``.

    Example:

    .. code-block:: json

        {
            "name": "requirements",
            "max_points": 1,
            "is_venv_required": false,
            "is_checking_install": true
        }

Pylint Check
""""""""""""

``pylintrc_path`` (optional)
    Local path to a custom pylint configuration file.
    Supports template variables like ``${{config_dir}}``.
    URLs and Cove URIs are not supported. Default: the bundled ``config/2024.pylintrc``.
    If the file does not exist, pylint runs with its own defaults.

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

``tests_path`` (required)
    Array of test files to run.
    Each entry can be a local path, a URL, or a ``cove://`` URI pointing to a Python item
    (requires the ``COVE_API_KEY`` environment variable).

``default_test_score`` (optional)
    Default score assigned to each test if not specified in ``test_score_mapping``.
    Default: ``0``.

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

``is_fatal`` (optional)
    Boolean marking the check as fatal. Default: ``false``.

    .. note::
        The flag is stored on the check but not acted upon yet - a failing structure check
        does not currently abort the grading run.

``structure_file`` (required)
    Path, URL or Cove URI to a JSON file defining the required project structure.
    Supports template variables like ``${{config_dir}}``.
    Can be a local path, a URL to a remote structure definition, or a ``cove://`` URI
    pointing to a JSON item. Cove URIs require the ``COVE_API_KEY`` environment variable.

Example:

.. code-block:: json

    {
        "name": "structure",
        "is_venv_required": false,
        "structure_file": "${{config_dir}}/project_structure.json"
    }

Example with a Cove URI:

.. code-block:: json

    {
        "name": "structure",
        "is_venv_required": false,
        "structure_file": "cove://fmi-python/project-structure"
    }

Type Hints and Coverage Checks
""""""""""""""""""""""""""""""

The ``type-hints`` and ``coverage`` checks take no options beyond the common properties.

Spec Check
""""""""""

Grades the project's source against a markdown specification using an LLM, via an
OpenAI-compatible chat completions endpoint (`OpenRouter <https://openrouter.ai>`_ by default).
The specification is passed via the check's ``assets`` list (see ``assets`` above) and
must be the first entry.

``model`` (optional)
    The model id to grade with, as accepted by the completions endpoint.
    Default: ``anthropic/claude-opus-5``.

``base_url`` (optional)
    The base URL of the OpenAI-compatible chat completions API.
    Default: ``https://openrouter.ai/api/v1``.

``api_key_env`` (optional)
    The environment variable holding the API key for ``base_url``.
    Default: ``OPENROUTER_API_KEY``.

Example:

.. code-block:: json

    {
        "name": "spec",
        "max_points": 10,
        "is_venv_required": false,
        "assets": [
            "${{config_dir}}/spec.md"
        ]
    }

.. note::
    A single spec file is shared across every project in a batch run - per-project spec
    resolution is not supported yet.

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
    For remote and Cove configs, this is the temporary directory the config was downloaded to.

Any other ``${{...}}`` placeholder in the file is an error.

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
