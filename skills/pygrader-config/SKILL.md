---
name: pygrader-config
description: Create or edit a pygrader grading configuration (the JSON file passed via --config). Use when the user wants a new grading config, to add/change checks or point values, to set up a structure file, test scoring, venv options, environment variables or a spec-graded check.
metadata:
  version: 1.0.0
  pygrader-version: ">=2.2.0"
---

# Creating a pygrader configuration

A grading config is a JSON file passed to pygrader with `--config`. It lists the checks to
run, how many points each is worth, and their options. The full reference is
`docs/source/config.rst`. When this skill and that file disagree, the file wins: update this
skill and bump its version.

## Workflow

1. Ask what should be graded (lint, type hints, coverage, the course's own tests,
   project structure, requirements, LLM spec grading) and the points for each, unless already given.
2. Write the config to `config/<name>.json`. Put companion files (structure JSON, pylintrc,
   spec.md) next to it and reference them with `${{config_dir}}`.
3. Validate it (see **Validate** below) before handing it over.

## Root object

```json
{
    "environment": { "variables": { "KEY": "value" } },
    "venv": { "is_keeping_existing_venv": false, "name": ".venv-pygrader" },
    "checks": [ ... ]
}
```

- `checks` (required): array of check objects; they run in this order.
- `environment.variables` (optional): env vars for every check. A check's own
  `environment.variables` overrides them.
- `venv` (optional): only the keys `is_keeping_existing_venv` (bool, default `false`) and
  `name` (default `.venv-pygrader`). Any other key fails the run. A venv is only created when some
  check has `"is_venv_required": true`.
- Other unknown root keys are **silently ignored**, so a typo goes unnoticed. Check the spelling.

## Common check keys

| Key | Required | Notes |
|---|---|---|
| `name` | yes | Check type: `requirements`, `pylint`, `type-hints`, `coverage`, `tests`, `structure`, `complexity`, `spec` |
| `is_venv_required` | yes | JSON boolean. `"false"` (a string) counts as `true` |
| `max_points` | scored checks | int or float. **Not allowed** on `structure` and `complexity` (pass/fail) |
| `environment` | no | `{ "variables": {...} }`, overrides the global variables |
| `assets` | no | Array of local paths / URLs / `cove://` URIs |

Any key not listed here or in the check's own section **fails the run**: it's passed
to the check's constructor as a keyword argument.

## Per-check options

- **requirements**: `is_checking_install` (bool, default `false`) also checks that
  `requirements.txt` installs. Without it, the check only looks for the file. Awards all or nothing.
- **pylint**: `pylintrc_path` (local path only; default is the bundled `config/2024.pylintrc`).
  Needs `"is_venv_required": true` so pylint can resolve the project's imports.
- **type-hints**: no options. Scores the share of lines with type annotations (via mypy).
- **coverage**: no options. Runs the project's tests under coverage. Needs `"is_venv_required": true`.
- **tests**: runs course-provided test files against the project. Needs `"is_venv_required": true`.
  - `tests_path` (required): array of local paths, URLs or `cove://` Python items.
  - `default_test_score` (default `0`): points for each test that has no mapping.
  - `test_score_mapping`: `{ "TestClass": 0.5, "test_func": 2 }`. A class value applies to
    **each** test in that class; a test-name entry takes precedence over its class entry.
  - The weights of **all** tests (passed + failed) must add up to ≤ `max_points`, otherwise the check
    errors. Make them add up to exactly `max_points`.
- **structure** (pass/fail): `structure_file` (required; path, URL or `cove://` JSON item),
  `is_fatal` (bool, stored but not acted on yet).
- **complexity** (pass/fail): `max_complexity` (default `15`), `is_fatal`.
- **spec** (LLM grading): the first `assets` entry must be the markdown spec. Optional
  `model`, `base_url` (OpenAI-compatible, default OpenRouter), `api_key_env` (default
  `OPENROUTER_API_KEY`). The API key must be set in the environment / `.env`.

## How points are awarded

`pylint`, `coverage` and `type-hints` award points in **steps**, not proportionally. The tool's
result (pylint 0-10, coverage 0-100%, type hints 0-100%) is split into `ceil(max_points) + 1`
equal ranges, which award `0, step, ..., max_points`, where `step = max_points / ceil(max_points)`.

- `max_points: 3` → 4 ranges → `0 / 1 / 2 / 3` (coverage ≥ 75% gets full marks)
- `max_points: 1.5` → 3 ranges → `0 / 0.75 / 1.5`

So a large `max_points` makes the scoring finer-grained. Explain this to the user when they pick values.

## Structure file

A separate JSON file referenced by `structure_file`. Each top-level key is one category:

```json
{
    "source": { "name": "Source files", "required": true,  "patterns": ["src/**/*.py"] },
    "tests":  { "name": "Test files",   "required": false, "patterns": ["tests/**/*.py"] },
    "main":   { "name": "Main file",    "required": true,  "patterns": ["main.py"] }
}
```

## Remote resources and templates

- `${{config_dir}}` expands to the config's directory (for remote/Cove configs, the temp dir it was
  downloaded to). **Any other `${{...}}` placeholder is an error.**
- The config itself, `tests_path` and `structure_file` accept `http(s)`/`ftp` URLs and `cove://`
  URIs. `pylintrc_path` accepts only a local path. Cove needs `COVE_API_KEY`.

## Example

```json
{
    "venv": { "is_keeping_existing_venv": true },
    "checks": [
        { "name": "structure", "is_venv_required": false,
          "structure_file": "${{config_dir}}/project_structure.json" },
        { "name": "requirements", "max_points": 1, "is_venv_required": false, "is_checking_install": true },
        { "name": "pylint", "max_points": 3, "is_venv_required": true,
          "pylintrc_path": "${{config_dir}}/2024.pylintrc" },
        { "name": "type-hints", "max_points": 1.5, "is_venv_required": true },
        { "name": "coverage", "max_points": 5, "is_venv_required": true },
        { "name": "tests", "max_points": 6, "is_venv_required": true,
          "tests_path": ["${{config_dir}}/tests/test_solution.py"],
          "default_test_score": 1,
          "test_score_mapping": { "TestEdgeCases": 0.5 } },
        { "name": "complexity", "is_venv_required": false, "max_complexity": 15 }
    ]
}
```

More examples live in `config/` (`full.json`, `projects_2026_summer.json`, `spec_example.json`,
`templates_example.json`).

## Validate

Build the checks without grading anything. This catches unknown check names, missing required keys,
bad options and bad `${{...}}` templates:

```bash
uv run python -c "from grader.utils.config import load_config; from grader.checks.checks_factory import create_checks; c = load_config('config/<name>.json'); print(create_checks(c, '.'))"
```

Then do a real run on a sample project (`just setup_sample_project` clones one):

```bash
uv run python pygrader.py <project_path> --config config/<name>.json -v
```

Use `--checks pylint,coverage` to run a subset while iterating.

## Changelog

- **1.0.0**: Initial version, matching pygrader 2.2.0 (float `max_points` with scaled steps).
