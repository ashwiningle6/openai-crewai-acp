# openai-crewai-acp
ACP communication between different Agent Frameworks

# Create a pyproject.toml file in the project folder
$ uv init

# Import existing requirements
$ uv add -r requirements.txt

# Create & activate virtual environment
uv venv
.venv/bin/activate

# Syncs all the imported libraries with the tomel file
$ uv sync

# Check that all dependencies were imported correctly:
$ uv pip freeze