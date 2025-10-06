import os
from crewai import Agent, LLM
from crewai_tools import SerperDevTool
from tools.youtube_search_tool import YoutubeVideoSearchTool
from crewai.tools import BaseTool
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OpenRouter API key not set in OPENROUTER_API_KEY")

llm = LLM(
    model="openrouter/deepseek/deepseek-r1",
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    stream=True,
    temperature=0.4
)

class CompanyResearchAgents:
    def __init__(self):
        self.llm = llm
        self.searchInternetTool = SerperDevTool()
        self.youtubeSearchTool = YoutubeVideoSearchTool()
        print("Setting up agents for company research")

        # Wrap tools for Agent correctly
        self.tools = [
            BaseTool(name="WebSearch", func=self.searchInternetTool),
            BaseTool(name="YouTubeSearch", func=self.youtubeSearchTool)
        ]


    def research_manager(self, companies: list[str], positions: list[str]) -> Agent:
        companies_str = ", ".join(companies)
        positions_str = ", ".join(positions)
        goal = f"""
Generate JSON objects with:
- URLs + titles for 3 recent blog posts
- URLs + titles for 3 recent YouTube interviews
Per position for each company.

Companies: {companies_str}
Positions: {positions_str}

Rules:
- Include *all* companies & positions.
- Use "MISSING" if no data found for a position.
- Don't invent data — only return verified info.
- Continue searching until you have data for each position.
- Each position must have exactly 3 blog posts + 3 interviews.
"""
        backstory = """
You are a Company Research Manager. Your job is to fetch recent, credible info
(blog + video interviews) for given companies and positions. Do this thoroughly
and truthfully.
"""

        agent = Agent(
            role="Company Research Manager",
            goal=goal,
            backstory=backstory,
            llm=self.llm,
            tools=self.tools,
            verbose=True,
            allow_delegation=True
        )
        return agent

    def company_research_agent(self) -> Agent:
        goal = """
Look up the specific positions for a given company and find urls for 3 recent blog articles and
the url and title for 3 recent YouTube interview for each person in the specified positions. Return this info in a JSON object.
"""
        backstory = """As a Company Research Agent, you are responsible for looking up specific positions
within a company and gathering relevant information."""

        agent = Agent(
            role="Company Research Agent",
            goal=goal,
            backstory=backstory,
            llm=self.llm,
            tools=self.tools,
            verbose=True,
            allow_delegation=False
        )
        return agent
