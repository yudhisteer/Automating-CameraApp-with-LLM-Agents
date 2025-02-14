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
    launch_chat,
)
import json

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
    sys_msg="set_automatic_framing_agent_msg.txt",
    llm_config=llm_config,
    function_map={"set_automatic_framing": set_automatic_framing},
)

set_blur_type_agent = create_assistant_agent(
    name="set_blur_type_agent",
    sys_msg="set_blur_type_agent_msg.txt",
    llm_config=llm_config,
    function_map={"set_blur_type": set_blur_type},
)

set_background_effects_agent = create_assistant_agent(
    name="set_background_effects_agent",
    sys_msg="set_background_effects_agent_msg.txt",
    llm_config=llm_config,
    function_map={"set_background_effects": set_background_effects},
)

switch_camera_agent = create_assistant_agent(
    name="switch_camera_agent",
    sys_msg="switch_camera_agent_msg.txt",
    llm_config=llm_config,
    function_map={"switch_camera": switch_camera},
)

camera_mode_agent = create_assistant_agent(
    name="camera_mode_agent",
    sys_msg="You can execute the following functions: camera_mode. You can switch between 'photo' and 'video' mode.",
    llm_config=llm_config,
    function_map={"camera_mode": camera_mode},
)

take_photo_agent = create_assistant_agent(
    name="take_photo_agent",
    sys_msg="take_photo_agent_msg.txt",
    llm_config=llm_config,
    function_map={"take_photo": take_photo},
)

take_video_agent = create_assistant_agent(
    name="take_video_agent",
    sys_msg="take_video_agent_msg.txt",
    llm_config=llm_config,
    function_map={"take_video": take_video},
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
    sys_msg="user_proxy_agent_msg.txt",
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
        (switch_camera, switch_camera_agent, "switch_camera", "Switch between cameras"),
        (camera_mode, camera_mode_agent, "camera_mode", "Switch between photo and video mode"),
        (take_photo, take_photo_agent, "take_photo", "Take a photo"),
        (take_video, take_video_agent, "take_video", "Take a video"),
    ]
    register_agent_functions(user_proxy_agent, agent_functions)

    # agents map
    agent_map = {
        "open_camera_agent": open_camera_agent,
        "close_camera_agent": close_camera_agent,
        "minimize_camera_agent": minimize_camera_agent,
        "restore_camera_agent": restore_camera_agent,
        "set_automatic_framing_agent": set_automatic_framing_agent,
        "set_blur_type_agent": set_blur_type_agent,
        "set_background_effects_agent": set_background_effects_agent,
        "switch_camera_agent": switch_camera_agent,
        "camera_mode_agent": camera_mode_agent,
        "take_photo_agent": take_photo_agent,
        "take_video_agent": take_video_agent,
    }

    # Load the test cases
    with open('cases/test_cases.json', 'r') as f:
        test_data = json.load(f)

    # Access a specific test case by ID
    test_id = "2"
    query = test_data['testCases'][test_id]
    print(f"Running test: {query['description']}")

    # Update a test result by ID
    test_data['testCases'][test_id]['result'] = "N/A"

    # Save the updated results
    with open('cases/test_cases.json', 'w') as f:
        json.dump(test_data, f, indent=2)

    # query = input("Enter a query: ")
    msg_type, iterations, interpreted_query = interpret_query(query, interpreter_agent)
    print("msg_type: ", msg_type)
    print("iterations: ", iterations)
    print("interpreted_query: ", interpreted_query)

    # Determine the agents to use
    agent_sequence = determine_agents(interpreted_query, manager_agent, agent_map)
    print("agent_sequence: ", agent_sequence)

    # open_camera()
    # process_sequential_chats(interpreted_query, agent_sequence, agent_map, user_proxy_agent)

    # Run the workflow
    run_workflow(
        query=interpreted_query,
        iterations=iterations,
        agent_sequence=agent_sequence,
        agent_map=agent_map,
        user_proxy_agent=user_proxy_agent
    )

    # launch_chat(interpreter_agent, manager_agent, agent_map, user_proxy_agent)