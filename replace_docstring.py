import ast
import inspect
import astor
from ellm import replace_docstring

# if main file
if __name__ == "__main__":
    # Replace the docstring of function 'foo' in 'example.py'
    # Replace docstring of function 'foo' in file 'test.py'
    replace_docstring('test.py', "foo", "new docstring")
    

