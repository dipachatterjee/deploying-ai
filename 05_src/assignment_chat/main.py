from openai import OpenAI
from dotenv import load_dotenv
import json
import requests
from utils.logger import get_logger
import os

from langgraph.graph import StateGraph, MessagesState, START
from langchain.chat_models import init_chat_model
from langgraph.prebuilt.tool_node import ToolNode, tools_condition
from langchain_core.messages import SystemMessage,  HumanMessage, AIMessage

from assignment_chat.prompts import return_instructions
from assignment_chat.tools_weather import get_weather
from assignment_chat.tools_bird import get_bird_facts
from assignment_chat.tools_history import get_history_facts

_logs = get_logger(__name__)

load_dotenv(".env")
load_dotenv(".secrets")


client = OpenAI(default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')},
    base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1')
open_ai_model = os.getenv("OPENAI_MODEL", "gpt-4")

tools = [get_weather, get_bird_facts, get_history_facts]
instructions = return_instructions()


#def call_model(state: MessagesState):
#    """LLM decides whether to call a tool or not"""
#    response = client.bind_tools(tools).invoke([SystemMessage(content=instructions)] + state["messages"])
#    return {
#        "messages": [response]
#    }

def call_model(state: MessagesState):
    messages_payload = [
        {"role": "system", "content": instructions}
    ] + [
        {"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": m.content}
        for m in state["messages"]
    ]

    resp = client.chat.completions.create(
        model=open_ai_model,
        messages=messages_payload
    )

    # Extract content from response
    content = resp.choices[0].message.content

    return {
        "messages": [AIMessage(content=content)]
    }


def get_graph():
    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    builder.add_node(ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        tools_condition,
    )
    builder.add_edge("tools", "call_model")
    graph = builder.compile()
    return graph