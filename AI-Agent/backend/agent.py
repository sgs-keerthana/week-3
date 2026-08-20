from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from tools.weather import get_weather
from tools.calendar import calendar_tool
from tools.gmail import gmail_tool

#1. Create the Qwen3.5 model
model=ChatOllama(
    model="qwen3.5:4b",
    temperature=0.1,
    think=False
)

#2. Give the agent its tools
tools=[get_weather,
       calendar_tool,
       gmail_tool]

#3.Create the Agent
agent=create_agent(
    model=model,
    tools=tools
)

