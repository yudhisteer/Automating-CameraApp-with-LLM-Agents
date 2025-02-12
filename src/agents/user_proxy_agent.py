from autogen import UserProxyAgent

from ..utils.load_system_message import get_system_message


def create_user_proxy_agent(
    name: str, sys_msg: str, human_input_mode: str = "NEVER", **kwargs
) -> UserProxyAgent:
    try:
        system_message = get_system_message(sys_msg)
    except FileNotFoundError:
        print(f"System message file not found: {sys_msg}")
        return None
    # Create the User Proxy Agent
    return UserProxyAgent(
        name=name,
        human_input_mode=human_input_mode,
        is_termination_msg=lambda msg: msg.get("content") is not None
        and "TERMINATE" in msg["content"],
        system_message=system_message,
        code_execution_config={"work_dir": ".", "use_docker": False},
        **kwargs,
    )
