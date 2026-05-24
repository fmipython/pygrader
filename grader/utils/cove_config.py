from dataclasses import dataclass


@dataclass
class CoveConfig:
    base_url: str
    api_key: str
    project_id: str
