# PythonProjectGrader

[![Tests](https://github.com/fmipython/PythonProjectGrader/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/fmipython/PythonProjectGrader/actions/workflows/tests.yml)[![GPL-3.0](https://img.shields.io/badge/license-GPL_3.0-blue.svg)](https://github.com/lyubolp/slightly-better-cut/blob/main/LICENSE)

A grader for Python projects, used in the ["Programming with Python"](https://github.com/fmipython) course at Sofia University "St. Kliment Ohridski", Faculty of Mathematics and Informatics.

Automatically grader Python projects based on a set of checks.
Current supported set of checks are:

- If the project has a requirements.txt file
- Pylint
- Type hints (via mypy)
- Code coverage (via pytest & coverage)

The tool supports configuration files, where you can specify the score for each check.

## Installation

1. Clone the repository and create a virtual environment:

```bash
git clone https://github.com/fmipython/PythonProjectGrader
cd PythonProjectGrader
python3 -m venv .venv
```

2. Activate the virtual environment:
   Linux/MacOS

```bash
source .venv/bin/activate
```

Or for Windows:

```bash
.venv\Scripts\activate
```

3. Install the package:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 main.py -c ./config/2024.json PROJECT_PATH
```

Where `PROJECT_PATH` is the path to the project you want to grade.

## Configuration

## Documentation

Link to the documentation [here](https://fmipython.github.io/PythonProjectGrader/)

## Contributing

## Licence

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)
