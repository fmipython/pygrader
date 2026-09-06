"""Configuration for Cove API integration."""

from dataclasses import dataclass


@dataclass
class CoveConfig:
    """Configuration for Cove API integration."""

    base_url: str
    api_key: str
    project_id: str
