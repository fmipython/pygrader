venv:
    . .venv/bin/activate

init:
    python3 -m venv .venv
    venv
    pip install -r requirements.txt

lint: venv
    python3 -m pylint $(git ls-files '*.py') --fail-under 9
    mypy grader --ignore-missing-imports
    flake8 grader

lint_file file: venv
    python3 -m pylint {{file}} --fail-under 9
    mypy {{file}} --ignore-missing-imports

test: venv
    python3 -m unittest discover -s tst

push: venv lint test
    git push

coverage: venv
    coverage run --source="src" -m unittest discover -s tst
    coverage report -m --fail-under 75
    coverage lcov -o lcov.info

run: venv
    python3 src/main.py