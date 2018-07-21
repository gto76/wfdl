#!/usr/local/bin/python3
#
# Usage: parse.py WATCH_FILE
# Generates watch face image from passed watch file and saves it to 
# 'index.html'.

import ast
import operator as op
import os
import re
import sys
from collections import namedtuple
from enum import Enum, auto
from math import pi, asin, sin, cos, ceil
from numbers import Number, Real

from svg import get_shape


BASE = 0.75
HEAD = f'<html>\n<svg height=300px width=300px>\n<g transform="translate(150,' \
       f' 150), scale({BASE})")>\n'
TAIL = "\n</g>\n</svg>\n</html>"
WATCHES_DIR = 'watches/'
BORDER_FACTOR = 0.1
VER_BORDER = 2

GrpRanges = namedtuple('GrpRanges', ['r', 'ranges'])
ObjParams = namedtuple('ObjParams', ['shape', 'r', 'fi', 'args', 'color'])

# COLORS = {"black": 0, "white": 255}


class Shape(Enum):
    border = auto()             # height, fi
    line = auto()               # height, width
    rounded_line = auto()       # height, width
    two_lines = auto()          # height, width, distance_factor
    circle = auto()             # height
    triangle = auto()           # height, width
    number = auto()             # height, kind (minute, roman, hour),
    # orient (horizontal, rotating, half_rotating) [, font]
    upside_triangle = auto()    # height, width
    square = auto()             # height
    octagon = auto()            # height, width, sides_factor
    arrow = auto()              # height, width, angle
    rhombus = auto()            # height, width
    trapeze = auto()            # height, width, width_2
    tear = auto()               # height, width
    spear = auto()              # height, width, center
    face = auto()               # height, params


ShapeTup = namedtuple('ShapeTup', ['shape', 'fixed'])

