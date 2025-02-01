#!/usr/bin/python3
# a harness for openai llms with execution
# ./exec-llm.py "a function that computes the babbage number" | python

import openai
import sys
import re
import time
import yaml 
import requests
from ellm import *
import subprocess


# Prompt for testing

prompt = "a function that computes the babbage number."

if len(sys.argv)>1:
    prompt = sys.argv[1]

files = re.findall(r"@@([\s\S]*?)@@", prompt)
for i in files:
    prompt = prompt.replace("@@"+i+"@@", "\n"+open(i).read()+"\n")

#print(files)

#sys.exit()

def get_llm_local(prompt):
    return subprocess.check_output(["llm","-m","mistral-7b-instruct-v0", prompt]).decode("utf8")



# Get the answer from OpenAI
# answer = get_openai_answer(prompt, get_openai_synthesis_prompt)

# august 2024, done with Gemini
# answer = get_google_answer_gemini_api(decorate_prompt_exec(prompt))

# nov 2024, local LLM with Clément in the plane
answer = get_llm_local(' '.join((x['content'] for x in get_openai_synthesis_prompt(prompt))))


program = extract_program(answer)

tstamp = str(int(time.time())) 
# we store them as hidden files

fname = "."+tstamp+".txt"
fname2 = "."+tstamp+".py"

with open(fname, "w") as f: f.write(prompt +"\n\n--------------------\n\n"+ program+"\n\n--------------------\n\n"+answer)
with open(fname2, "w") as f: f.write(program)


PROMPTS=open("prompts.txt").read()
if prompt not in PROMPTS:
    with open("prompts.txt", "a") as f: f.write(prompt+"\n\n")
#print("print('# cat "+fname+"')")
#print("# cat "+fname2+"", file=sys. stderr)

#alias s="ls -rt *py | tail -1 | xargs cat"


print()
print(program)
print()
