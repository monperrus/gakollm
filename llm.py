#!/bin/env python

import atexit
import click
import datetime
import os
import requests
import sys
import yaml
import json
import re

from pathlib import Path
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.markdown import Markdown

WORKDIR = Path(__file__).parent
CONFIG_FILE = Path(WORKDIR, "config.yaml")
HISTORY_FILE = Path(WORKDIR, ".history")
BASE_ENDPOINT = "https://api.openai.com/v1"
ENV_VAR = "OPENAI_API_KEY"
SAVE_FOLDER = "session-history"
# contains the model name
SAVE_FILE = "llm-session-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".json"

# https://openai.com/api/pricing/
PRICING_RATE = {
    "gpt-3.5-turbo-0125": {"prompt": 0.5/1e6, "completion": 1.5/1e6},
    "gpt-3.5-turbo-instruct": {"prompt": 1.5/1e6, "completion": 2/1e6},
    "gpt-4": {"prompt": 30/1e6, "completion": 60/1e6},
    "gpt-4-turbo": {"prompt": 10/1e6, "completion": 15/1e6},
    "gpt-4-32k": {"prompt": 60/1e6, "completion": 120/1e6},
    "gpt-4o": {"prompt": 5/1e6, "completion": 15/1e6},
}


# Initialize the messages history list
# It's mandatory to pass it at each API call in order to have a conversation
messages = []
# Initialize the token counters
prompt_tokens = 0
completion_tokens = 0
# Initialize the console
console = Console()


def load_config(config_file: str) -> dict:
    """
    Read a YAML config file and returns it's content as a dictionary
    """
    with open(config_file) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    # Optional parameter
    # note max_tokens are for output tokens, not for input tokens
    if "max_tokens" not in config:
        config["max_tokens"] = 100 # default, otherwise see config.yaml

    return config


def create_save_folder() -> None:
    """
    Create the session history folder if not exists
    """
    if not os.path.exists(SAVE_FOLDER):
        os.mkdir(SAVE_FOLDER)


def add_markdown_system_message() -> None:
    """
    Try to force ChatGPT to always respond with well formatted code blocks if markdown is enabled.
    """
    instruction = "Always use code blocks with the appropriate language tags"
    messages.append({"role": "system", "content": instruction})


def calculate_expense(
    prompt_tokens: int,
    completion_tokens: int,
    prompt_pricing: float,
    completion_pricing: float,
) -> float:
    """
    Calculate the expense, given the number of tokens and the pricing rates
    """
    expense = ((prompt_tokens) * prompt_pricing) + (
        (completion_tokens) * completion_pricing
    )
    return round(expense, 6)


def display_expense(model: str) -> None:
    """
    Given the model used, display total tokens used and estimated expense
    """
    total_expense = calculate_expense(
        prompt_tokens,
        completion_tokens,
        PRICING_RATE[model]["prompt"],
        PRICING_RATE[model]["completion"],
    )
    console.print(
        f"\nTotal tokens used: [green bold]{prompt_tokens + completion_tokens}"
    )
    console.print(f"Estimated expense: [green bold]${total_expense}")


def get_openai_model(config):
    """
    Fetch available models from OpenAI API and let user select one
    or return configured model if specified
    
    Args:
        config (dict): Configuration dictionary containing API key and optional model
        
    Returns:
        str: Selected model identifier
    """
    # If model is specified in config, use that
    # if 'model' in config:
    #     return config['model']
        
    # Otherwise fetch available models from API
    headers = {
        "Authorization": f"Bearer {config['api-key']}",
    }
    
    try:
        r = requests.get(f"{BASE_ENDPOINT}/models", headers=headers)
        r.raise_for_status()
        
        models = r.json()['data']
        
        # Filter for chat models if not date YYYY-MM-DD in id
        chat_models = [model['id'] for model in models if "gpt" in model['id'] and "preview" not in model['id'] and "latest"  not in model['id'] and  not re.match(r".*\d{4}-\d{2}-\d{2}", model['id']) and not re.match(r".*-\d{4}(-|$)", model['id'])]
        
        
        # Sort by version
        chat_models.sort(reverse=True)
        
        # Let user select
        console.print("\nAvailable models:")
        for i, model in enumerate(chat_models, 1):
            console.print(f"{i}. {model}")
            
        while True:
            try:
                choice = int(input("\nSelect model number: "))
                if 1 <= choice <= len(chat_models):
                    return chat_models[choice-1]
            except ValueError:
                pass
            console.print("Invalid selection, try again", style="red")
            
    except requests.exceptions.RequestException as e:
        console.print(f"Error fetching models: {e}", style="red bold")
        # Fall back to default model
        return "gpt-3.5-turbo"


def prompt_openai_api(messages, config):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api-key']}",
    }

    # Base body parameters
    body = {
        "model": config["model"],
        "temperature": config["temperature"],
        "messages": messages,
    }
    # Optional parameter
    if "max_tokens" in config:
        body["max_tokens"] = config["max_tokens"]

    r = None
    try:
        r = requests.post(
            f"{BASE_ENDPOINT}/chat/completions", headers=headers, json=body
        )
    except requests.ConnectionError:
        console.print("Connection error, try again...", style="red bold")
        messages.pop()
        raise KeyboardInterrupt
    except requests.Timeout:
        console.print("Connection timed out, try again...", style="red bold")
        messages.pop()
        raise KeyboardInterrupt
    return r

