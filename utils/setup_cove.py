from cove_sdk import CoveClient

with CoveClient(base_url="http://127.0.0.1:8001") as client:
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

    client.json_items.create(
        project_id=project.id,
        name="config",)
