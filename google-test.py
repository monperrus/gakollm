from ellm import *
print(get_huggingface_answer("# a python function that computes an approximation of pi", lambda x: [{"content":x, "role":"user"}]))

