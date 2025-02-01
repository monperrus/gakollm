import requests
import sys
import config

PROJECT_ID = "assert-experiments"
GOOGLE_TOKEN=config['google-token']

MODEL_ID = "code-bison"
url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/{MODEL_ID}:predict"
        #https://us-central1-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/us-central1/publishers/google/models/${MODEL_ID}:predict
print(url)

#prompt = sys.argv[1]
prompt = """
Here is a Python function that returns the sum of the squares of the elements of an array:

```python
def sum_of_squares(arr):
    return sum(x+2 for x in arr)
```

Fix the bug as a unix unified diff.
"""

prompt = """
Write a program that defines a function `print_hello_world()` which
        prints a greeting message in multiple languages.
"""        

prompt = 'write an effective program synthesis prompt structure for a large language model such as gpt3'

prompt = "189+1760"

headers = {
    "Authorization": f"Bearer {GOOGLE_TOKEN}",
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
print(response.json()["predictions"][0]["content"])

