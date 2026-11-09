# Imports
from pydantic import BaseModel, Field
from agents import Agent, ModelSettings, WebSearchTool
from messenger_solution import send_email_tool
from dotenv import load_dotenv
import os

# Constants
load_dotenv(override=True)
NUM_SEARCH_TERMS = os.getenv("NUM_SEARCH_TERMS", 5) 
MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME") 


## Followup agent ##

# Output type
class followups(BaseModel):
    followups: list[str] = Field(description="A list of follow-up questions")

# Instruction
instructions_research_assistant = """
You are a research assistant. Given a user query for a research report, you generate three follow-up questions to clarify the requirements for the report.
"""

#Agent
research_assistant = Agent(name="Research Assistant", instructions=instructions_followup_agent, model=MODEL_NAME, output_type=followups)



## Planner agent ##

# Output type
class search_term(BaseModel):
    reason: str = Field(description="short reason for this search term")
    term:   str = Field(description="The term for the websearch")

class planner_results(BaseModel):
    search_terms: list[search_term] = Field(description="A list of web searchs to perform to best answer the query.")

# Instruction
instructions_planner_agent = f"""
You are an assistant who writes search terms for websearch.
Your Task: Given a query, you generate {NUM_SEARCH_TERMS} search terms to best answer the query. 
"""

# Agent
planner_agent = Agent(name = "Planner Agent", instructions=instructions_planner_agent, model= MODEL_NAME, output_type=planner_results)



## Search agent ##

# Instruction
instructions_search_agent = f"""
You are an assistant who does websearch.
Your Task: Given a search term, you perform a web search using the WebSearchTool.
You respond with a summary of your results in 2-3 paragraphs in a maximum of 300 words, by capturing the main points and being succinct. 
"""

# Agent
search_model_settings = ModelSettings(tool_choice="required")
search_agent = Agent(name = "Search Agent", instructions=instructions_search_agent, model= MODEL_NAME, tools=[WebSearchTool()], model_settings=search_model_settings)



## Writer agent ##

# Output type
class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    markdown_report: str = Field(description="The final report")
    follow_up_questions: list[str] = Field(description="Suggested topics to research further")

# Instruction
instructions_writer_agent = """
You are a senior researcher tasked with writing a cohesive report for a research query.
You will be provided with the original query, and some research.
Generate a comprehensive report based on the research and the query.
The final output should be in markdown format, and it should be lengthy and detailed. Aim 
for 5-10 pages of content, at least 1000 words.
"""

# Agent
writer_agent = Agent(name = "Writer Agent", instructions=instructions_writer_agent, model= MODEL_NAME, output_type=ReportData)



## Email agent ##

# Instructions
instructions_email_agent = """
You are provided with a detailed report. Use your tool to send an email, converting the report into
a clean, well presented HTML email with an appropriate subject line.

Rule: The email body should contain only the report, and nothing else. For example: no salutations, 'I can also draft email in another tone' kind of remarks.
"""
# Agent
email_sender_agent = Agent(name = "Email Sender Agent", instructions=instructions_email_agent, model= MODEL_NAME, tools=[send_email_tool], model_settings=ModelSettings(tool_choice="required"))