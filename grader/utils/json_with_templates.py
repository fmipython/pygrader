import json


def load_with_values(file_path: str, **kwargs: str) -> dict:
    """
    Load a JSON file with template placeholders and replace them with provided values.
    :param file_path: Path to the JSON file.
    :param values: Key-value pairs to replace in the JSON file.
    :return: The processed JSON content as a dictionary.
    """
    with open(file_path, encoding="utf-8") as config_file:
        content = config_file.read()

    for key, value in kwargs.items():
        placeholder = "${{" + key + "}}"
        content = content.replace(placeholder, str(value))

    return json.loads(content)
