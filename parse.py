#!/usr/bin/python3
#
# Usage: parse.py 
# 

import math
import sys
import re
import ast
import operator as op
from numbers import Number


BASE = 0.75
HEAD = '<html>\n<svg height=300px width=300px>\n<g transform="translate(150, 50), scale({})")>\n'.format(BASE)
TAIL = "\n</g>\n</svg>\n</html>"

SPEEDMASTER = [
                {'len_a': 2, 'widht_a': 0.5, 'off_b': 2},
                [
                  [100, ['len_a', 12, 0.75], [11, 60, 'widht_a'], ['len_a', 240, 'widht_a']],
                  ['100 - len_a - off_b', [23, 12, 5]]
                ]
              ]

def main():
    out = HEAD
    dictionary = SPEEDMASTER[0]
    elements = SPEEDMASTER[1]
    elements = replace_matched_items(elements, dictionary)
    for element in elements:
        out += get_group(element)
    print(out+TAIL)


def replace_matched_items(word_list, dictionary):
    out = []
    for element in word_list:
        if type(element) is list:
            out.append(replace_matched_items(element, dictionary))
        else:
            out.append(get_value_of_exp(element, dictionary))
    return out


def get_value_of_exp(exp, dictionary):
    if isinstance(exp, Number):
        return exp
    for key, value in dictionary.items():
        exp = exp.replace(key, str(value))
    return eval_expr(exp)


def get_group(elements):
    if len(elements) < 2:
        return
    out = ""
    filled_positions = set()
    offset = elements[0]
    elements = elements[1:]
    for element in elements:
        length = element[0]
        n = element[1]
        width = element[2]
        positions = get_positions(n)
        positions = positions.difference(filled_positions)
        out += get_circle(positions, offset, offset-length, width)
        filled_positions.update(positions)
    return out


def get_positions(n):
    return set([i/n for i in range(n)])


def get_circle(positions, ro, ri, width):
    out = ""
    for position in positions:
        deg = position * 2*math.pi
        out += get_line(deg, ri, ro, width)
    return out 


def get_line(deg, ri, ro, width):
    x1 = math.cos(deg) * ri
    x2 = math.cos(deg) * ro
    y1 = math.sin(deg) * ri
    y2 = math.sin(deg) * ro
    return '<line x1={} y1={} x2={} y2={} style="stroke-width:{}; ' \
           'stroke:#000000"></line>'.format(x1, y1, x2, y2, width)


###
##  EVAL
#

operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}


def eval_expr(expr):
    """
    >>> eval_expr('2^6')
    4
    >>> eval_expr('2**6')
    64
    >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
    -5.0
    """
    return eval_(ast.parse(expr, mode='eval').body)


def eval_(node):
    if isinstance(node, ast.Num): # <number>
        return node.n
    elif isinstance(node, ast.BinOp): # <left> <operator> <right>
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
        return operators[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(node)


if __name__ == '__main__':
    main()
