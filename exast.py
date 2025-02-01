#!/usr/bin/python3
# -*- coding: utf-8 -*-

import ast
import pprint
DATA={}

def all_operands(node, ret):
    # this is a BoolOp node
    if isinstance(node, ast.BoolOp):
        #print(f"BoolOp: {node.op}")
        for operand in node.values:
            if not isinstance(operand, ast.BoolOp):
                print(f"if \"{operand.left.value}\" in reason_txt: return \"{operand.left.value}\", \"{ret}\"")
                DATA[ret].append(operand.left.value)
            all_operands(operand, ret)
def extract_function_calls(node):
    # if this is an IF node
    if isinstance(node, ast.If):
        val = node.body[0].value
        DATA[val.value]=[]
        print(f"## {val.value}")
        all_operands(node.test, val.value)
        # print the value of the then statement
        # pretty print the value
        #print(f"\"{val.value}\"")

    for child_node in ast.iter_child_nodes(node):
        extract_function_calls(child_node)

with open('./test.py', 'r') as file:
    code = file.read()
    tree = ast.parse(code)
    extract_function_calls(tree)
    pprint.pprint(DATA)
