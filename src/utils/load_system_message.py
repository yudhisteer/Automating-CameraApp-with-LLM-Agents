import os
from pathlib import Path


def get_system_message(sys_msg: str, log_dir: Path = None) -> str:
    # If sys_msg doesn't end with .txt, treat it as a direct message
    if not sys_msg.endswith(".txt"):
        message = sys_msg
    else:
        filepath = os.path.join(
            os.path.dirname(__file__), "..", "..", "system_messages", sys_msg
        )
        with open(filepath, "r") as f:
            message = f.read()

    if log_dir is not None:
        # Replace the placeholder with the actual log_dir
        message = message.format(log_dir=log_dir)

    return message