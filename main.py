from src.utils.config_loader import load_config
from src.tools.tools import *
from src.agents.assistant_agent import create_assistant_agent
from src.agents.user_proxy_agent import create_user_proxy_agent
from src.utils.agent_utils import (
    register_agent_functions,
    interpret_query,
    determine_agents,
    process_sequential_chats,
    run_workflow,
)


filter_dict = {"model": "gpt-4o-mini"}
llm_config = {"config_list": load_config(filter_dict)}

open_camera_agent = create_assistant_agent(
    name="open_camera_agent",
    sys_msg="You can execute the following functions: open_camera",
    llm_config=llm_config,
    function_map={"open_camera": open_camera},
)

close_camera_agent = create_assistant_agent(
    name="close_camera_agent",
    sys_msg="You can execute the following functions: close_camera",
    llm_config=llm_config,
    function_map={"close_camera": close_camera},
)

minimize_camera_agent = create_assistant_agent(
    name="minimize_camera_agent",
    sys_msg="You can execute the following functions: minimize_camera",
    llm_config=llm_config,
    function_map={"minimize_camera": minimize_camera},
)

restore_camera_agent = create_assistant_agent(
    name="restore_camera_agent",
    sys_msg="You can execute the following functions: restore_camera",
    llm_config=llm_config,
    function_map={"restore_camera": restore_camera},
)

set_automatic_framing_agent = create_assistant_agent(
    name="set_automatic_framing_agent",
    sys_msg="You can execute the following functions: set_automatic_framing",
    llm_config=llm_config,
    function_map={"set_automatic_framing": set_automatic_framing},
)

set_blur_type_agent = create_assistant_agent(
    name="set_blur_type_agent",
    sys_msg="You can execute the following functions: set_blur_type",
    llm_config=llm_config,
    function_map={"set_blur_type": set_blur_type},
)

set_background_effects_agent = create_assistant_agent(
    name="set_background_effects_agent",
    sys_msg="You can execute the following functions: set_background_effects",
    llm_config=llm_config,
    function_map={"set_background_effects": set_background_effects},
)

interpreter_agent = create_assistant_agent(
    name="interpreter_agent",
    sys_msg="interpreter_agent_msg.txt",
    llm_config=llm_config,
)

manager_agent = create_assistant_agent(
    name="manager_agent",
    sys_msg="manager_agent_msg.txt",
    llm_config=llm_config,
)


user_proxy_agent = create_user_proxy_agent(
    name="user_proxy_agent",
    sys_msg="Execute the appropriate function based on the user's request.",
    llm_config=llm_config,
    human_input_mode="NEVER",
)


if __name__ == "__main__":

    # Register the functions first
    agent_functions = [
        (open_camera, open_camera_agent, "open_camera", "Open the camera"),
        (close_camera, close_camera_agent, "close_camera", "Close the camera"),
        (minimize_camera, minimize_camera_agent, "minimize_camera", "Minimize the camera"),
        (restore_camera, restore_camera_agent, "restore_camera", "Restore the camera"),
        (set_automatic_framing, set_automatic_framing_agent, "set_automatic_framing", "Set automatic framing to on or off"),
        (set_blur_type, set_blur_type_agent, "set_blur_type", "Set blur type to standard or portrait"),
        (set_background_effects, set_background_effects_agent, "set_background_effects", "Set background effects to on or off"),
    ]
    register_agent_functions(user_proxy_agent, agent_functions)

    # user_proxy_agent.initiate_chat(
    #     open_camera_agent,
    #     message="open the camera",
    #     max_turns=2,
    # )

    # user_proxy_agent.initiate_chat(
    #     set_automatic_framing_agent,
    #     message="set automatic framing to on and off 22 times",
    #     max_turns=2,
    # )

    # user_proxy_agent.initiate_chat(
    #     set_blur_type_agent,
    #     message="set blur type to standard",
    #     max_turns=2,
    # )

    # user_proxy_agent.initiate_chat(
    #     set_background_effects_agent,
    #     message="set background effects to off",
    #     max_turns=2,
    # )

    # user_proxy_agent.initiate_chat(
    #     minimize_camera_agent,
    #     message="minimize camera",
    #     max_turns=2,
    # )

    # user_proxy_agent.initiate_chat(
    #     restore_camera_agent,
    #     message="restore camera",
    #     max_turns=2,
    # )

    # Interpret the query and message type with number of iterations
    query = "minimize and restore camera 2 times"
    msg_type, iterations, interpreted_query = interpret_query(query, interpreter_agent)
    print("msg_type: ", msg_type)
    print("iterations: ", iterations)
    print("interpreted_query: ", interpreted_query)

    # Determine the agents to use
    agent_list = determine_agents(interpreted_query, manager_agent, agent_functions)
    print("agent_list: ", agent_list)

    # Process the query with the agents
    #process_sequential_chats(interpreted_query, agent_list, agent_functions, user_proxy_agent)


    run_workflow(
        query=interpreted_query,
        iterations=iterations,
        agent_list=agent_list,
        agent_functions=agent_functions,
        user_proxy_agent=user_proxy_agent
    )