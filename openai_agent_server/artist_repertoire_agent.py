import textwrap
import os
from dotenv import load_dotenv
import json
import asyncio

from acp_sdk import Metadata, Annotations, Author, Capability
from acp_sdk.models.platform import PlatformUIAnnotation, PlatformUIType, AgentToolInfo
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import RunYield, RunYieldResume, Server, Context
from collections.abc import AsyncGenerator
from pydantic import BaseModel, Field
from typing import List, Optional
from agents import Agent, Runner, gen_trace_id, trace, set_default_openai_key, Prompt
from agents.mcp import MCPServer, MCPServerSseParams, MCPServerSse
from agents.model_settings import ModelSettings
from agents.items import TResponseInputItem

load_dotenv()

server = Server()

class SongEvaluationOutput(BaseModel):
    """Structured payload returned by the LLM for a song evaluation."""
    hit_potential_score: int = Field(
        description="Hit Potential Score (1-10): How likely is this to succeed commercially?"
    )
    target_audience: str = Field(
        description="Who would stream/buy this song?"
    )
    strengths: str = Field(
        description="What works well (hooks, lyrics, production)?"
    )
    concerns: str = Field(
        description="What might limit its success?"
    )
    market_comparison: str = Field(
        description="What successful artists/songs does this remind you of?"
    )
    recommendation: str = Field(
        description='Recommendation: "Sign", "Pass", or "Needs work?"'
    )

@server.agent(
    name="artist-repertoire-agent",
    description="An A&R agent that evaluates songs for commercial potential and artistic merit.",
    metadata=Metadata(
        framework="OpenAI",
        programming_language="Python",
        # annotations=Annotations(
        #     beeai_ui=PlatformUIAnnotation(
        #         ui_type=PlatformUIType.HANDSOFF,
        #         display_name="Artist & Repertoire Agent",
        #         user_greeting="Paste your song lyrics or description for A&R evaluation.",
        #         tools=[AgentToolInfo(name="WebSearch", description="Search the web for up-to-date information")]
        #     )
        # ),
        capabilities=[
            Capability(name="Song Evaluation", description="Assess commercial and artistic potential of songs"),
            Capability(name="Market Comparison", description="Compare songs to current hits and artists"),
            Capability(name="A&R Recommendation", description="Provide sign/pass/needs work recommendations")
        ],
        tags=["music", "A&R", "song-evaluation", "entertainment", "nlp"],
        documentation="""
### Artist & Repertoire Agent acts as an A&R Representative for a major record label, evaluating hit potential and artistic merit of songs.

#### Features
- Hit potential scoring (1-10)
- Target audience identification
- Strengths and concerns analysis
- Market comparison to current successful artists/songs
- Concise, industry-focused recommendations

#### Input Formats
- Song lyrics (text)
- Song metadata (optional)

#### Output
- JSON with hit score, audience, strengths, concerns, market comparison, and recommendation
"""
    )
)

async def artist_repertoire_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Evaluates commercial potential and artistic merit of a song and saves the output."""
    user_prompt = input[-1].parts[0].content if input and input[-1].parts else ""
    system_msg = textwrap.dedent("""
        You are an A&R Representative for a major record label. Your job is to evaluate commercial potential and artistic merit of songs.

        Analyze the provided song and return:
        1. Hit Potential Score (1-10): How likely is this to succeed commercially?
        2. Target Audience: Who would stream/buy this song?
        3. Strengths: What works well (hooks, lyrics, production)?
        4. Concerns: What might limit its success?
        5. Market Comparison: What successful artists/songs does this remind you of?
        6. Recommendation: Sign, pass, or needs work?

        Keep feedback concise and industry-focused. Think like someone who discovers the next big hit.
    """)

    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
    llm = Agent(
        name="Music Expert",
        instructions=system_msg,
        # prompt=Prompt(user_prompt),
        model=model_name,
        model_settings=ModelSettings(temperature=0.90, top_p=0.90),
        output_type=SongEvaluationOutput
    )

    response = await Runner.run(
        starting_agent=llm,
        input=str(user_prompt)
        )
    output = response.final_output

    # Save the thoughtful response to a Markdown file
    with open("json_response.md", "w") as f:
        f.write(f"## Song Evaluation\n\n```json\n{output}\n```\n")
    yield output

def run():
    server.run(port=9000)

if __name__ == "__main__":
    run()