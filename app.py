import argparse
import json

from src.agents.assistant_agent import create_assistant_agent
from src.agents.user_proxy_agent import create_user_proxy_agent
from src.tools.tools import *
from src.utils.agent_utils import (
    determine_agents,
    interpret_query,
    launch_chat,
    process_sequential_chats,
    register_agent_functions,
    run_workflow,
)
from src.utils.config_loader import load_config

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

    """
    Camera Control Application

    A CLI tool for running camera control tests and commands through an agent-based system.

    Usage:
        python camera_control.py [OPTIONS]

    Options:
        --test_id ID           Run a specific test case by ID from test_cases.json
        --query TEXT           Run a custom query (e.g., "Open camera and take photo")
        --interactive          Launch interactive chat mode with the agent system
        --list_tests           Display all available test cases with their IDs and descriptions
        --save_results         Save test results to the test_cases.json file
        --force_status STATUS  Force a specific test result status ("Pass" or "Fail")

    Examples:
        # List all available test cases
        python app.py --list_tests

        # Run a specific test case
        python app.py --test_id 3

        # Run a test case and save results (auto-determine pass/fail)
        python app.py --test_id 3 --save_results

        # Run a test case and force it to be marked as passed
        python app.py --test_id 3 --save_results --force_status Pass

        # Run a test case and force it to be marked as failed
        python app.py --test_id 3 --save_results --force_status Fail

        # Run a custom query without saving results
        python app.py --query "Open the camera and set blur to portrait"

        # Launch interactive mode
        python app.py --interactive

    Notes:
        - If no options are provided, interactive mode is launched by default
        - Test cases are loaded from cases/test_cases.json
        - When saving results without --force_status:
        1. If the test case has an 'expected_result' field, pass/fail is determined automatically
        2. If no 'expected_result' exists, you'll be prompted to manually confirm if the test passed
    """
    # args parser
    parser = argparse.ArgumentParser(description="Camera Control Application")

    # Add arguments
    parser.add_argument("--test_id", type=str, help="Test case ID to run")
    parser.add_argument("--query", type=str, help="Custom query to run")
    parser.add_argument(
        "--interactive", action="store_true", help="Launch interactive chat mode"
    )
    parser.add_argument(
        "--list_tests", action="store_true", help="List available test cases"
    )
    parser.add_argument(
        "--save_results", action="store_true", help="Save test results to file"
    )
    parser.add_argument(
        "--force_status",
        choices=["Pass", "Fail"],
        help="Force a specific pass/fail status",
    )

    # Parse arguments
    args = parser.parse_args()

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

    # Load test cases if needed
    test_data = None
    if args.test_id or args.list_tests:
        try:
            with open("cases/test_cases.json", "r") as f:
                test_data = json.load(f)
        except FileNotFoundError:
            print("Error: Test cases file not found.")
            exit(1)

    # List test cases and exit if requested
    if args.list_tests and test_data:
        print("Available test cases:")
        for id, test in test_data["testCases"].items():
            print(f"ID: {id} - {test.get('description', 'No description')}")
        exit(0)

    # Determine the query to run
    query = None
    if args.test_id and test_data:
        if args.test_id in test_data["testCases"]:
            test_case = test_data["testCases"][args.test_id]
            query = test_case["query"] if "query" in test_case else test_case
            print(f"Running test: {test_case.get('description', 'No description')}")
        else:
            print(f"Error: Test ID {args.test_id} not found.")
            exit(1)
    elif args.query:
        query = args.query
        print(f"Running custom query: {query}")

    # Execute the query if we have one
    if query and not args.interactive:
        msg_type, iterations, interpreted_query = interpret_query(
            query, interpreter_agent
        )
        print("msg_type: ", msg_type)
        print("iterations: ", iterations)
        print("interpreted_query: ", interpreted_query)

        # Determine the agents to use
        agent_sequence, agent_states = determine_agents(
            interpreted_query, manager_agent, agent_map
        )
        print("agent_sequence: ", agent_sequence)
        print("agent_states: ", agent_states)

        # Run the workflow
        result = run_workflow(
            query=interpreted_query,
            iterations=iterations,
            agent_sequence=agent_sequence,
            agent_states=agent_states,
            agent_map=agent_map,
            user_proxy_agent=user_proxy_agent,
        )

        # Determine if test passed based on expected results or user override
        if args.force_status:
            test_status = args.force_status
        else:
            test_status = "Pass"
            if args.test_id and test_data:
                expected_result = test_data["testCases"][args.test_id].get(
                    "expected_result"
                )
                if expected_result:
                    # Compare actual result with expected result
                    # This logic can be customized based on your specific requirements
                    if expected_result != result:
                        test_status = "Fail"
                else:
                    # If no expected result is defined, ask user for manual verification
                    print(f"\nTest result: {result}")
                    user_input = input("Did the test pass? (y/n): ").strip().lower()
                    test_status = "Pass" if user_input.startswith("y") else "Fail"

        # Save results if requested
        if args.save_results and args.test_id and test_data:
            test_data["testCases"][args.test_id]["result"] = result
            test_data["testCases"][args.test_id]["status"] = test_status
            with open("cases/test_cases.json", "w") as f:
                json.dump(test_data, f, indent=2)
            print(f"Results saved for test ID {args.test_id}: {test_status}")

    # Launch interactive mode if requested or if no other action was specified
    if args.interactive or (not query and not args.list_tests):
        print("Starting interactive chat mode...")
        launch_chat(interpreter_agent, manager_agent, agent_map, user_proxy_agent)
