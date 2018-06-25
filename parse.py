#!/usr/local/bin/python3
#
# Usage: parse.py WATCH_FILE
# Generates watch face image from passed watch file and saves it to 
# 'index.html'.

import ast
import json
from math import sin, cos, pi
from numbers import Number
import operator as op
import os
import re
import sys
from itertools import count


BASE = 0.75
HEAD = f'<html>\n<svg height=300px width=300px>\n<g transform="translate(150,' \
       f' 150), scale({BASE})")>\n'
TAIL = "\n</g>\n</svg>\n</html>"


def main():
    if len(sys.argv) < 2:
        print('Missing watch file argument.', file=sys.stderr)
        sys.exit(1)
    watch_file = sys.argv[1]
    if not os.path.isfile(watch_file):
        print(f'File "{watch_file}" does not exist.', file=sys.stderr)
        sys.exit(2)
    watch_str = ''.join(read_file(watch_file))
    svg = get_svg(watch_str)
    write_to_file('index.html', HEAD + svg + TAIL)


def get_svg(watch_str):
    out = []
    dictionary, elements = ast.literal_eval(watch_str)
    elements = replace_matched_items(elements, dictionary)
    offset = 0
    for element in elements:
        offset += element[0]
        out.append(get_group(offset, element[1:]))
    return ''.join(out)


def get_group(offset, elements):
    if not elements:
        return
    out = ""
    filled_pos = set()
    for element in elements:
        pos, shape, args = element
        if isinstance(pos, Number):
            pos = get_positions(pos)
        if isinstance(pos, list):
            pos = get_positions_list(pos)
        pos = pos.difference(filled_pos)
        filled_pos.update(pos)
        out += get_shapes(pos, shape, args, offset)
    return out


def get_positions(n):
    return set([i/n for i in range(n)])


def get_positions_list(args):
    n = args[0]
    start = 0
    if len(args) == 2:
        end = args[1]
    else:
        start = args[1]
        end = args[2]
    return set([i/n for i in range(n) if i/n >= start and i/n <= end])


def get_shapes(pos, shape, args, offset):
    if shape == 'line':
        length, width = args
        return get_elements(pos, get_line, 
                            [100-offset, 100-offset-length, width])
    if shape == 'rounded line':
        length, width = args
        return get_elements(pos, get_rounded_line, 
                            [100-offset, 100-offset-length, width])
    elif shape == 'two lines':
        length, width, factor = args
        return get_elements(pos, get_two_lines, 
                            [100-offset, 100-offset-length, width, factor])
    elif shape == 'circle':
        diameter = args[0]
        return get_elements(pos, get_circle, [100-offset, diameter])
    elif shape == 'number':
        diameter = args[0]
        kind = args[1]
        orient = args[2]
        return get_elements(pos, get_number, [100-offset, diameter, kind, orient])
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


def get_number(args):
    deg, ro, diameter, kind, orient = args
    x = cos(deg) * (ro - diameter/2)
    y = sin(deg) * (ro - diameter/2)
    i = get_hour(deg) if kind == "hour" else get_minute(deg)
    rot = get_num_rotation(orient, deg, i)
    return f'<g transform="translate({x}, {y})"><text transform="rotate({rot})" class="title" fill="#111111" fill-opacity="0.9" font-size="{diameter}" font-weight="bold" alignment-baseline="middle" text-anchor="middle">{i}</text></g>'


def get_num_rotation(orient, deg, i):
    if orient == "horizontal":
        return 0
    elif orient == "rotating":
        return (deg + pi/2) / pi * 180
    else:
        delta = pi if deg > 0 and deg < pi else 0
        return (deg + pi/2 + delta) / pi * 180


def get_hour(deg):
    return deg_to_time(deg, 12)


def get_minute(deg):
    return deg_to_time(deg, 60)


def deg_to_time(deg, factor):
    i = (deg + pi/2) / (2*pi) * factor
    i = round(i)
    if i == 0:
        i = factor
    return i


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
    return _get_line(x1, y1, x2, y2, width)


def get_rounded_line(args):
    deg, ri, ro, width = args
    x1 = cos(deg) * ri
    x2 = cos(deg) * ro
    y1 = sin(deg) * ri
    y2 = sin(deg) * ro
    deg = (deg-pi/2) / pi * 180 
    return f'<rect rx="{width/2}" y="{ro}" x="-{width/2}" ry="{width/2}" transform="rotate({deg})" height="{ri-ro}" width="{width}"></rect>'


def get_two_lines(args):
    deg, ri, ro, width, sep = args
    x1 = cos(deg) * ri
    x2 = cos(deg) * ro
    y1 = sin(deg) * ri
    y2 = sin(deg) * ro
    r_line = abs(ri - ro)
    factor = width / 2 * (1 + sep)
    dx = sin(deg) * factor
    dy = cos(deg) * factor
    return _get_line(x1 + dx, y1 + dy, x2 + dx, y2 + dy, width) + \
        _get_line(x1 - dx, y1 - dy, x2 - dx, y2 - dy, width)


def _get_line(x1, y1, x2, y2, width):
    return f'<line x1={x1} y1={y1} x2={x2} y2={y2} style="stroke-width:{width}; ' \
           'stroke:#000000"></line>'


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


def write_to_file(filename, text):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)


if __name__ == '__main__':
    main()
