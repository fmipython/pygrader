#!/bin/sh
set -e

# Copy project files from bind mount to working directory
cp -r /tmp/project_bind/* /project/

# Run the grader
exec uv run --no-dev pygrader.py --config ./config/projects_2025.json /project
