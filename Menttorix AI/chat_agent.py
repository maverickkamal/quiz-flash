import os
from dotenv import load_dotenv
from math_tool import solve_equation, solve_system, factor, expand, differentiate, limit, series
from diagram import generate_svg_diagram
from sandbox import execute_safe_code
from math_tool import matrix_multiply, determinant, eigenvalues
from math_tool import kinematics, projectile_motion, simple_harmonic_motion
from math_tool import beam_deflection, fluid_flow
from typing import Annotated, Literal, Optional, Callable
from typing_extensions import TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig, RunnableLambda

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import AnyMessage, add_messages

import uuid
from datetime import datetime 



load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Menttorix AI"




def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: str

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}

from datetime import datetime

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")


assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a cool study buddy called Menttorix, and your aim is to help students learn." 
            "Use the provided tools to solve any kind of mathematics, some physics and engineering questions,"
            " and other information to assist the student's queries."

            "When searching, be persistent. Expand your query bounds if the first search returns no results." 
            "If a search comes up empty, expand your search before giving up."

            "For mathematical problems or diagram requests:"
            "1. Always check if an available tool can solve the problem or create the diagram, even if you know the answer directly."
            "2. If a tool is available, use it to solve the problem or create the diagram."
            "3. If an error occurs while using the tool, retry the operation."
            "4. If the error persists after retrying, solve the problem or create the diagram using your own knowledge and capabilities."
            "5. If no suitable tool is available, proceed to solve the problem or create the diagram using your available knowledge."

            "Continuously learn from errors encountered while using tools." 
            "Analyze these errors to understand their causes and how to fix them in future interactions." 
            "Apply this learning to improve your problem-solving approach and tool usage."

            "Current time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

part_3_safe_tools = [
    TavilySearchResults(max_results=5),
    generate_svg_diagram, 
    execute_safe_code,
    solve_equation, 
    solve_system, 
    factor, 
    expand,
    differentiate, limit, series,
    matrix_multiply, determinant, eigenvalues,
    kinematics, projectile_motion, simple_harmonic_motion,
    beam_deflection, fluid_flow,
]

part_3_sensitive_tools = [
    execute_safe_code,
]
sensitive_tool_names = {t.name for t in part_3_sensitive_tools}
# Our LLM doesn't have to know which nodes it has to route to. In its 'mind', it's just invoking functions.
part_3_assistant_runnable = assistant_prompt | llm.bind_tools(
    part_3_safe_tools + part_3_sensitive_tools
)

builder = StateGraph(State)


builder.add_edge(START, "assistant")
builder.add_node("assistant", Assistant(part_3_assistant_runnable))
builder.add_node("safe_tools", create_tool_node_with_fallback(part_3_safe_tools))
builder.add_node(
    "sensitive_tools", create_tool_node_with_fallback(part_3_sensitive_tools)
)
# Define logic


def route_tools(state: State) -> Literal["safe_tools", "sensitive_tools", "__end__"]:
    next_node = tools_condition(state)
    # If no tools are invoked, return to the user
    if next_node == END:
        return END
    ai_message = state["messages"][-1]
    # This assumes single tool calls. To handle parallel tool calling, you'd want to
    # use an ANY condition
    first_tool_call = ai_message.tool_calls[0]
    if first_tool_call["name"] in sensitive_tool_names:
        return "sensitive_tools"
    return "safe_tools"


builder.add_conditional_edges(
    "assistant",
    route_tools,
)
builder.add_edge("safe_tools", "assistant")
builder.add_edge("sensitive_tools", "assistant")

memory = MemorySaver()
part_3_graph = builder.compile(
    checkpointer=memory,
    # NEW: The graph will always halt before executing the "tools" node.
    # The user can approve or reject (or even alter the request) before
    # the assistant continues
    interrupt_before=["sensitive_tools"],
)

thread_id = str(uuid.uuid4())

config = {
    "configurable": {
        # The user_id is used in our deck, quiz, and flashcards tools to
        # access a user in a db the user's information
        "user_id": "gfHzDK63OERX26TX7IzqkZ8ofjx2",
        # Checkpoints are accessed by thread_id
        "thread_id": thread_id,
    }
}


_printed = set()
# We can reuse the tutorial questions from part 1 to see how it does.
# for question in tutorial_questions:

if __name__ == "__main__":

    while True:
        question = input("User: ")
        if question.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        events = part_3_graph.stream(
            {"messages": ("user", question)}, config, stream_mode="values"
        )
        for event in events:
            _print_event(event, _printed)
        snapshot = part_3_graph.get_state(config)
        while snapshot.next:
            # We have an interrupt! The agent is trying to use a tool, and the user can approve or deny it
            # Note: This code is all outside of your graph. Typically, you would stream the output to a UI.
            # Then, you would have the frontend trigger a new run via an API call when the user has provided input.
            user_input = input(
                "Do you approve of the above actions? Type 'y' to continue;"
                " otherwise, explain your requested changed.\n\n"
            )
            if user_input.strip() == "y":
                # Just continue
                result = part_3_graph.invoke(
                    None,
                    config,
                )
            else:
                # Satisfy the tool invocation by
                # providing instructions on the requested changes / change of mind
                result = part_3_graph.invoke(
                    {
                        "messages": [
                            ToolMessage(
                                tool_call_id=event["messages"][-1].tool_calls[0]["id"],
                                content=f"API call denied by user. Reasoning: '{user_input}'. Continue assisting, accounting for the user's input.",
                            )
                        ]
                    },
                    config,
                )
            snapshot = part_3_graph.get_state(config)

