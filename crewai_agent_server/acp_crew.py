from collections.abc import Iterator
from typing import Any

from acp_sdk import Message, MessagePart
from acp_sdk.server import Context, Server
from crewai import LLM, Agent, Crew, Task
from crewai.agents.parser import AgentAction, AgentFinish
from pydantic import AnyUrl
from dotenv import load_dotenv
import os
import json
    
load_dotenv()

# ----- OpenAI Cloud MODEL Setup -----
llm = LLM(
    model=os.environ.get("OPENAI_MODEL_NAME", "gpt-4o-mini"),
    temperature=0.9,
    top_p=0.9,
    stream=False,
)

## Setup the ACP Server
server = Server()


@server.agent()
def song_writer_agent(input: list[Message], context: Context) -> Iterator:
    """Agent that writes a song about a website. Accepts a message with URL"""
    try:
        url = str(AnyUrl(str(input[-1])))
    except ValueError:
        yield MessagePart(content="This is not a URL, please provide valid website.")
        return

    website_scraper = Agent(
        llm=llm,
        role="Website Researcher",
        goal="Find useful content for songwriting from this text: Music is the art of arranging sounds.",
        backstory="Expert researcher who finds inspiring stories and themes online.",
        verbose=False,
    )

    song_writer = Agent(
        llm=llm,
        role="Songwriter",
        goal="Create songs from research material.",
        backstory="Talented songwriter who transforms information into emotional, memorable songs.",
        verbose=False,
    )

    scrape_task = Task(
        description="Research this URL for songwriting material: {url}",
        expected_output="Collection of themes, stories, and facts for songwriting inspiration.",
        agent=website_scraper,
    )

    write_song_task = Task(
        description="Write a song based on research.",
        expected_output="Complete song with lyrics and style based on research.",
        agent=song_writer,
    )

    crew = Crew(
        agents=[website_scraper, song_writer],
        tasks=[scrape_task, write_song_task],
        verbose=False,
        step_callback=lambda event, *args, **kwargs: step_callback(event, context, *args, **kwargs),
    )
    result = crew.kickoff(inputs={"url": url})
    yield MessagePart(content=result.raw)

@server.agent()
def markdown_report_agent(input: list[Message], context: Context) -> Iterator:
    """Agent that formats the original song and A&R feedback JSON into a markdown report."""
    try:
        payload = input[-1].parts[0].content
        data = json.loads(payload) if isinstance(payload, str) else payload
        song = data.get("song", "")
        feedback = data.get("feedback", {})
        # if isinstance(feedback, str):
            # feedback = eval(feedback)
    except Exception as e:
        yield MessagePart(content=f"Error parsing input: {e}")
        exit()

    md = [
        "## Generated Song",
        "",
        "```",
        song,
        "```",
        "",
        "## A&R Feedback",
        "",
        f"- **Hit Potential Score:** {feedback.get('hit_potential_score', '')}",
        f"- **Target Audience:** {feedback.get('target_audience', '')}",
        f"- **Strengths:** {feedback.get('strengths', '')}",
        f"- **Concerns:** {feedback.get('concerns', '')}",
        f"- **Market Comparison:** {feedback.get('market_comparison', '')}",
        f"- **Recommendation:** {feedback.get('recommendation', '')}",
    ]
    markdown_report = "\n".join(md)
    yield MessagePart(content=markdown_report)

def step_callback(event: Any, context: Context, *args, **kwargs) -> None:
    match event:
        case AgentAction():
            context.yield_sync(
                {
                    "thought": event.thought,
                    "tool": event.tool,
                }
            )
        case AgentFinish():
            context.yield_sync(
                {
                    "final_result": getattr(event, "result", str(event)),
                }
            )


if __name__ == "__main__":
    server.run()
