from grader.utils.cli import get_args
from grader.utils.virtual_environment import VirtualEnvironment
from grader.checks.pylint import PylintCheck

if __name__ == "__main__":
    print("Python project grader, v0.1")
    args = get_args()
    print(args)

    with VirtualEnvironment(args["project_root"]) as venv:
        pylint = PylintCheck("pylint", 3)
        pylint.run()
