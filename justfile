venv:
    . .venv/bin/activate

init:
    python3 -m venv .venv
    venv
    pip install -r requirements.txt

lint: venv
    python3 -m pylint grader tests pygrader.py --fail-under 9
    mypy grader --ignore-missing-imports
    flake8 grader

lint_file file: venv
    python3 -m pylint {{file}} --fail-under 9
    mypy {{file}} --ignore-missing-imports

test:
    unit_tests
    functional_tests: venv-

unit_tests: venv
    find tests -type f -name "test_*.py" -not -name "test_functional.py" | xargs python3 -m unittest

functional_tests: venv
    python3 -m unittest discover -s tests -p "test_functional.py"

push: venv lint test
    git push

coverage: venv
    find tests -type f -name "test_*.py" -not -name "test_functional.py" | xargs coverage run --source="grader" -m unittest
    coverage lcov -o lcov.info
    coverage report -m --fail-under 75

run: venv
    python3 src/pygrader.py

docs: venv
    sphinx-apidoc -o docs/source grader
    sphinx-build -b html docs/source docs/build

clean:
    rm -rf .coverage
    rm -rf .pytest_cache
    rm -rf .mypy_cache
    rm -rf docs/build
    rm -f lcov.info
    rm -rf *.log

clean_logs:
    rm -rf *.log

clean_venv:
    rm -rf .venv