"""
Simple linear LangGraph demo without checkpointing.

This file demonstrates the smallest end-to-end LangGraph pipeline in this project:
an input `State` enters at `START`, is processed by a chatbot node, then passes
through a second sample node, and exits at `END`.

LangGraph concepts implemented here:
- `StateGraph` construction with a typed state schema
- Node registration and sequential edge routing
- Graph compilation and synchronous invocation
- Message reducer usage via `add_messages`

Relationship to other files:
- `chat_checkpoint.py` extends this pattern by adding MongoDB checkpointing.
- `chat2.py` experiments with conditional routing patterns.
"""

from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph , START , END
from langchain.chat_models import init_chat_model

# ARCHITECTURE: Environment variables are loaded once at module import time so
# model/client setup can rely on API keys in local development.
load_dotenv()

# ARCHITECTURE: A single shared model instance avoids re-initializing the LLM
# for every node call and reflects common LangGraph node design.
llm = init_chat_model(
    model="gpt-4.1-mini",
    model_provider="openai"
)

class State(TypedDict):
    # LANGGRAPH: `messages` is the canonical conversational state field.
    # LANGGRAPH: `add_messages` is a reducer that tells LangGraph how to merge
    # message updates returned by nodes into the running state.
    messages: Annotated[list , add_messages]

    
def chatbot(state:State):
    """Generate an assistant response from accumulated conversation state.

    Why this exists:
    - This node is the primary reasoning/generation step in the graph.

    State contract:
    - Receives: `state["messages"]` containing prior conversation turns.
    - Returns: partial state update with a new model response under
      `{"messages": [response]}` for reducer-based merge.
    """
    # LANGGRAPH: Nodes receive the current graph state snapshot and return a
    # partial update; LangGraph merges that update according to schema rules.
    response = llm.invoke(state.get("messages"))
    # LANGGRAPH: Returning only the delta keeps nodes composable and avoids
    # accidental overwrites of unrelated state fields.
    return {"messages":[response]}    

def Samplenode(state:State):
    """Illustrate a second node that appends another message to state.

    Why this exists:
    - It demonstrates that multiple nodes can sequentially mutate the same
      `messages` state channel.

    State contract:
    - Receives: full state after `chatbot` executes.
    - Returns: a message update merged into `messages` by `add_messages`.
    """
    print("\n\nInside Sample Node node",state)
    # LANGGRAPH: This node returns a plain string message; the reducer handles
    # integration into the message history for downstream visibility.
    return {"messages":["Hi , This is a message from Chatbot Node"
    ""]}    




graph_builder = StateGraph(State)

# LANGGRAPH: Registering nodes maps symbolic node names to callable handlers.
graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("Samplenode",Samplenode)

# LANGGRAPH: `START` and `END` are sentinel vertices representing entry/exit.
# LANGGRAPH: These edges form a deterministic linear flow.
graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot","Samplenode")
graph_builder.add_edge("Samplenode" , END)

# LANGGRAPH: `compile()` validates topology and produces an executable graph.
graph = graph_builder.compile()

# LANGGRAPH: `invoke()` runs the full graph synchronously and returns final
# merged state after all node transitions complete.
updated_state = graph.invoke(State({"messages":["Hi , My name is Akashdeep Thanda"]}))
print("\n\nupdated_state",updated_state)

#(START) -> chatbot -> samplenode -> (END)