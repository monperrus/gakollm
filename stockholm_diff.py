#!/usr/bin/python3
# a library for behavioral diff
# from stockholm_diff import *
import sys
import re
import time
import yaml
import requests
from io import StringIO
import tokenize
import difflib
import ast
import astor

def remove_comments_and_docstrings(source):
    """The function `remove_comments_and_docstrings(source)` takes a string input `source` which represents a Python source code. It returns a modified version of the input source code with all the comments and docstrings removed. The function uses Python's tokenize module to parse the source code and selectively remove the comments and docstrings while preserving the indentation and structure of the code."""
    io_obj = StringIO(source)
    out = ''
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    for tok in tokenize.generate_tokens(io_obj.readline):
        token_type = tok[0]
        token_string = tok[1]
        (start_line, start_col) = tok[2]
        (end_line, end_col) = tok[3]
        ltext = tok[4]
        # The following two conditionals preserve indentation.
        # This is necessary because we're not using tokenize.untokenize()
        # (because it spits out code with copious amounts of oddly-placed
        # whitespace).
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            out += ' ' * (start_col - last_col)
        # Remove comments:
        if token_type == tokenize.COMMENT:
            pass
        # This series of conditionals removes docstrings:
        elif token_type == tokenize.STRING:
            if prev_toktype != tokenize.INDENT:
                # This is likely a docstring; double-check we're not inside an operator:
                if prev_toktype != tokenize.NEWLINE:
                    # Note regarding NEWLINE vs NL: The tokenize module
                    # differentiates between newlines that start a new statement
                    # and newlines inside of operators such as parens, brackes,
                    # and curly braces.  Newlines inside of operators are
                    # NEWLINE and newlines that start new code are NL.
                    # Catch whole-module docstrings:
                    if start_col > 0:
                        # Unlabelled indentation means we're inside an operator
                        out += token_string
                    # Note regarding the INDENT token: The tokenize module does
                    # not label indentation inside of an operator (parens,
                    # brackets, and curly braces) as actual indentation.
                    # For example:
                    # def foo():
                    #     "The spaces before this docstring are tokenize.INDENT"
                    #     test = [
                    #         "The spaces before this string do not get a token"
                    #     ]
        else:
            out += token_string
        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line
    return out
#https://stackoverflow.com/questions/63893283/difflib-ignore-whitespace-diffs-w-ndiff

def prefilter(line):
    '''"""
This function takes a string input 'line', removes any leading or trailing white spaces using the strip() method, and then replaces any occurrence of one or more consecutive white spaces in the string with a single space using the re.sub() method from the re module. The modified string is then returned.
"""'''
    return re.sub('\\s+', ' ', line.strip())

def split_for_diff(s):
    """The function 'prefilter' takes a single argument 'line' which is a string. It removes any leading or trailing white spaces from 'line' and replaces any occurrence of one or more consecutive white spaces within 'line' with a single space. The function returns the modified string."""
    # we remove empty lines as well
    return [prefilter(x) for x in s.split('\n') if len(prefilter(x)) > 0]

class RemoveDocstrings(ast.NodeTransformer):

    def visit_FunctionDef(self, node):
        if len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
            # remove first statement
            node.body = node.body[1:]
        return self.generic_visit(node)

    def visit_ClassDef(self, node):
        if len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
            # remove first statement
            node.body = node.body[1:]
        return self.generic_visit(node)

    def visit_Module(self, node):
        if len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
            # remove first statement
            node.body = node.body[1:]
        return self.generic_visit(node)

def str2ast2str(source):
    '''"""
This function visits a Module node in an Abstract Syntax Tree (AST). If the first statement of the module body is an expression and its value is a string, it removes the first statement from the body. The function then proceeds to visit all other nodes in the module using the generic_visit method.
"""'''
    tree = ast.parse(source)
    RemoveDocstrings().visit(tree)
    return ast.unparse(tree)

def diff_python(before, after):
    '''"""
This function takes two Python code strings as input, removes comments and docstrings, converts them into abstract syntax trees (ASTs), and then back into strings. It then uses the 'difflib' library to generate a list of differences between the two code strings. The differences are returned in a unified diff format.
"""'''
    f = remove_comments_and_docstrings
    f = str2ast2str
    before = f(before)
    after = f(after)
    delta = [x for x in difflib.unified_diff(split_for_diff(before), split_for_diff(after), n=0)]
    return delta
