from autogen import ConversableAgent, register_function
from autogen import AssistantAgent, UserProxyAgent
from typing import Tuple
from src.tools.tools import open_camera, close_camera
import gradio as gr


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
    query: str, interpreter_agent: AssistantAgent
) -> Tuple[str, int, str]:
    """
    Interpret a given query into command parameters using the interpreter agent.

    Args:
        query (str): The user's input query to interpret
        interpreter_agent: The LLM agent used for interpretation

    Returns:
        tuple: (msg_type, iterations, query)
    """

    def parse_interpreter_response(response):
        """
        Parse the interpreter's response into its components.
        """
        msg_type = None
        iterations = 1
        query = None

        try:
            lines = response.strip().split("\n")
            for line in lines:
                if not line.strip():
                    continue

                parts = [p.strip() for p in line.split(":", 1)]
                if len(parts) != 2:
                    continue

                key, value = parts

                if key == "TYPE":
                    msg_type = value
                elif key == "ITERATIONS":
                    try:
                        iterations = int(value)
                    except ValueError:
                        iterations = 1
                elif key == "QUERY":
                    query = value

        except Exception as e:
            print(f"Error parsing response: {e}")

        return msg_type, iterations, query

    # Create the messages structure
    messages = [
        {
            "role": "user",
            "content": f"""Given this conversation context, interpret the user's intent into a clear command.
        If clarification is needed, ask for it. If a previous query is referenced, resolve it.
        For sequential actions (like minimize then restore), include both commands in the QUERY separated by 'then'.

        Query:
        {query}

        Output format:
        TYPE: [TASK|CONVERSATION|UNCLEAR]
        ITERATIONS: [Number of times to execute, default 1]
        QUERY: [Final interpreted command(s) with tool and parameters. Use 'then' for sequential actions]""",
        }
    ]

    # Get response from interpreter agent
    response = interpreter_agent.generate_reply(messages)

    # Parse and return the components
    return parse_interpreter_response(response)


# def determine_agents(
#     task: str, decision_agent: ConversableAgent, agent_map: dict
# ) -> Tuple[list, list]:
#     """
#     Determine the sequence of agents needed to complete a task.

#     Args:
#         task: The task to be completed
#         decision_agent: The agent that will determine the sequence
#         agent_map: Dictionary mapping agent names to actual agent objects
#                   (e.g., {"data_fetcher_agent": data_fetcher})

#     Returns:
#         list: A list of agent objects in the order they should be executed
#     """
#     try:
#         message = {
#             "role": "user",
#             "content": f"""Based on this task: '{task}', determine the sequence of agents needed to complete it.
#                 Please respond with a Python list containing the required agents in order.
#                 Use only these options:
#                 {chr(10).join(f'- {agent}' for agent in agent_map.keys())}
                
#                 If no agents are needed or the task is complete, return an empty list."""
#         }

#         response = decision_agent.generate_reply([message])
        
#         try:
#             agent_list = eval(response)
#             if isinstance(agent_list, list):
#                 if all(agent in agent_map for agent in agent_list):
#                     return agent_list
#                 else:
#                     print(f"Invalid agent(s) in list: {agent_list}")
#                     return []
#             else:
#                 print(f"Invalid response format: {response}")
#                 return []
#         except Exception as e:
#             print(f"Error parsing response: {response}")
#             print(f"Error details: {str(e)}")
#             return []

#     except Exception as e:
#         print(f"Error in determine_agents: {str(e)}")
#         return []


def determine_agents(
    task: str, decision_agent: ConversableAgent, agent_map: dict
) -> Tuple[list, list]:
    """
    Determine the sequence of agents needed to complete a task.

    Args:
        task: The task to be completed
        decision_agent: The agent that will determine the sequence
        agent_map: Dictionary mapping agent names to actual agent objects
                  (e.g., {"data_fetcher_agent": data_fetcher})

    Returns:
        Tuple[list, list]: A tuple containing:
            - List of agent names in order they should be executed
            - List of agent names with explicit state parameters
    """
    try:
        message = {
            "role": "user",
            "content": f"""Based on this task: '{task}', determine the sequence of agents needed to complete it.
                Analyze the task according to camera control operation requirements.
                
                Please respond with TWO Python lists:
                1. Sequence: List of agent names in order
                2. State: List of agent names with explicit state parameters
                
                Use only these agents:
                {chr(10).join(f'- {agent}' for agent in agent_map.keys())}
                
                If no agents are needed or the task is complete, return two empty lists."""
        }

        response = decision_agent.generate_reply([message])
        
        try:
            # Extract the two lists from the response
            if "Sequence:" in response and "State:" in response:
                sequence_part = response.split("Sequence:")[1].split("State:")[0].strip()
                state_part = response.split("State:")[1].strip()
                
                agent_sequence = eval(sequence_part)
                agent_states = eval(state_part)
                
                if isinstance(agent_sequence, list) and isinstance(agent_states, list):
                    if all(agent in agent_map for agent in agent_sequence):
                        return agent_sequence, agent_states
                    else:
                        print(f"Invalid agent(s) in list: {agent_sequence}")
                        return [], []
                else:
                    print(f"Invalid response format: {response}")
                    return [], []
            else:
                print(f"Response missing Sequence or State: {response}")
                return [], []
        except Exception as e:
            print(f"Error parsing response: {response}")
            print(f"Error details: {str(e)}")
            return [], []

    except Exception as e:
        print(f"Error in determine_agents: {str(e)}")
        return [], []


