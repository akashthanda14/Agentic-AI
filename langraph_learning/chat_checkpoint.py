"""
LangGraph chatbot with MongoDB-backed checkpoint persistence.

This file demonstrates how to compile the same `StateGraph` with a MongoDB
checkpointer so graph state can be persisted and resumed across invocations.

LangGraph concepts implemented here:
- Typed state schema with message reducer
- Single-node graph from `START` to `END`
- Graph compilation with and without checkpointer
- Streaming execution with per-step state values

Checkpointing concepts implemented here:
- `MongoDBSaver` lifecycle management
- Thread-scoped execution via `configurable.thread_id`
- Automatic checkpoint writes during graph execution

Relationship to other files:
- Builds on the base no-checkpoint flow from `chat.py`.
- Shares the same teaching-oriented graph structure as the other examples.
"""

from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph , START , END
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver


# ARCHITECTURE: Dotenv loading is performed at import time so credentials are
# available to both the LLM client and MongoDB checkpointer setup.
load_dotenv()

# ARCHITECTURE: Reusing one initialized chat model keeps node execution simple
# and prevents repeated client setup overhead.
llm = init_chat_model(
    model="gpt-4.1-mini",
    model_provider="openai"
)

class State(TypedDict):
    # LANGGRAPH: `messages` is declared as a reducer-managed channel.
    # LANGGRAPH: `add_messages` instructs LangGraph to append/merge message
    # deltas returned by nodes rather than replacing the full list.
    messages: Annotated[list , add_messages]

    
def chatbot(state:State):
    """Generate one assistant message using the conversation state.

    Why this exists:
    - It is the core node that transforms input messages into model output.

    State contract:
    - Receives: `state["messages"]` containing prior messages.
    - Returns: `{"messages": [response]}` as a partial state update.

    LangGraph pattern:
    - Node-as-pure-transform style: read state, return delta, let reducers merge.
    """
    # LANGGRAPH: `invoke` calls the provider-specific model under LangChain's
    # unified interface; this keeps node logic provider-agnostic.
    response = llm.invoke(state.get("messages"))
    # LANGGRAPH: Returning a message delta enables deterministic state merge and
    # is checkpoint-friendly because transitions are explicit.
    return {"messages":[response]}    
  



graph_builder = StateGraph(State)

# LANGGRAPH: Register graph node callable under symbolic route name.
graph_builder.add_node("chatbot",chatbot)

# LANGGRAPH: Define linear execution path from entry to node to terminal state.
graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot",END)

# LANGGRAPH: Base compile without persistence. Useful for local smoke tests.
graph = graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):
    """Compile graph with a pluggable checkpoint backend.

    Why this exists:
    - Separates graph topology definition from runtime persistence strategy.

    State/checkpoint contract:
    - Input: checkpointer implementation (here `MongoDBSaver`).
    - Output: executable compiled graph that persists run state transitions.
    """
    # LANGGRAPH: Passing `checkpointer` wires persistence into runtime so state
    # snapshots can be stored/retrieved by thread ID across calls.
    return graph_builder.compile(checkpointer=checkpointer)
    
DB_URI = "mongodb://admin:admin@localhost:27017" 
with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:

    # CHECKPOINT: Context manager owns MongoDB connection lifecycle and ensures
    # clean open/close semantics around graph execution.

    graph_with_checkpoint = compile_graph_with_checkpointer(checkpointer=checkpointer)

    config = {
        "configurable": {
            # CHECKPOINT: `thread_id` is the conversation/session key used by
            # LangGraph checkpointers to isolate and retrieve run history.
            "thread_id": "Akash" #userid
        }
    }

    for chunk in graph_with_checkpoint.stream(
        # LANGGRAPH: Input state enters at `START` for this invocation.
        State({"messages": ["Hi , what is my name"]}),
        config,
        # LANGGRAPH: `stream_mode="values"` yields evolving state snapshots
        # after each node transition instead of only final output.
        stream_mode="values"
        ):
            # CHECKPOINT: During streamed execution, LangGraph persists state
            # transitions through the configured checkpointer by thread ID.
            chunk["messages"][-1].pretty_print()
            
    # ARCHITECTURE: This print references `updated_state`, which is not defined
    # in this script. Left unchanged to preserve existing functional code.
    print("\n\nupdated_state",updated_state)

#(START) -> chatbot -> samplenode -> (END)