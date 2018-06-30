#!/usr/local/bin/python3
#
# Usage: parse.py WATCH_FILE
# Generates watch face image from passed watch file and saves it to 
# 'index.html'.

import ast
from math import sin, cos, pi, asin
from numbers import Number
import operator as op
import os
import re
import sys
import enum
from enum import Enum
from collections import namedtuple


BASE = 0.75
HEAD = f'<html>\n<svg height=300px width=300px>\n<g transform="translate(150,' \
       f' 150), scale({BASE})")>\n'
TAIL = "\n</g>\n</svg>\n</html>"
ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IIII', 5: 'V', 6: 'VI', 7: 'VII',
         8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'}
WATCHES_DIR = 'watches/'
BORDER_FACTOR = 0.2
VER_BORDER = 2

GrpRanges = namedtuple('GrpRanges', ['r', 'ranges'])
ObjParams = namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])


class Shape(Enum):
    line = enum.auto()
    rounded_line = enum.auto()
    two_lines = enum.auto()
    circle = enum.auto()
    triangle = enum.auto()
    number = enum.auto()
    square = enum.auto()


WIDTH_FORMULA = {
        Shape.line: lambda args: args[1],
        Shape.rounded_line: lambda args: args[1],
        Shape.two_lines: lambda args: 2*args[1] + args[1]*args[2],
        Shape.circle: lambda args: args[0],
        Shape.number: lambda args: args[0],
        Shape.triangle: lambda args: args[1],
        Shape.square: lambda args: args[0]
    }


###
##  MAIN
#

def main():
    if len(sys.argv) < 2:
        print('Missing watch file argument.', file=sys.stderr)
        sys.exit(1)
    watch_file = WATCHES_DIR + sys.argv[1]
    if not os.path.isfile(watch_file):
        print(f'File "{watch_file}" does not exist.', file=sys.stderr)
        sys.exit(2)
    watch_str = ''.join(read_file(watch_file))
    svg = get_svg(watch_str)
    write_to_file('index.html', HEAD + svg + TAIL)


###
##  RENDERING
#

def get_svg(watch_str):
    out = []
    dictionary, elements = ast.literal_eval(watch_str)
    elements = replace_matched_items(elements, dictionary)
    rs = get_rs(elements)
    ranges = []
    for r, element in zip(reversed(rs), reversed(elements)):
        group = get_group(r, element[1:], ranges)
        out.extend(group)
    return ''.join(out)


def get_rs(elements):
    out = []
    r = 100
    offsets = [a[0] for a in elements]
    for offset in offsets:
        r -= offset
        out.append(r)
    return out


def get_group(r, elements, ranges):
    if not elements:
        return
    out = []
    ranges.append(GrpRanges(r, []))
    for element in elements:
        if len(element) < 3:
            out.append(get_circular_border(element, 100 - r))
            continue
        pos, shape, args = element
        shape = Shape[shape]
        fis = get_fis(pos)
        objects = get_objects(ranges, fis, shape, args, r)
        out.extend(objects)
    return out


def get_fis(pos):
    if isinstance(pos, set):
        return pos
    elif isinstance(pos, int):
        return [i / pos for i in range(pos)]
    elif isinstance(pos, list):
        n = pos[0]
        start = 0
        if len(pos) == 2:
            end = pos[1]
        else:
            start = pos[1]
            end = pos[2]
        return [i / n for i in range(n) if start <= i / n <= end]


def get_objects(ranges, fis, shape, args, r):
    out = (get_object(ranges, ObjParams(shape, r, fi, list(args)))
           for fi in fis)
    return [a for a in out if a]


###
##  OBJECT
#

def get_object(ranges, prms):
    height = get_height(prms)
    max_height = get_max_height(ranges, prms)
    if height > max_height:
        update_height(prms.shape, prms.args, max_height)
    if range_occupied(ranges, prms):
        return None
    update_ranges(ranges, prms)
    return get_svg_el(prms)


