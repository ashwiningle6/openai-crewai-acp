# openai-crewai-acp
ACP communication between different Agent Frameworks

# Create a pyproject.toml file 
$ uv init --bare
This creates a minimal pyproject.toml without sample code.

# Import your existing requirements 
$ uv add -r requirements.txt
This command:
Reads dependencies from requirements.txt
Adds them to pyproject.toml
Creates/updates the lockfile
Installs dependencies in the project environment

# Check that all dependencies were imported correctly:
$ uv pip freeze

# Manage dependencies using uv 
# Add new runtime dependency
$ uv add requests

# Add development dependency
$ uv add --dev pytest

# Remove dependency
$ uv remove requests


uv venv
source .venv/bin/activate

uv sync