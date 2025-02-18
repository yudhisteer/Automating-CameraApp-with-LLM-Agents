import os
import sys
from pathlib import Path


def get_system_message(sys_msg: str, log_dir: Path = None) -> str:
    # If sys_msg doesn't end with .txt, treat it as a direct message
    if not sys_msg.endswith(".txt"):
        message = sys_msg
    else:
        # Get the working directory and find system_messages folder
        working_dir = Path.cwd()
        filepath = working_dir / "system_messages" / sys_msg
        try:
            if not (working_dir / "system_messages").exists():
                raise FileNotFoundError(
                    "system_messages directory not found in working directory"
                )
            if not filepath.exists():
                raise FileNotFoundError(f"System message file '{sys_msg}' not found")

            with open(filepath, "r") as f:
                message = f.read()
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            return f"Error loading system message: {e}"

    if log_dir is not None:
        # Replace the placeholder with the actual log_dir
        message = message.format(log_dir=log_dir)

    return message