def get_height(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    return prms.args[0]


def get_max_height(all_ranges, prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    if len(all_ranges) <= 1:
        return 100
    for grp_ranges in reversed(all_ranges[:-1]):
        r, ranges = grp_ranges
        width = get_angular_width(prms.shape, prms.args, r)
        if pos_occupied(prms.fi, width, ranges):
            return (prms.r - r) - VER_BORDER
    return 100


def update_height(shape, args, height):
    if shape == Shape.triangle:
        height_old, width_old = args
        factor = height / height_old
        width = width_old * factor
        args[0], args[1] = height, width
    else:
        args[0] = height


def range_occupied(ranges, prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    width = get_angular_width(prms.shape, prms.args, prms.r)
    return pos_occupied(prms.fi, width, ranges[-1].ranges)


def update_ranges(occupied_ranges, prms):
    ranges = get_ranges_prms(prms)
    occupied_ranges[-1].ranges.extend(ranges)


def get_svg_el(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    drawers = {Shape.line: get_line, Shape.rounded_line: get_rounded_line,
               Shape.two_lines: get_two_lines, Shape.circle: get_circle,
               Shape.number: get_number, Shape.triangle: get_triangle}
    drawer = drawers[prms.shape]
    return drawer(prms)


###
## RANGES
#

def pos_occupied(fi, width, occupied_ranges):
    ranges = get_ranges(fi, width)
    return any(rng_intersects(rng, occupied_ranges) for rng in ranges)


def rng_intersects(rng, filled_ranges):
    start, end = rng
    for fil_range in filled_ranges:
        f_start, f_end = fil_range
        if (f_start <= start <= f_end) or (f_start <= end <= f_end) or \
                (start <= f_start and end >= f_end):
            return True
    return False


def get_ranges_prms(prms):
    width = get_angular_width(prms.shape, prms.args, prms.r)
    return get_ranges(prms.fi, width)


def get_ranges(pos, width):
    border = width * BORDER_FACTOR
    start = (pos - width / 2) - border
    end = (pos + width / 2) + border
    if start < 0:
        return [[start + 1, 1], [0, end]]
    if end > 1:
        return [[start, 1], [0, end - 1]]
    return [[start, end]]


def get_angular_width(shape, args, r):
    width_formula = WIDTH_FORMULA[shape]
    width = width_formula(args)
    return compute_angular_width(width, r)


def compute_angular_width(width, r):
    a_sin = width / r
    return asin(a_sin) / (2 * pi)


###
##  SVG
#

def get_line(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height, width = prms.args
    rad = get_rad(prms.fi)
    x1 = cos(rad) * prms.r
    x2 = cos(rad) * (prms.r - height)
    y1 = sin(rad) * prms.r
    y2 = sin(rad) * (prms.r - height)
    return _get_line(x1, y1, x2, y2, width)


def get_rounded_line(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height, width = prms.args
    rad = get_rad(prms.fi)
    rot = (rad - pi / 2) / pi * 180
    return f'<rect rx="{width/2}" y="{prms.r}" x="-{width/2}" ry="{width/2}" ' \
           f'transform="rotate({rot})" height="{height}" width="{width}">' \
           '</rect>'


def get_two_lines(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height, width, sep = prms.args
    rad = get_rad(prms.fi)
    x1 = cos(rad) * (prms.r - height)
    x2 = cos(rad) * prms.r
    y1 = sin(rad) * (prms.r - height)
    y2 = sin(rad) * prms.r
    factor = width / 2 * (1 + sep)
    dx = sin(rad) * factor
    dy = cos(rad) * factor
    return _get_line(x1 + dx, y1 + dy, x2 + dx, y2 + dy, width) + \
        _get_line(x1 - dx, y1 - dy, x2 - dx, y2 - dy, width)


def get_circle(prms):
    diameter = prms.args[0]
    rad = get_rad(prms.fi)
    cx = cos(rad) * (prms.r - diameter / 2)
    cy = sin(rad) * (prms.r - diameter / 2)
    return f'<circle cx={cx} cy={cy} r={diameter / 2} style="stroke-width: 0;' \
           ' fill: rgb(0, 0, 0);"></circle>'


def get_triangle(prms):
    height, width = prms.args
    rad = get_rad(prms.fi)
    x1 = (cos(rad) * prms.r) - (sin(rad) * width / 2)
    y1 = (sin(rad) * prms.r) + (cos(rad) * width / 2)
    x2 = (cos(rad) * prms.r) + (sin(rad) * width / 2)
    y2 = (sin(rad) * prms.r) - (cos(rad) * width / 2)
    x3 = cos(rad) * (prms.r - height)
    y3 = sin(rad) * (prms.r - height)
    return f'<polygon points="{x1},{y1} {x2},{y2} {x3},{y3}" />'


def get_number(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    font = ''
    if len(prms.args) == 3:
        size, kind, orient = prms.args
    else:
        size, kind, orient, font = prms.args
    rad = get_rad(prms.fi)
    x = cos(rad) * (prms.r - size / 2)
    y = sin(rad) * (prms.r - size / 2)
    i = get_num_str(kind, rad)
    rot = get_num_rotation(orient, rad)
    return f'<g transform="translate({x}, {y})"><text transform="rotate({rot}' \
           f')" class="title" fill="#111111" fill-opacity="0.9" font-size=' \
           f'"{size}" font-weight="bold" font-family="{font}" ' \
           f'alignment-baseline="middle" text-anchor="middle">{i}</text></g>'


# <polygon points="4.550000000000005,-94.0 -4.5499999999999945,-94.0
# 4.9598195365467806e-15,-81.0"></polygon>
# def get_square(prms):
#     # height, width = prms.args
#     side = prms.args[0]
#     rad = get_rad(prms.fi)
#     x1 = (cos(rad) * prms.r) - (sin(rad) * width / 2)
#     y1 = (sin(rad) * prms.r) + (cos(rad) * width / 2)
#     x2 = (cos(rad) * prms.r) + (sin(rad) * width / 2)
#     y2 = (sin(rad) * prms.r) - (cos(rad) * width / 2)
#     x3 = cos(rad) * (prms.r - height)
#     y3 = sin(rad) * (prms.r - height)
#     return f'<polygon points="{x1},{y1} {x2},{y2} {x3},{y3}" />'


def get_circular_border(element, ver_pos):
    stroke_width = element[1][0]
    return f'<circle cx=0 cy=0 r={100-ver_pos} style=" stroke-width: ' \
           f'{stroke_width}; stroke: rgb(0,0,0); fill: rgba(0,0,0,0)' \
           ';"></circle>'


###
##  SVG UTIL
#

def get_rad(fi):
    return fi * 2 * pi - pi / 2


def _get_line(x1, y1, x2, y2, width):
    return f'<line x1={x1} y1={y1} x2={x2} y2={y2} style="stroke-width:' \
           f'{width}; stroke:#000000"></line>'


def get_num_str(kind, deg):
    if kind == 'minute':
        return get_minute(deg)
    if kind == 'roman':
        hour = get_hour(deg)
        return ROMAN[hour]
    else:
        return get_hour(deg)


def get_num_rotation(orient, deg):
    if orient == "horizontal":
        return 0
    elif orient == "rotating":
        return (deg + pi / 2) / pi * 180
    else:
        delta = pi if 0 < deg < pi else 0
        return (deg + pi / 2 + delta) / pi * 180


def get_hour(deg):
    return deg_to_time(deg, 12)


def get_minute(deg):
    return deg_to_time(deg, 60)


def deg_to_time(deg, factor):
    i = (deg + pi / 2) / (2 * pi) * factor
    i = round(i)
    if i == 0:
        i = factor
    return i


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
