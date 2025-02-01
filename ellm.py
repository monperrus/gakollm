#!/usr/bin/python3
# This library is a harness for OpenLLMs
import os
from openai import OpenAI

import sys
import re
import time
import yaml
import requests
import json
import ast
import astor
import stockholm_diff
import ast_comments
import keyring
login_keyring=keyring.get_keyring()

import vertexai
from vertexai.generative_models import GenerativeModel

import google.auth
# credentials, project = google.auth.default()

# Initialize an empty dictionary for configuration
config = {}
# Load the configuration from a YAML file
with open(os.path.dirname(__file__)+"/"+'config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    
client = OpenAI(api_key=config['api-key'])

VERBOSE=0
DEFAULT_META=lambda x: [{"content":x, "role":"user"}]
# Function to get the LLM answer based on the provider specified in the configuration
def get_llm_answer(prompt, metaprompt=DEFAULT_META):
    """This function determines the appropriate answer provider based on the configuration settings and then calls the corresponding function to get the answer to the given prompt. If the provider is 'openai', it calls get_openai_answer, if 'google', it calls get_google_answer, and if 'huggingface', it calls get_huggingface_answer. If none of these providers are specified, it raises an Exception."""
    if VERBOSE>0: print('using provider ' + config['provider'], file=sys.stderr)
    if config['provider'] == 'openai':
        if VERBOSE>0: print('using model ' + config['model'], file=sys.stderr)
        return get_openai_answer(prompt, metaprompt)
    if config['provider'] == 'google':
        return get_google_answer_predict_api(prompt, metaprompt)
    if config['provider'] == 'huggingface':
        return get_huggingface_answer(prompt, metaprompt)
    raise Exception()
# Function to get the answer from Hugging Face model

def get_huggingface_answer(prompt, metaprompt=DEFAULT_META):
    """This function prepares a prompt, sets up the URL, headers, and data for making a request to the Hugging Face API, sends the request, and prints the generated text in response."""
    # Prepare the prompt
    prompt = ' '.join((x['content'] for x in metaprompt(prompt)))
    # Set the URL for the Hugging Face API
    url = 'https://api-inference.huggingface.co/models/bigcode/starcoderplus'
    # Set the headers for the API request
    headers = {'Authorization': 'Bearer '+config["hf-key"], 'Content-Type': 'application/json'}
    # Set the data for the API request
    data = {'inputs': prompt, 'parameters': {'max_new_tokens': 100, 'stop': []}}
    # Make the API request and print the generated text
    response = requests.post(url, headers=headers, json=data)
    # print(response.json())
    print(response.json()[0]["generated_text"])


def get_google_answer_gemini_api(prompt, metaprompt=DEFAULT_META):
    """
    works on August 2024
    """
    
    # Prepare the prompt
    prompt = ' '.join((x['content'] for x in metaprompt(prompt)))

    vertexai.init(project="assert-experiments", location="us-central1")

    MODEL_ID = "gemini-1.5-flash-001"
    MODEL_ID = "gemini-1.5-pro-001"
    model = GenerativeModel(MODEL_ID)

    response = model.generate_content(prompt)

    return response.text


def get_google_answer_predict_api(prompt, metaprompt=DEFAULT_META):
    # Prepare the prompt
    prompt = ' '.join((x['content'] for x in metaprompt(prompt)))

    """This function takes a prompt and a metaprompt as input, prepares the prompt, sets the necessary headers and data for an API request to a Google model, makes the API request, and returns the generated content from the response."""
    # Set the project and model IDs for the Google API
    PROJECT_ID = 'assert-experiments'
    
    # https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/code-bison
    # MODEL_ID = 'code-bison'
    
    # gemini
    MODEL_ID = 'gemini-1.5-pro-001'
    # {'error': {'code': 400, 'message': 'Gemini cannot be accessed through Vertex Predict/RawPredict API. Please follow https://cloud.google.com/vertex-ai/docs/generative-ai/start/quickstarts/quickstart-multimodal for Gemini usage.', 'status': 'FAILED_PRECONDITION'}}


    url = f'https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/{MODEL_ID}:predict'
    # Set the headers for the API request
    # headers = {'Authorization': f'Bearer ' + config['google-token'], 'Content-Type': 'application/json'}
    headers={}
    # https://console.cloud.google.com/iam-admin/serviceaccounts
    
    # credentials, project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    
    
    from google.oauth2 import service_account
    credentials = service_account.Credentials.from_service_account_info(json.loads(login_keyring.get_password('login2', 'google-service-account')))

    scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])

    from google.auth.transport.requests import AuthorizedSession

    authed_session = AuthorizedSession(scoped_credentials)

    # Set the data for the API request
    data = {'instances': [{'prefix': prompt}], 'parameters': {'temperature': 0.5, 'maxOutputTokens': 256}}
    # Make the API request and return the generated content
    response = authed_session.post(url, headers=headers, json=data)
    # print(response.json())
    return response.json()["predictions"][0]["content"]
