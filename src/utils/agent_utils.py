from autogen import ConversableAgent, register_function
from autogen import AssistantAgent, UserProxyAgent
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


def determine_agents(
    task: str, decision_agent: ConversableAgent, agent_functions: list
) -> list:
    """
    Determine the sequence of agents needed to complete a task.

    Args:
        task: The task to be completed
        decision_agent: The agent that will determine the sequence
        agent_functions: List of tuples (function, agent, name, description)

    Returns:
        list: A list of agents in the order they should be executed
    """
    try:
        # Create a clean list of available agents with their descriptions
        available_agents = [
            f"- {func_tuple[2]}: {func_tuple[3]}" for func_tuple in agent_functions
        ]

        # Create messages for the decision agent
        messages = [
            {
                "role": "user",
                "content": f"""Analyze this task and determine which agents are needed to complete it.
                Task: '{task}'
                
                Available agents:
                {chr(10).join(available_agents)}
                
                Respond with a Python list containing only the required agent names in order.
                If no agents are needed or the task is complete, return an empty list: []""",
            }
        ]

        # Get response from decision agent using generate_reply
        response = decision_agent.generate_reply(messages)

        # Parse the response
        try:
            agent_list = eval(response)
            if isinstance(agent_list, list):
                # Create a map of agent names to agents for validation
                agent_map = {
                    func_tuple[2]: func_tuple[1] for func_tuple in agent_functions
                }

                # Validate all agents exist in agent_functions
                if all(agent in agent_map for agent in agent_list):
                    # Return the actual agent objects in the specified order
                    return agent_list
                else:
                    print(f"Invalid agent(s) in list: {agent_list}")
                    return []
            else:
                print(f"Invalid response format: {response}")
                return []
        except Exception as e:
            print(f"Error parsing response: {response}")
            print(f"Error details: {str(e)}")
            return []

    except Exception as e:
        print(f"Error in determine_agents: {str(e)}")
        return []

def process_sequential_chats(
    query: str, 
    agent_sequence: list, 
    agent_functions: list, 
    user_proxy_agent: UserProxyAgent
) -> None:
    """
    Process a sequence of chats between agents, passing results from one to the next.
    
    Args:
        query: Initial message/task to process
        agent_sequence: List of agent names to process the message sequentially
        agent_functions: List of tuples (function, agent, name, description)
        user_proxy_agent: UserProxyAgent instance
        
    Returns:
        str: Final result after processing through all agents
    """
    # Create a mapping of agent names to their actual agent objects
    agent_map = {func_tuple[2]: func_tuple[1] for func_tuple in agent_functions}
    
    current_message = query
    for agent_name in agent_sequence:
        # Get the corresponding agent object
        recipient = agent_map[agent_name]
        
        # Initiate chat with current agent
        user_proxy_agent.initiate_chat(
            recipient=recipient, 
            message=current_message, 
            max_turns=2, 
            silent=True
        )
        
        # Get the chat messages and extract the final result
        chat_messages = user_proxy_agent.chat_messages[recipient]
        current_message = next(
            (
                msg["content"]
                for msg in reversed(chat_messages)
                if msg["content"] is not None
            ),
            None,
        )
        
        # Print formatted message with clear separation
        print("\n" + "=" * 50)
        print(f"Response from {agent_name}:")
        print("-" * 50)
        print(current_message)
        print("=" * 50 + "\n")
        
        if current_message is None:
            raise ValueError(f"Failed to get response from {agent_name}")