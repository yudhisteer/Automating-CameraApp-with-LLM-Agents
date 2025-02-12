from autogen import ConversableAgent, register_function
from autogen import AssistantAgent
from typing import Tuple

def register_agent_functions(
    user_proxy_agent: ConversableAgent, agent_functions: list
) -> None:
    """
    Register multiple functions with their respective agents.

    Args:
        user_proxy_agent: The executor agent for all functions
        agent_functions: List of tuples containing (function: function, caller_agent: ConversableAgent, name: str, description: str)
    """
    for func, caller, name, description in agent_functions:
        register_function(
            f=func,
            caller=caller,
            executor=user_proxy_agent,
            name=name,
            description=description,
        )


def interpret_query(
    context: str, interpreter_agent: AssistantAgent
) -> Tuple[str, bool, str]:
    """
    Get a clean, interpreted query from the interpreter agent.
    Returns: (interpreted_query, needs_clarification, clarification_msg)
    """
    messages = [
        {
            "role": "user",
            "content": f"""Given this conversation context, interpret the user's intent into a clear command.
        If clarification is needed, ask for it. If a previous query is referenced, resolve it.

        Context:
        {context}

        Output format:
        NEEDS_CLARIFICATION: [true/false]
        CLARIFICATION_MSG: [your question if clarification needed]
        QUERY: [the interpreted command]""",
        }
    ]

    response = interpreter_agent.generate_reply(messages)
    print("Interpreter response:", response)

    # Parse response
    parsed = {
        key: value.strip()
        for line in response.split("\n")
        if ": " in line
        for key, value in [line.split(":", 1)]
    }

    return (
        parsed.get("QUERY", ""),
        parsed.get("NEEDS_CLARIFICATION", "false").lower() == "true",
        parsed.get("CLARIFICATION_MSG", ""),
    )