# Function to prepare the chat prompt for OpenAI

def decorate_prompt_exec(prompt):
    return ' '.join((x['content'] for x in get_openai_synthesis_prompt(prompt)))

def get_openai_synthesis_prompt(prompt):
    """This function takes a prompt and a metaprompt as input, prepares the prompt, sets the necessary headers and data for an API request to a Google model, makes the API request, and returns the generated content from the response."""
    return [{'role': 'system', 'content': 'You are a software developer who writes python code. You write only code as output, starting with ``` and ending with ```.'}, {'role': 'user', 'content': 'write ' + json.dumps(prompt) + ' and at the end call that function'}]
# Function to get the answer from OpenAI's GPT-3 model

def get_openai_answer(prompt, metaprompt):
    """This function generates a synthesis prompt for OpenAI GPT-3 based on the input prompt provided. The prompt includes instructions for a software developer to write Python code that outputs only code enclosed in triple backticks."""
    # Set the temperature for the model
    temperature = 0  # for live coding
    if VERBOSE>0: print('using temperature ' + str(temperature), file=sys.stderr)
    # Create a chat completion request
    response = client.chat.completions.create(model=config['model'], messages=metaprompt(prompt), temperature=temperature)
    # Extract the generated answer from the response
    answer = response.choices[0].message.content
    return answer
# Function to extract the generated program from the answer

def extract_program(answer, lang='python'):
    """This function extracts the code program from a given answer string by removing the syntax and returning the code program in the specified language (default is Python)."""
    lines = answer.split('\n')
    while lines[-1] == '':
        # Remove the syntax 
        # Sometimes the last lines is empty
        lines.pop()
    if lines[0].startswith('```') and lines[-1].startswith('```'):
        return '\n'.join(lines[1:-1])
    result = re.findall('```(?:' + lang + ')?([\\s\\S]*?)```', answer)
    return '\n'.join(result)

def llm_doctsring(source, lang='python'):
    """This function extracts the code program from a given answer string by removing the syntax and returning the code program in the specified language (default is Python)."""
    prompt = 'write a docstring summary of the following python function.\n'
    initial_program = source
    prompt += '```' + lang + '\n' + initial_program + '\n```'
    return get_llm_answer(prompt)

def remove_function(initial_program, function_name):
    """This function extracts the code program from a given answer string by removing the syntax and returning the code program in the specified language (default is Python)."""
    tree = ast_comments.parse(initial_program)
    # Find function named 'foo' and remove it
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            tree.body.remove(node)
    # pretty print incl. comments
    # checking for absenece of differences
    return ast_comments.unparse(tree)

def replace_docstring(filename, fname, newdocstring):
    """This function extracts the code program from a given answer string by removing the syntax and returning the code program in the specified language (default is Python)."""
    initial_program = ''

    # Regular expression pattern with multiline support
    pattern = r'"""((?:.|[\n\r])*?)"""'

    # Find and display the content of the docstring
    match = re.search(pattern, newdocstring, re.DOTALL)
    if match:
        newdocstring = match.group(1)

    # Parse the Python source file
    with open(filename, 'r') as source:
        initial_program = source.read()
        # parse the source with comments nodes in ast
        tree = ast_comments.parse(initial_program)
    # Find function named 'foo' and replace its docstring
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fname:
            ast.get_docstring(node, clean=True)
            # if first statement is docstring, replace it
            if len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                node.body[0].value.s = newdocstring
            else:
                # prepend it
                node.body.insert(0, ast.Expr(ast.Str(newdocstring)))
    # pretty print incl. comments
    # checking for absenece of differences
    ppprogram = ast_comments.unparse(tree)
    delta = stockholm_diff.diff_python(initial_program, ppprogram)
    for i in delta:
        print(i, file=sys.stderr)
    if len(delta) > 0:
        print('behavior has been changed by the LLM!!!', file=sys.stderr)
        # print the command to output the diff of the original and the commented program
    # print(f"diff -u {file_to_comment} {file_to_comment}.commented",file=sys.stderr)
    # Write the modified tree back to the source file
    with open(filename, 'w') as source:
        source.write(ppprogram)
