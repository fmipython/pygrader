"""
Module containing the spec check.

It grades a project against a markdown specification using an LLM via an
OpenAI-compatible chat completions endpoint (OpenRouter by default).
"""

import json
import logging
import os
from typing import Optional

import requests
from dotenv import load_dotenv

from grader.checks.abstract_check import ScoredCheck
from grader.exceptions import CheckError, ResourceError
from grader.models.check_result import ScoredCheckResult
from grader.utils.files import find_all_source_files

logger = logging.getLogger("grader")
load_dotenv()

SYSTEM_PROMPT = (
    "You are grading a Python student project against a written specification. "
    "Score strictly on evidence in the provided source: cite file paths for anything you "
    "credit or dock. Do not award points for functionality the specification did not ask for."
)

_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "spec_grade",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "score": {"type": "number"},
                "rationale": {"type": "string"},
            },
            "required": ["score", "rationale"],
            "additionalProperties": False,
        },
    },
}


class SpecCheck(ScoredCheck):
    """The spec check class."""

    def __init__(
        self,
        name: str,
        project_root: str,
        max_points: int,
        is_venv_required: bool = False,
        env_vars: Optional[dict[str, str]] = None,
        assets: Optional[list[str]] = None,
        model: str = "anthropic/claude-opus-5",
        base_url: str = "https://openrouter.ai/api/v1",
        api_key_env: str = "OPENROUTER_API_KEY",
    ) -> None:
        """
        Initialize the spec check.

        :param name: The name of the check.
        :param project_root: The root directory of the project.
        :param max_points: The maximum points this check can award.
        :param is_venv_required: Whether a virtual environment is required.
        :param env_vars: Optional environment variables for the check.
        :param assets: The spec file, as a single-entry list (local path, URL or Cove URI).
        :param model: The model id to grade with, as accepted by the completions endpoint.
        :param base_url: The base URL of the OpenAI-compatible chat completions API.
        :param api_key_env: The environment variable holding the API key.
        """
        super().__init__(name, max_points, project_root, is_venv_required, env_vars, assets)
        self.__model = model
        self.__base_url = base_url
        self.__api_key_env = api_key_env

    def run(self) -> ScoredCheckResult:
        """
        Grade the project against its specification using an LLM.

        :raises CheckError: If the spec cannot be read, the API call fails, or the response is malformed.
        :return: The score and rationale from the check.
        """
        self._pre_run()

        if not self.assets:
            raise CheckError("No spec file configured; add its path/URL to the check's 'assets' list")

        try:
            spec = self.assets[0].read()
        except ResourceError as error:
            raise CheckError(f"Cannot read spec file: {error}") from error

        source = self.__collect_source()
        score, rationale = self.__grade(spec, source)
        clamped_score = max(0.0, min(score, float(self.max_points)))

        return ScoredCheckResult(self.name, clamped_score, rationale, "", self.max_points)

    def __collect_source(self) -> str:
        """
        Concatenate the project's source files into a single string for the prompt.

        Test files are excluded, matching :func:`find_all_source_files`.

        :raises CheckError: If a source file cannot be read or is not valid UTF-8.
        :return: The concatenated source, one section per file.
        """
        chunks = []
        for path in find_all_source_files(self._project_root):
            relative_path = os.path.relpath(path, self._project_root)
            try:
                with open(path, "r", encoding="utf-8") as file_pointer:
                    chunks.append(f"# === {relative_path} ===\n{file_pointer.read()}")
            except (OSError, UnicodeDecodeError) as error:
                raise CheckError(f"Cannot read source file {relative_path}: {error}") from error

        return "\n\n".join(chunks)

    def __grade(self, spec: str, source: str) -> tuple[float, str]:
        """
        Call the LLM and parse its score/rationale for the project.

        :param spec: The specification markdown.
        :param source: The concatenated project source.
        :raises CheckError: If the API key is missing, the call fails, or the response is malformed.
        :return: A (score, rationale) tuple.
        """
        api_key = os.environ.get(self.__api_key_env)
        if not api_key:
            raise CheckError(f"{self.__api_key_env} environment variable is not set")

        user_prompt = (
            f"# Specification\n{spec}\n\n"
            f"# Project source\n{source}\n\n"
            f"Score this project out of {self.max_points} points against the specification above."
        )

        payload = {
            "model": self.__model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": _RESPONSE_FORMAT,
        }

        try:
            response = requests.post(
                f"{self.__base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
                timeout=180,
            )
        except requests.RequestException as error:
            raise CheckError(f"Error calling {self.__base_url}: {error}") from error

        if response.status_code != 200:
            raise CheckError(f"LLM endpoint returned {response.status_code}: {response.text}")

        try:
            body = response.json()
        except json.JSONDecodeError as error:
            raise CheckError(f"LLM endpoint returned invalid JSON: {response.text}") from error

        if "error" in body:
            raise CheckError(f"LLM endpoint returned an error: {body['error']}")

        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as error:
            raise CheckError(f"Unexpected LLM response shape: {body}") from error

        return SpecCheck.__parse_grade(content)

    @staticmethod
    def __parse_grade(content: str) -> tuple[float, str]:
        """
        Parse the model's JSON grade, tolerating a markdown code fence around it.

        :param content: The raw message content returned by the model.
        :raises CheckError: If the content is not valid JSON or misses required fields.
        :return: A (score, rationale) tuple.
        """
        stripped = content.strip()
        if stripped.startswith("```"):
            stripped = stripped.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        try:
            parsed = json.loads(stripped)
            return float(parsed["score"]), str(parsed["rationale"])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise CheckError(f"Could not parse model output as a grade: {content}") from error
