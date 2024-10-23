from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import create_react_agent

from app.inference.analyzer.tools import toolkit


class СhatModel:
    def __init__(self):
        self.model = ChatOpenAI(model='gpt-4o-mini')
        self.agent_executor = create_react_agent(self.model, toolkit)

    def run(self, messages: list[BaseMessage], stream: bool = False) -> str:
        if stream:
            pass

        response = self.agent_executor.invoke({'messages': messages})
        return response.content