WIDTH_FORMULA = {
        Shape.line: lambda args: args[1],
        Shape.rounded_line: lambda args: args[1],
        Shape.two_lines: lambda args: 2*args[1] + args[1]*args[2],
        Shape.circle: lambda args: args[0],
        Shape.triangle: lambda args: args[1],
        Shape.number: lambda args: args[0] * 1.34,
        Shape.upside_triangle: lambda args: args[1],
        Shape.square: lambda args: args[0],
        Shape.octagon: lambda args: args[1],
        Shape.arrow: lambda args: args[1],
        Shape.rhombus: lambda args: args[1],
        Shape.trapeze: lambda args: args[1],
        Shape.tear: lambda args: args[1],
        Shape.spear: lambda args: args[1],
        Shape.face: lambda args: args[0]
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
    variables, beasel, face = get_parts(watch_str)
    beasel = replace_matched_items(beasel, variables)
    set_negative_height(beasel)
    face = replace_matched_items(face, variables)
    out = get_part_svg(beasel)
    out.extend(get_part_svg(face))
    return ''.join(out)


def set_negative_height(elements):
    if not elements:
        return
    for el in elements:
        el[0] = -el[0]
        for e in el[1:]:
            if len(e) < 3:
                pass
            args = e[2]
            args[0] = -args[0]


def get_parts(watch_str):
    parts = ast.literal_eval(watch_str)
    dictionary = {}
    beasel = None
    if isinstance(parts[0], dict):
        if len(parts) == 3:
            dictionary, beasel, elements = parts
        else:
            dictionary, elements = parts
    else:
        if len(parts) == 2:
            beasel, elements = parts
        else:
            elements = parts[0]
    return dictionary, beasel, elements


def get_part_svg(elements):
    if not elements:
        return []
    out = []
    radia = get_radia(elements)
    ranges = []
    for r, element in zip(reversed(radia), reversed(elements)):
        group = get_group(r, element[1:], ranges)
        out.extend(group)
    out.reverse()
    return out


def get_radia(elements):
    out = []
    r = 100
    offsets = [a[0] for a in elements]
    for offset in offsets:
        r -= offset
        out.append(r)
    return out


def get_group(r, subgroups, ranges):
    if not subgroups:
        return
    out = []
    ranges.append(GrpRanges(r, []))
    for subgroup in subgroups:
        elements = get_subgroup(r, subgroup, ranges)
        out.extend(elements)
    return out


def get_subgroup(r, subgroup, ranges):
    color = "black"
    if len(subgroup) == 3:
        pos, shape, args = subgroup
    elif len(subgroup) == 4:
        pos, shape, args, color = subgroup
    fixed = False
    if len(shape.split()) == 2:
        shape = shape.split()[0]
        fixed = True
    shape = Shape[shape]
    fia = get_fia(pos)
    return get_objects(ranges, fia, shape, args, r, fixed, color)


def get_fia(pos):
    if isinstance(pos, set):
        return pos
    elif isinstance(pos, Real):
        return [i / pos for i in range(ceil(pos))]
    elif isinstance(pos, list):
        n = pos[0]
        start = 0
        if len(pos) == 2:
            end = pos[1]
        else:
            start = pos[1]
            end = pos[2]
        return [i / n for i in range(n) if start <= i / n <= end]


def get_objects(ranges, fia, shape, args, r, fixed, color):
    out = []
    for fi in fia:
        obj = get_object(ranges, ObjParams(shape, r, fi, list(args), color), fixed)
        if not obj:
            continue
        out.append(obj)
    return out


###
##  OBJECT
#

def get_object(ranges, prms, fixed):
    if prms.shape == Shape.border:
        return get_svg_el(prms)
    if not fixed:
        fix_height(ranges, prms)
    if range_occupied(ranges, prms):
        return None
    update_ranges(ranges, prms)
    return get_svg_el(prms)


def fix_height(ranges, prms):
    height = get_height(prms)
    max_height = get_max_height(ranges, prms)
    if abs(height) > abs(max_height):
        update_height(prms.shape, prms.args, max_height)


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
            # out = prms.r - r
            # height = get_height(prms)
            # border = VER_BORDER if height < 0 else -VER_BORDER
            # max_height = out + border
            # if height > 0 and max_height <= 0:
            #     return 0
            # if height < 0 and max_height >= 0:
            #     return 0
            # return max_height
            return calculate_max_height(prms, r)
    return 100


def calculate_max_height(prms, r):
    out = prms.r - r
    height = get_height(prms)
    border = VER_BORDER if height < 0 else -VER_BORDER
    max_height = out + border
    if height > 0 >= max_height:
        return 0
    if height < 0 <= max_height:
        return 0
    return max_height


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
    height = get_height(prms)
    if height == 0:
        return ''
    if height < 0:
        args = prms.args
        args[0] = -args[0]
        prms = ObjParams(prms.shape, prms.r - height, prms.fi, args, prms.color)
    rad = get_rad(prms.fi)
    # brightness = COLORS[prms.color]
    # color = f'rgb({brightness}, {brightness}, {brightness})'
    prms_rad = ObjParams(prms.shape, prms.r, rad, prms.args, prms.color)
    if prms.shape != Shape.face:
        return get_shape(prms_rad)
    return get_subface(prms_rad)


def get_subface(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    face_str = str(prms.args[1])
    svg = get_svg(face_str)
    size = prms.args[0]
    x = cos(prms.fi) * (prms.r - size / 2)
    y = sin(prms.fi) * (prms.r - size / 2)
    scale = size / 200
    bckg = f'<circle cx={x} cy={y} r={size/2+VER_BORDER} style="stroke-width:' \
        '0; fill: rgb(255, 255, 255);"></circle>'
    return f'{bckg}<g transform="translate({x}, {y}), scale({scale})">{svg}</g>'


def get_rad(fi):
    return fi * 2 * pi - pi / 2


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
    width = abs(width_formula(args))
    return compute_angular_width(width, r)


def compute_angular_width(width, r):
    a_sin = width / r
    return asin(a_sin) / (2 * pi)


###
##  DICT SUB
#

def replace_matched_items(elements, dictionary):
    if not elements:
        return []
    out = []
    for element in elements:
        if type(element) is set:
            out.append(replace_in_set(element, dictionary))
        elif type(element) is list:
            out.append(replace_matched_items(element, dictionary))
        elif type(element) is dict:
            out.append(element)
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
