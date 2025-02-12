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


def interpret_context(context: str, interpreter_agent: AssistantAgent) -> Tuple[str, int, str]:
    """
    Interpret a given context into command parameters using the interpreter agent.
    
    Args:
        context (str): The user's input context to interpret
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
            lines = response.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                    
                parts = [p.strip() for p in line.split(':', 1)]
                if len(parts) != 2:
                    continue
                    
                key, value = parts
                
                if key == 'TYPE':
                    msg_type = value
                elif key == 'ITERATIONS':
                    try:
                        iterations = int(value)
                    except ValueError:
                        iterations = 1
                elif key == 'QUERY':
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

        Context:
        {context}

        Output format:
        TYPE: [TASK|CONVERSATION|UNCLEAR]
        ITERATIONS: [Number of times to execute, default 1]
        QUERY: [Final interpreted command with tool and parameters]""",
        }
    ]

    # Get response from interpreter agent
    response = interpreter_agent.generate_reply(messages)
    
    # Parse and return the components
    return parse_interpreter_response(response)



