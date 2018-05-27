#!/usr/local/bin/python3
#
# Usage: parse.py 
# 

import ast
import json
from math import sin, cos, pi
from numbers import Number
import operator as op
import os
import re
import sys


BASE = 0.75
HEAD = '<html>\n<svg height=300px width=300px>\n<g transform="translate(150, ' \
       '150), scale({})")>\n'.format(BASE)
TAIL = "\n</g>\n</svg>\n</html>"

SPEEDMASTER = [
                {'a_len': 2, 'a_width': 0.5, 'b_off': 2, 'b_len': 23, 
                 'c_diameter': 3},
                [
                  [1, 
                    [12, 'line', ['a_len', 'a_width * 1.5']], 
                    [60, 'line', [11, 'a_width']], 
                    [240, 'line', ['a_len', 'a_width']]],
                  ['a_len + b_off', 
                    [12, 'line', ['b_len', 5]]],
                  ['b_len - c_diameter', 
                    [{'1/60', '-1/60'}, 'circle', ['c_diameter']]]
                ]
              ]

# SUBMARINER = [
#                {'a_len': 3, 'a_width': 0.75, 'b_off': 2, 'b_len': 30, 
#                 'c_diameter': 3},
#                [
#                  [1,
#                    [12, 'line', ['a_len', 'a_width * 1.5']],
#                    [60, 'line', ['a_len', 'a_width']]],
#                  ['a_len + b_off',
#                    [1, 'triangle', ['b_len', 'b_len * 0.7']],
#                    [4, 'line', ['b_len', 'b_len / 3']],
#                    [12, 'circle', ['b_len * 0.55']]]
#                ]
#              ]

def main():
    if len(sys.argv) < 2:
        print('Missing watch file argument.', file=sys.stderr)
        sys.exit(1)
    watch_file = sys.argv[1]
    if not os.path.isfile(watch_file):
        print(f'File "{watch_file}" does not exist.', file=sys.stderr)
        sys.exit(2)
    out = HEAD
    watch_str = ''.join(read_file(watch_file))
    dictionary, elements = ast.literal_eval(watch_str)
    elements = replace_matched_items(elements, dictionary)
    offset = 0
    for element in elements:
        offset += element[0]
        out += get_group(offset, element[1:])
    print(out+TAIL, file='index.html')


def get_group(offset, elements):
    if not elements:
        return
    out = ""
    filled_pos = set()
    for element in elements:
        pos, shape, args = element
        if isinstance(pos, Number):
            pos = get_positions(pos)
        pos = pos.difference(filled_pos)
        filled_pos.update(pos)
        out += get_shapes(pos, shape, args, offset)
    return out


def get_positions(n):
    return set([i/n for i in range(n)])


def get_shapes(pos, shape, args, offset):
    if shape == 'line':
        length, width = args
        return get_elements(pos, get_line, 
                            [100-offset, 100-offset-length, width])
    elif shape == 'circle':
        diameter = args[0]
        return get_elements(pos, get_circle, [100-offset, diameter])
    elif shape == 'triangle':
        length, width = args
        return get_elements(pos, get_triangle, 
                            [100-offset, 100-offset-length, width])
    return ""


def get_elements(positions, drawer, args):
    out = ""
    for position in positions:
        deg = position * 2*pi - pi/2
        out += drawer([deg] + args)
    return out 


def get_circle(args):
    deg, ro, diameter = args
    cx = cos(deg) * (ro - diameter/2)
    cy = sin(deg) * (ro - diameter/2)
    return '<circle cx={} cy={} r={} style="stroke-width: 0; fill: rgb(0, 0, ' \
           '0);"></circle>'.format(cx, cy, diameter/2)


def get_line(args):
    deg, ri, ro, width = args
    x1 = cos(deg) * ri
    x2 = cos(deg) * ro
    y1 = sin(deg) * ri
    y2 = sin(deg) * ro
    return '<line x1={} y1={} x2={} y2={} style="stroke-width:{}; ' \
           'stroke:#000000"></line>'.format(x1, y1, x2, y2, width)


def get_triangle(args):
    deg, ro, ri, width = args
    x1 = (cos(deg) * ro) - (sin(deg) * width / 2)
    y1 = (sin(deg) * ro) + (cos(deg) * width / 2)
    x2 = (cos(deg) * ro) + (sin(deg) * width / 2)
    y2 = (sin(deg) * ro) - (cos(deg) * width / 2)
    x3 = cos(deg) * ri
    y3 = sin(deg) * ri
    return '<polygon points="{},{} {},{} {},{}" />'.format(x1, y1, x2, y2, x3, 
                                                           y3)


###
##  DICT SUB
#

def replace_matched_items(elements, dictionary):
    out = []
    for element in elements:
        if type(element) is set:
            out.append(replace_in_set(element, dictionary))
        elif type(element) is list:
            out.append(replace_matched_items(element, dictionary))
        else:
            out.append(get_value_of_exp(element, dictionary))
    return out


def replace_in_set(elements, dictionary):
    return {get_value_of_exp(element, dictionary) for element in elements}


def get_value_of_exp(exp, dictionary):
    if isinstance(exp, Number):
        return exp
    for key, value in dictionary.items():
        exp = exp.replace(key, str(value))
    if re.search('[a-zA-Z]', exp):
        return exp
    return eval_expr(exp)


###
##  EVAL
#

operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}


def eval_expr(expr):
    return eval_(ast.parse(expr, mode='eval').body)


def eval_(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp):
        return operators[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(node)


###
##  UTIL
#

def read_file(filename):
    with open(filename, encoding='utf-8') as file:
        return file.readlines()


def read_json_file(filename):
    with open(filename, encoding='utf-8') as file:
        return json.load(file)


if __name__ == '__main__':
    main()
