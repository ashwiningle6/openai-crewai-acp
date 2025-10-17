# openai-crewai-acp
ACP communication between different Agentic Frameworks
Given an website URL the CrewAI agent will generate a song from the URL content (if accessible)
The song is then passed on to the OpenAI agent that will evaluate it on different parameters
The Song & evaluated parameters and then sent to CrewAI for a markdown file creation 

## Create a pyproject.toml file in the project folder
$ uv init

## Import existing requirements
$ uv add -r requirements.txt

## Create & activate virtual environment
uv venv
.venv/bin/activate

## Syncs all the imported libraries with the tomel file
$ uv sync

## Check that all dependencies were imported correctly:
$ uv pip freeze

## Run CrewAI agent (Terminal 1)
uv run ./crewai_agent_server/acp_crew.py

## Run OpenAI agent (Terminal 2)
uv run ./openai_agent_server/artist_repertoire_agent.py

## Run ACP client (Terminal 3)
uv run acp_client.py
pass any URL