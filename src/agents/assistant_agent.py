from autogen import AssistantAgent

from ..utils.load_system_message import get_system_message


def create_assistant_agent(
    name: str, sys_msg: str, llm_config: dict = None, **kwargs
) -> AssistantAgent:
    try:
        system_message = get_system_message(sys_msg)
    except FileNotFoundError:
        print(f"System message file not found: {sys_msg}")
        return None
    # Create the Result Analyzer Agent
    return AssistantAgent(
        name=name,
        is_termination_msg=lambda msg: msg.get("content") is not None
        and "TERMINATE" in msg["content"],
        system_message=system_message,
        llm_config=llm_config,
        **kwargs,
    )