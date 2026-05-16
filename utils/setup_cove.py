import json

from cove_sdk import CoveClient

from grader.utils.cove_config import CoveConfig

cc = CoveConfig(
    base_url="http://127.0.0.1:8001", api_key="9b256764-fc22-458b-bc69-3a52a6bb2877"
)


with CoveClient(**cc.to_dict()) as client:
    # client.login("pygrader", "1234")

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

    with open("config/full_single_point.json", "r") as f:
        value = json.load(f)

    config = client.json_items.get(project_id=project.id, key="config")
    if config is None:
        print("Creating JSON item 'config' for project pygrader-test")
        client.json_items.create(project_id=project.id, key="config", value=value)
    else:
        print("JSON item 'config' already exists for project pygrader-test")
        print(config.json_value)
