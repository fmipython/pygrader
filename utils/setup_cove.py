import json

import requests
from cove_sdk import CoveClient

with CoveClient(base_url="http://localhost:8001") as client:
    client.login("pygrader", "1234")

    projects = client.projects.list()

    if "pygrader-test" not in [p.name for p in projects]:
        print("Creating project pygrader-test")
        response = client.projects.create("pygrader-test")
        project_id = response.project_id
    else:
        print("Project pygrader-test already exists. Using existing project.")
        project_id = [p.id for p in projects if p.name == "pygrader-test"][0]

    if project_id is None:
        raise Exception("Failed to create or find project pygrader-test")

    project = client.projects.get(project_id)

    print(f"Project ID: {project.id}")

    test_code = client.python_items.get(project_id=project.id, key="test_code")

    code_value = requests.get(
        "https://raw.githubusercontent.com/fmipython/pygrader-sample-project/refs/heads/main/tests/test_sample_code.py"
    ).text

    if test_code is None:
        print("Creating Python item 'test_code' for project pygrader-test")
        client.python_items.create(project_id=project.id, key="test_code", code=code_value)
    else:
        print("Python item 'test_code' already exists for project pygrader-test")

    with open("config/cove_test.json", "r") as f:
        value = json.load(f)

    value["checks"][2]["tests_path"] = [f"cove://localhost:8001/python_item/{project.id}/test_code"]

    config = client.json_items.get(project_id=project.id, key="config")
    if config is None:
        print("Creating JSON item 'config' for project pygrader-test")
        client.json_items.create(project_id=project.id, key="config", value=value)
    else:
        print("JSON item 'config' already exists for project pygrader-test")
        print(config.json_value)

    api_keys = [api_key.access_for_project_id for api_key in client.api_keys.list()]

    if project.id in api_keys:
        print("API key for project pygrader-test already exists. Using existing API key.")
    else:
        print("Creating API key for project pygrader-test")
        result = client.api_keys.create(project_id=project.id)

        print(f"Created API key {result.key}")
