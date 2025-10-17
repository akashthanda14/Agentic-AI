from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph , START , END
from langchain.chat_models import init_chat_model

load_dotenv()

llm = init_chat_model(
    model="gpt-4.1-mini",
    model_provider="openai"
)

class State(TypedDict):
    messages: Annotated[list , add_messages]

    
def chatbot(state:State):
    response = llm.invoke(state.get("messages"))
    return {"messages":[response]}    

def Samplenode(state:State):
    print("\n\nInside Sample Node node",state)
    return {"messages":["Hi , This is a message from Chatbot Node"
    ""]}    




graph_builder = StateGraph(State)

graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("Samplenode",Samplenode)

graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot","Samplenode")
graph_builder.add_edge("Samplenode" , END)

graph = graph_builder.compile()

updated_state = graph.invoke(State({"messages":["Hi , My name is Akashdeep Thanda"]}))
print("\n\nupdated_state",updated_state)

#(START) -> chatbot -> samplenode -> (END)