venv:
    . .venv/bin/activate

init:
    python3 -m venv .venv
    venv
    pip install -r requirements.txt

lint: venv
    python3 -m pylint grader tests main.py --fail-under 9
    mypy grader --ignore-missing-imports
    flake8 grader

lint_file file: venv
    python3 -m pylint {{file}} --fail-under 9
    mypy {{file}} --ignore-missing-imports

test: venv
    python3 -m unittest discover -s tests

push: venv lint test
    git push

coverage: venv
    coverage run --source="grader" -m unittest discover -s tests
    coverage lcov -o lcov.info
    coverage report -m --fail-under 75

run: venv
    python3 src/main.py

docs: venv
    sphinx-apidoc -o docs/source grader
    sphinx-build -b html docs/source docs/build