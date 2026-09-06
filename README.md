# pygrader

<img src="https://raw.githubusercontent.com/fmipython/PythonProjectGrader/refs/heads/main/logo.png" alt="Logo" width="200" height="200">

[![pygrader CI&CD](https://github.com/fmipython/pygrader/actions/workflows/cicd.yml/badge.svg)](https://github.com/fmipython/pygrader/actions/workflows/cicd.yml)[![GPL-3.0](https://img.shields.io/badge/license-GPL_3.0-blue.svg)](https://github.com/lyubolp/slightly-better-cut/blob/main/LICENSE)

A grader for Python projects, used in the ["Programming with Python"](https://github.com/fmipython) course at Sofia University "St. Kliment Ohridski", Faculty of Mathematics and Informatics.

Automatically grader Python projects based on a set of checks.
Current supported set of checks are:

- Project structure
- Pylint
- Type hints (via mypy)
- Code coverage (via pytest & coverage)
- Run the code against certain tests
- If the project has a requirements.txt/pyproject.toml file
- Grade the project against a markdown specification, using an LLM

The tool supports configuration files, where you can specify the score for each check.

## How to use (easier way)

1. If you don't have Docker (or Docker Desktop) already, install it from [here](https://docs.docker.com/get-docker).

2. Download or clone this repository, if you haven't already.

3. Navigate to the project repository in a terminal and execute the following command:

```bash
./run <path_to_Python_project>
```

Replace `<path_to_Python_project>` with the path to your project directory. This command should work on all operating systems.

⚠️ _If you are on Windows, `<path_to_Python_project>` should be a full path, not a relative one. For example, write `C:\Users\YourName\Documents\Project` instead of just `..\Project`._

## How to use 2.0 (raw way)

1. Clone the repository and create a virtual environment:

```bash
git clone https://github.com/fmipython/pygrader
cd pygrader
python3 -m venv .venv
```

2. Activate the virtual environment:

   - On Linux/MacOS:

   ```bash
   source .venv/bin/activate
   ```

   - On Windows:

   ```bash
   .venv\Scripts\activate
   ```

3. Install the dependencies:

```bash
pip install .
```

## Usage

```bash
python3 pygrader.py -c CONFIG_PATH PROJECT_PATH
```

Where `PROJECT_PATH` is the path to the project you want to grade and `CONFIG_PATH` is the path to the configuration you want to use.

`PROJECT_PATH` can also be a glob pattern matching several projects (e.g. one folder per student, each holding a zip archive downloaded in bulk from Moodle), in which case each match is graded separately, using the student ID parsed from its path as the run ID:

```bash
uv run pygrader.py --report-format json -c ./config/projects_2026_summer.json "/home/lyubolp/downloaded_projects/**/*.zip"
```

Note that `**` here is not a recursive glob (only one directory level is matched) - quote the pattern so your shell doesn't expand it first and pygrader can match it itself.

## Configuration

The grader supports configuration files in JSON format.
The configuration specifies which checks to run, their maximum score, as well as other requirements.
Refer to the [documentation](https://fmipython.github.io/pygrader//config.html) for more information.

## Documentation

Link to the documentation [here](https://fmipython.github.io/pygrader/)

## Contributing

## Licence

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)
