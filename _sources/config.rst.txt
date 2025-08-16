Configuration
=============

The grader supports configuration files in JSON format.
These config files specify the following things:

- The name of the check
- The maximum score for the check
- If the check should be run within a virtual environment

A sample configuration file is shown below:

.. code :: json

    {
        "checks": [
            {
                "name": "requirements",
                "max_points": 1,
                "requires_venv": false
            },
            {
                "name": "pylint",
                "max_points": 3,
                "requires_venv": true
            },
            {
                "name": "type-hints",
                "max_points": 3,
                "requires_venv": false
            },
            {
                "name": "coverage",
                "max_points": 5,
                "requires_venv": true
            }
        ]
    }


The generic structure of the configuration file is as follows:

The root object must contain a key called ``checks``.
This key should have a list of objects, each representing a check.
Each check object should have the following keys: ``name``, ``max_points``, and ``requires_venv``.

The values for these keys are as follows:
``name`` - The name of the check. This is used to identify the check in the output.
``max_points`` - The maximum score that can be awarded for this check.
``requires_venv`` - A boolean value indicating if the check should be run within a virtual environment.
