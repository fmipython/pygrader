.. PythonProjectGrader documentation master file, created by
   sphinx-quickstart on Fri Feb  7 18:55:43 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PythonProjectGrader
===================

A grader for Python projects, used in the `"Programming with Python" <https://github.com/fmipython>`_ course at Sofia University "St. Kliment Ohridski", Faculty of Mathematics and Informatics.

Automatically grade Python projects based on a set of checks.
Current supported set of checks are:

- If the project has a requirements.txt file
- Pylint
- Type hints (via mypy)
- Code coverage (via pytest & coverage)

The tool supports configuration files, where you can specify the score for each check.

=======================
Quickstart (via Docker)
=======================

1. If you don't have Docker (or Docker Desktop) already, install it from [here](https://docs.docker.com/get-docker).

2. Download or clone this repository, if you haven't already.

3. Navigate to the project repository in a terminal and execute the following command:

.. code:: bash

   ./run <path_to_Python_project>


Replace ``<path_to_Python_project>`` with the path to your project directory. This command should work on all operating systems.

⚠️ *If you are on Windows,* ``<path_to_Python_project>`` *should be a full path, not a relative one. For example, write* ``C:\Users\YourName\Documents\Project`` *instead of just* ``..\Project``.

=======================
Quickstart (via source)
=======================

1. Clone the repository and create a virtual environment:

.. code:: bash
   
   git clone https://github.com/fmipython/PythonProjectGrader
   cd PythonProjectGrader
   python3 -m venv .venv

2. Activate the virtual environment: Linux/MacOS - ``source .venv/bin/activate``, or for Windows - ``.venv\Scripts\activate``

3. Install the package: 
``pip install -r requirements.txt``

4. Run the grader:
``python3 main.py -c ./config/2024.json PROJECT_PATH``

Where ``PROJECT_PATH`` is the path to the project you want to grade.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   functionality
   install
   config
   checks
   dev_guide