def start_prompt(session: PromptSession, config: dict) -> None:
    """
    Ask the user for input, build the request and perform it
    """


    message = session.prompt(HTML(f"<b>[{prompt_tokens + completion_tokens}] >>> </b>"))

    if message.lower() == "/q":
        raise EOFError
    if message.lower() == "":
        raise KeyboardInterrupt

    messages.append({"role": "user", "content": message})

    lines = []
    if config["model"].startswith("gpt"):
        r = prompt_openai_api(messages, config)
        lines = parse_openai(r, config, messages)
    elif config["model"].startswith("claude"):
        # call the anthropic API
        lines = call_anthropic_api(messages, config)
        # print(lines)
    with open(os.path.join(SAVE_FOLDER, SAVE_FILE), "w") as f:
        json.dump({"model": config["model"], "messages": messages}, f, indent=4)



    for line in lines:
        console.print(line)

def call_anthropic_api(messages, config):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    # data = {
    #     "prompt": "\n".join([m["content"] for m in messages]),
    #     "max_tokens": 100,  # Adjust as needed
    #     "top_p": 1.0,  # Adjust as needed
    #     "stop_sequences": []  # Adjust as needed
    # }
    data = {
        "model": config["model"],
        "temperature": config["temperature"],
        "messages": messages,
        "max_tokens": config["max_tokens"],
    }

    response = requests.post(url, headers=headers, json=data)
    # print(response.json())
    if response.status_code == 200:
        answer = response.json()["content"][0]
        answer["role"] = "assistant"
        answer["content"] = answer["text"]
        del answer["text"]
        del answer["type"]
        messages.append(answer)

        return [x["text"] for x in response.json()["content"]]
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def parse_openai(r, config, messages):
    # TODO: Refactor to avoid a global variables
    global prompt_tokens, completion_tokens
    result = []
    # console.log(r.json())
    if r.status_code == 200:
        response = r.json()
        # console.log(response)
        message_response = response["choices"][0]["message"]
        usage_response = response["usage"]

        result.append("\n")
        if config["markdown"]:
            result.append(Markdown(message_response["content"].strip(), code_theme="lightbulb"))
        else:
            result.append(message_response["content"].strip())
        result.append("\n")

        prompt_tokens += usage_response["prompt_tokens"]
        completion_tokens += usage_response["completion_tokens"]

    elif r.status_code == 400:
        response = r.json()
        console.log(response)
        if "error" in response:
            if response["error"]["code"] == "context_length_exceeded":
                result.append("Maximum context length exceeded", style="red bold")
                raise EOFError
                # TODO: Develop a better strategy to manage this case
        result.append("Invalid request", style="bold red")
        raise EOFError

    elif r.status_code == 401:
        result.append("Invalid API Key", style="bold red")
        raise EOFError

    elif r.status_code == 429:
        result.append("Rate limit or maximum monthly limit exceeded", style="bold red")
        messages.pop()
        raise KeyboardInterrupt

    else:
        response = r.json()
        console.log(response)
        result.append(f"Unknown error, status code {r.status_code}", style="bold red")
        result.append(r.json())
        raise EOFError
    return result

@click.command()
@click.option(
    "-c",
    "--context",
    "context",
    type=click.File("r"),
    help="Path to a context file",
    multiple=True,
)
@click.option("-k", "--key", "api_key", help="Set the API Key")
@click.option("-m", "--model", "model", help="Set the model")
@click.option(
    "-ml", "--multiline", "multiline", is_flag=True, help="Use the multiline input mode"
)
def main(context, api_key, model, multiline) -> None:
    history = FileHistory(HISTORY_FILE)
    if multiline:
        session = PromptSession(history=history, multiline=True)
    else:
        session = PromptSession(history=history)

    try:
        config = load_config(CONFIG_FILE)
    except FileNotFoundError:
        console.print("Configuration file not found", style="red bold")
        sys.exit(1)

    create_save_folder()

    # Order of precedence for API Key configuration:
    # Command line option > Environment variable > Configuration file

    # If the environment variable is set overwrite the configuration
    if os.environ.get(ENV_VAR):
        config["api-key"] = os.environ[ENV_VAR].strip()
    # If the --key command line argument is used overwrite the configuration
    if api_key:
        config["api-key"] = api_key.strip()
    # If the --model command line argument is used overwrite the configuration
    if model:
        config["model"] = model.strip()

    # Run the display expense function when exiting the script
    # atexit.register(display_expense, model=config["model"])

    #console.print("ChatGPT CLI", style="bold")
    console.print(f"Model in use: [green bold]{config['model']}")
    console.print(f"Temperature: [green bold]{config['temperature']}")
    console.print(f"Max tokens: [green bold]{config['max_tokens']}")

    # Add the system message for code blocks in case markdown is enabled in the config file
    if config["markdown"]:
        add_markdown_system_message()

    # Context from the command line option
    if context:
        for c in context:
            console.print(f"Context file: [green bold]{c.name}")
            messages.append({"role": "system", "content": c.read().strip()})

    if config["model"].startswith("gpt") and config["model"].endswith("ask"):
        config["model"] = get_openai_model(config)

    console.rule()

    while True:
        try:
            start_prompt(session, config)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break


if __name__ == "__main__":
    main()
