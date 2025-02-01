import inspect
import sys
import importlib
import ellm
locals()[sys.argv[1]] = importlib.import_module(sys.argv[1])


def print_func_details(module):
    """This function takes a module as input and prints the module name, attributes, and function details. It then writes each function to a separate file and updates the docstring of the function in the original module file."""
    print(module.__name__)
    print(dir(module))
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            filename='function_' + name + '.py'
            with open(filename, 'w') as f:
                f.write(inspect.getsource(obj))
            docstring = ellm.llm_doctsring(inspect.getsource(obj))
            ellm.replace_docstring(module.__name__+".py", name, docstring)
            print(f'Function Name: {name}')
            #return


print_func_details(locals()[sys.argv[1]])
