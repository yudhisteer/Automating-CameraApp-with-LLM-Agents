from src.utils.config_loader import load_config
from src.tools.tools import *
from src.agents.assistant_agent import create_assistant_agent
from src.agents.user_proxy_agent import create_user_proxy_agent
from src.utils.agent_utils import register_agent_functions

filter_dict = {"model": "gpt-4o-mini"}
llm_config = {"config_list": load_config(filter_dict)}

open_camera_agent = create_assistant_agent(
    name="open_camera_agent",
    sys_msg="You can execute the following functions: open_camera",
    llm_config=llm_config,
    function_map={"open_camera": open_camera},
)

user_proxy_agent = create_user_proxy_agent(
    name="user_proxy_agent",
    sys_msg="You can execute the following functions: open_camera",
    llm_config=llm_config,
    human_input_mode="NEVER",
)


if __name__ == "__main__":

    # Register the functions first
    agent_functions = [
        (open_camera, open_camera_agent, "open_camera", "Open the camera"),
    ]
    register_agent_functions(user_proxy_agent, agent_functions)

    user_proxy_agent.initiate_chat(
        open_camera_agent,
        message="Open the camera",
        max_turns=2,
    )
