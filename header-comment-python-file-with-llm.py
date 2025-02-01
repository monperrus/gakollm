#!/usr/bin/python3
# a harness for openai llms with execution
# ./exec-llm.py "a function that computes the babbage number" | python

from openai import OpenAI


import sys
import re
import time
import yaml 
import requests
from io import StringIO
import tokenize
import difflib
from stockholm_diff import *

config={}
with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

client = OpenAI(api_key=config["api-key"])

def get_llm_answer(prompt):
    if config["provider"] == "openai":
        return get_gpt3_answer(prompt)
    if config["provider"] == "google":
        return get_bard_answer(prompt)
    if config["provider"] == "huggingface":
        return get_huggingface_answer(prompt)
    raise Exception()

def get_huggingface_answer(prompt):
    prompt =" ".join(x["content"] for x in get_openai_chat_promp(prompt))
    url = 'https://api-inference.huggingface.co/models/bigcode/starcoder'
    url = 'https://api-inference.huggingface.co/models/bigcode/starcoderplus'
    #url = 'https://api-inference.huggingface.co/models/ASSERT-KTH/RepairLLaMa'
    #url = 'https://api-inference.huggingface.co/models/bigcode/santacoder'
    #url = 'https://api-inference.huggingface.co/models/WizardLM/WizardCoder-15B-V1.0'
    #{'error': 'The model WizardLM/WizardCoder-15B-V1.0 is too large to be loaded automatically (31GB > 10GB). Please use Spaces (https://huggingface.co/spaces) or Inference Endpoints (https://huggingface.co/inference-endpoints).'}


    headers = {
        'Authorization': 'Bearer '+config["hf-key"],
        'Content-Type': 'application/json',
    }
    data = {
        "inputs": "# python function which adds all elements in a list",
        "parameters": {
            "max_new_tokens": 100,
            "stop": [],
            #"best_of": 1,
            #"details": true,
            #"do_sample": true,
            #"repetition_penalty": 1.03,
            #"return_full_text": true,
            #"seed": null,
            #"temperature": 0.5,
            #"top_k": 10,
            #"top_p": 0.95,
            #"truncate": null,
            #"typical_p": 0.95,
            #"watermark": true
        }
    }

    response = requests.post(url, headers=headers, json=data)
    print(response.json().generated_text)

def get_bard_answer(prompt):
    PROJECT_ID = "assert-experiments"
    MODEL_ID = "code-bison"
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/{MODEL_ID}:predict"

    prompt =" ".join(x["content"] for x in get_openai_chat_promp(prompt))
    #print(prompt)
    headers = {
    "Authorization": f"Bearer "+config["google-token"],
    "Content-Type": "application/json"
    }
    data = {
        "instances": [
            {"prefix": prompt}
        ],
        "parameters": {
            "temperature": 0.5,
            "maxOutputTokens": 256
        }
    }

    response = requests.post(url, headers=headers, json=data)
    #print(response.status_code)
    return response.json().predictions[0].content


def get_openai_chat_promp(prompt):
  return [
            {"role": "system", "content": "You are a software developer. You write only code as output, starting with ``` and ending with ```."},
            {"role": "user", "content": prompt}
        ]

def get_gpt3_answer(prompt):
    # Create a chat completion request
    response = client.chat.completions.create(#model="gpt-3.5-turbo",
    model="gpt-4-turbo",
    messages=get_openai_chat_promp(prompt),
    temperature=0)

    # Extract the generated answer from the response
    answer = response.choices[0].message.content

    return answer

def extract_program(answer, lang="python"):
# remove the syntax 
    lines = answer.split("\n")
    # sometimes the last lines is empty
    while lines[-1]=="": lines.pop()
    if lines[0].startswith("```") and lines[-1].startswith("```"):
        return "\n".join(lines[1:-1])
    raise Exception(answer)
    result = re.findall(r"```(?:"+lang+")?([\\s\\S]*?)```", answer)
    return "\n".join(result)

# Prompt for testing


if len(sys.argv)==0:
    print("comment-file-with-llm.py <file-to-comment>")
    sys.exit(-1)


file_to_comment = sys.argv[1]
lang = file_to_comment.split(".")[-1]
prompt = "add a header to the python file summarizing the program. return one single code block.\n"
initial_program = open(file_to_comment).read()
prompt += "```"+lang+"\n"+initial_program+"\n```"


# Get the answer from LLM based on the config
answer = extract_program(get_llm_answer(prompt))

# save the answer in a file
with open(file_to_comment+".commented", "w") as f:
    f.write(answer)

print(answer)

delta = diff_python(initial_program, answer)
for i in delta:
    print(i,file=sys. stderr)

if len(delta)>0:
    print("behavior has been changed by the LLM!!!",file=sys.stderr)
    # print the command to output the diff of the original and the commented program
    print(f"diff -u {file_to_comment} {file_to_comment}.commented",file=sys.stderr)



#print(extract_program(answer, lang))