def process_sequential_chats(
    query: str,
    agent_sequence: list,
    agent_states: list,
    agent_map: dict,
    user_proxy_agent: UserProxyAgent,
) -> None:
    """
    Process commands through a sequence of agents with clear action context.
    Each agent receives information about what specific action they should take.
    """
    chat_configs = []
    original_command = query

    
    # Build chat configurations for each agent
    for idx, (agent_name, intended_action) in enumerate(zip(agent_sequence, agent_states)):
        step_context = (
            f"Original command: {original_command}\n"
            f"Your role: You are step {idx + 1} in a {len(agent_sequence)}-step sequence.\n"
            f"Your specific task: {intended_action}\n"
            "\nPrevious steps executed:\n"
        )
        
        if idx > 0:
            for step_num, prev_agent in enumerate(agent_sequence[:idx], 1):
                step_context += f"Step {step_num}: Action by {prev_agent}\n"
        else:
            step_context += "No steps executed yet\n"

        chat_configs.append({
            "recipient": agent_map[agent_name],
            "message": step_context,
            "max_turns": 2,
            "summary_method": "reflection_with_llm",
            "summary_prompt": "What specific action did you take in this step?"
        })

    return user_proxy_agent.initiate_chats(chat_configs)




def run_workflow(
    query: str,
    iterations: int,
    agent_sequence: list,
    agent_states: list,
    agent_map: dict,
    user_proxy_agent: UserProxyAgent
) -> None:
    """
    Execute a camera-related task for specified number of iterations with proper camera handling.
    
    Args:
        query: The task query to execute
        iterations: Number of times to repeat the task
        agent_sequence: List of agents to use in sequence
        agent_map: Dictionary mapping agent names to actual agent objects
        user_proxy_agent: UserProxyAgent instance
    """
    try:
        # # First open the camera
        # print("\nOpening camera...")
        # open_camera()
        
        # Execute the task for specified iterations
        for i in range(iterations):
            print(f"\nIteration {i+1}/{iterations}:")
            try:
                process_sequential_chats(query, agent_sequence, agent_states, agent_map, user_proxy_agent)
            except Exception as e:
                print(f"Error in iteration {i+1}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error during task execution: {str(e)}")
    

def process_message(message: str, chat_history, interpreter_agent, manager_agent, agent_map, user_proxy_agent):
    """Process a single message through the workflow and return formatted responses."""
    try:
        # First, show the user's message
        chat_history.append({"role": "user", "content": message})
        
        # Interpret the query
        msg_type, iterations, interpreted_query = interpret_query(message, interpreter_agent)
        interpretation = f"""Query Interpretation:
• Type: {msg_type}
• Iterations: {iterations}
• Interpreted as: {interpreted_query}"""
        chat_history.append({"role": "assistant", "content": interpretation})
        
        # Determine agent sequence
        agent_sequence, agent_states = determine_agents(interpreted_query, manager_agent, agent_map)
        sequence_msg = f"""Agent Sequence:
{', '.join(agent_sequence) if agent_sequence else 'No agents needed'}"""
        chat_history.append({"role": "assistant", "content": sequence_msg})
        
        # Run the workflow if we have agents to execute
        if agent_sequence:
            try:
                run_workflow(
                    query=interpreted_query,
                    iterations=iterations,
                    agent_sequence=agent_sequence,
                    agent_states=agent_states,
                    agent_map=agent_map,
                    user_proxy_agent=user_proxy_agent
                )
                chat_history.append({"role": "assistant", "content": "Task executed successfully!"})
            except Exception as e:
                chat_history.append({"role": "assistant", "content": f"Error executing task: {str(e)}"})
        
        return chat_history
    except Exception as e:
        chat_history.append({"role": "assistant", "content": f"Error processing message: {str(e)}"})
        return chat_history

def create_chat_interface(interpreter_agent, manager_agent, agent_map, user_proxy_agent):
    """Create and configure the Gradio chat interface."""
    with gr.Blocks() as chat_interface:
        chatbot = gr.Chatbot(
            show_label=False,
            height=600,
            bubble_full_width=False,
            type="messages"
        )
        
        with gr.Row():
            msg = gr.Textbox(
                label="Your command",
                placeholder="Type your command here...",
                show_label=True,
                scale=4
            )
            submit = gr.Button("Send", scale=1)
        
        clear = gr.ClearButton([msg, chatbot])

        def respond(message, chat_history):
            if message:
                chat_history = process_message(
                    message,
                    chat_history,
                    interpreter_agent,
                    manager_agent,
                    agent_map,
                    user_proxy_agent
                )
            return "", chat_history

        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        submit.click(respond, [msg, chatbot], [msg, chatbot])

    return chat_interface

def launch_chat(interpreter_agent, manager_agent, agent_map, user_proxy_agent):
    """Launch the chat interface."""
    chat_interface = create_chat_interface(
        interpreter_agent,
        manager_agent,
        agent_map,
        user_proxy_agent
    )
    chat_interface.launch(share=False)