import os
from dotenv import load_dotenv
import gradio as gr
from autogen import ConversableAgent

# Load environment variables
load_dotenv()

# Configure the language model
llm_config = {
    "config_list": [
        {
            "model": "gpt-4o-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "api_type": "openai",
        }
    ]
}

# Create the AI friend agent
ai_friend_agent = ConversableAgent(
    name="Hazel",
    system_message="You are an AI friend chatbot",
    llm_config=llm_config,
    code_execution_config=False,
    human_input_mode="NEVER",
)

def chatbot_response(user_input, chat_history):
    """Handle chat interaction and update the UI."""
    if user_input:
        # Add user message to chat history
        chat_history.append((user_input, None))
        
        # Get response from the chatbot
        reply = ai_friend_agent.generate_reply(
            messages=[{"content": user_input, "role": "user"}]
        )
        
        # Add bot's reply to chat history
        chat_history[-1] = (user_input, reply)
        
    return chat_history, ""

# Create Gradio interface
with gr.Blocks() as chat_interface:
    chatbot = gr.Chatbot(
        label="Chat with Hazel",
        height="80vh",
        bubble_full_width=False,
        show_label=True
    )
    msg = gr.Textbox(
        label="Your message",
        placeholder="Type your message here...",
        show_label=True
    )
    clear = gr.ClearButton([msg, chatbot])

    msg.submit(chatbot_response, [msg, chatbot], [chatbot, msg])

if __name__ == "__main__":
    chat_interface.launch()