from dotenv import load_dotenv
from typing_extensions import TypedDict
from openai import OpenAI
from typing import Optional,Literal
from langgraph.graph import StateGraph,START,END



load_dotenv()

client = OpenAI()

class State(TypedDict):
    user_query: str
    llm_output: Optional[str]
    is_good: Optional[bool]


def chatbot(state:State):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role":"user" , "content":state.get("user_query")}
        ]
    )   

    state["llm_output"] = response.choices[0].message.content
    return state

def evalaute_response(state:State) -> Literal["chatbot_gemini","endnode"]:
    if True:
        return "endnode"
    
    return "chatbot_gemini" 


def chatbot(state:State):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role":"user" , "content":state.get("user_query")}
        ]
    )   

    state["llm_output"] = response.choices[0].message.content
    return state


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("chatbot_gemini",chatbot_gemini)
graph_builder.add_node("endnode",endnode)