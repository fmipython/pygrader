venv:
    . .venv/bin/activate

init:
    python3 -m venv .venv
    venv
    pip install -r requirements.txt

lint: venv
    python3 -m pylint grader desktop tests pygrader.py --fail-under 9
    mypy grader desktop tests pygrader.py --ignore-missing-imports
    flake8 grader desktop tests pygrader.py
    complexipy .

lint_file file: venv
    python3 -m pylint {{file}} --fail-under 9
    mypy {{file}} --ignore-missing-imports

test: unit_tests functional_tests

unit_tests: venv
    find tests -type f -name "test_*.py" -not -name "test_functional.py" -not -path "*sample_project*" | xargs python3 -m unittest -v

functional_tests: venv
    python3 -m unittest discover -s tests -p "test_functional.py"

push: venv lint test
    git push

coverage: venv
    find tests -type f -name "test_*.py" -not -name "test_functional.py" | xargs coverage run --source="grader,desktop" -m unittest
    coverage lcov -o lcov.info
    coverage report -m --fail-under 85 --sort=cover

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
    rm -rf *.log.*
    rm -rf "pygrader-sample-project"

clean_logs:
    rm -rf *.log.*
    rm -rf *.log

clean_venv:
    rm -rf .venv


setup_sample_project: clean_sample_project
    git clone https://github.com/fmipython/pygrader-sample-project


clean_sample_project:
    if [ -d "pygrader-sample-project" ]; then rm -rf "pygrader-sample-project"; fi


build_diagrams:
    java -jar ~/plantuml-1.2025.4.jar ./docs/diagrams/*.puml -o out

build_docker:
    docker build -f Dockerfile -t pygrader:latest .