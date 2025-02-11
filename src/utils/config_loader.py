import os

import autogen
from dotenv import load_dotenv


def load_config(filter_dict: dict = None):
    load_dotenv()
    # Load config list from JSON file
    config_list = autogen.config_list_from_json(
        env_or_file="OAI_CONFIG_LIST.json",
        file_location="config",
        filter_dict=filter_dict,
    )
    print(f"Using model: {filter_dict['model']}")

    for config in config_list:
        # Skip if it's ollama (uses direct API key)
        if config.get("api_type") == "ollama":
            continue

        # Get the API key from environment variables
        api_key_name = config["api_key"]
        config["api_key"] = os.getenv(api_key_name)

        if not config["api_key"]:
            raise ValueError(
                f"Missing API key: {api_key_name} not found in environment variables"
            )
    return config_list


if __name__ == "__main__":
    config_list = load_config()
    print(config_list)
