#!/usr/bin/python3
# a harness for openai llms with execution
# ./exec-llm.py "a function that computes the babbage number" | python

import openai
import sys
import re
import time
import yaml 
import requests
from io import StringIO
import tokenize
import difflib
from stockholm_diff import *
from  ellm import *

# Prompt for testing


if len(sys.argv)==0:
    print("summarize-file-with-llm.py <file-to-comment>")
    sys.exit(-1)


file_to_comment = sys.argv[1]
lang = file_to_comment.split(".")[-1]
#refactor_command = sys.argv[2]
# introduce a main function
prompt = "write a docstring summary of the following python function.\n"
initial_program = open(file_to_comment).read()
prompt += "```"+lang+"\n"+initial_program+"\n```"


# Get the answer from LLM based on the config
answer = get_llm_answer(prompt, lambda x: x)

print(answer)



#print(extract_program(answer, lang))
