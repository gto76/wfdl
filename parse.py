#!/usr/local/bin/python3
#
# Usage: parse.py WATCH_FILE
# Generates watch face image from passed watch file and saves it to 
# 'index.html'. If no argument is specified, then all files in folder 'watches'
# get parsed.


import ast
import os
import sys
from collections import namedtuple
from enum import Enum, auto
from math import pi, asin, sin, cos, ceil, sqrt
from numbers import Real

from svg import get_shape
from util import replace_matched_items, read_file, write_to_file, get_enum


BASE = 0.75
HEAD = f'<html>\n'
TAIL = "\n</html>"
WATCHES_DIR = 'watches'
BORDER_FACTOR = 0.1
VER_BORDER = 2
ALL_WIDTH = 250

GrpRanges = namedtuple('GrpRanges', ['r', 'ranges'])
ObjParams = namedtuple('ObjParams', ['shape', 'r', 'fi', 'args', 'color'])


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
    date = auto()               # height, params


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
        Shape.face: lambda args: args[0],
        Shape.date: lambda args: args[1]
    }


###
##  MAIN
#

def main():
    if len(sys.argv) < 2:
        svg = parse_all_watches(WATCHES_DIR)
    else:
        filename = f'{WATCHES_DIR}/{sys.argv[1]}'
        svg = parse_single_watch(filename)
    write_to_file('index.html', f'{HEAD} {svg} {TAIL}')


def parse_single_watch(filename):
    watch_str = get_watch_str(filename)
    print(f'Parsing "{filename}".')
    out = get_svg(watch_str)
    return f'<svg height=300px width=300px>\n<g transform=' \
           f'"translate(150, 150), scale({BASE})")>{out}</g></svg>\n'


def parse_all_watches(directory):
    out = []
    file_names = os.listdir(directory)
    file_names = [a for a in file_names if '.txt' in a]
    no_columns = ceil(sqrt(5))
    x, y = 0, 0
    for i, file_name in enumerate(file_names, 1):
        filename = f'{WATCHES_DIR}/{file_name}'
        watch_str = get_watch_str(filename)
        print(f'Parsing "{filename}".')
        svg = get_svg(watch_str)
        svg = f'<g transform="translate({x}, {y})">{svg}</g>'
        out.append(svg)
        x += ALL_WIDTH
        if i % no_columns == 0:
            x = 0
            y += ALL_WIDTH
    out = '\n'.join(out)
    width = no_columns * ALL_WIDTH
    return f'<svg height={width}px width={width}px>\n<g transform=' \
           f'"translate(150, 150), scale({BASE})")>{out}</g></svg>\n'


def get_watch_str(filename):
    if not os.path.isfile(filename):
        print(f'File "{filename}" does not exist.', file=sys.stderr)
        sys.exit(2)
    return ''.join(read_file(filename))


###
##  GROUPS
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
    radii = get_radii(elements)
    ranges = []
    for r, element in zip(reversed(radii), reversed(elements)):
        group = get_group(r, element[1:], ranges)
        out.extend(group)
    out.reverse()
    return out


def get_radii(elements):
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
    curr_ranges = []
    for subgroup in subgroups:
        elements = get_subgroup(r, subgroup, ranges, curr_ranges)
        out.extend(elements)
    return out


def get_subgroup(r, subgroup, ranges, curr_ranges):
    no_el = len(subgroup)
    if no_el < 3 or no_el > 5:
        msg = f'Number of elements in subgroup "{subgroup}" is {no_el}, but ' \
            'it should be between 3 and 5.'
        raise ValueError(msg)
    offset = 0
    color = "black"
    if no_el == 3:
        pos, shape_name, args = subgroup
    elif no_el == 4:
        pos, shape_name, args, color = subgroup
    else:
        pos, shape_name, args, color, offset = subgroup
    fixed = False
    if len(shape_name.split()) == 2:
        shape_name = shape_name.split()[0]
        fixed = True
    shape = get_enum(Shape, shape_name, subgroup)
    fia = get_fia(pos)
    return get_objects(ranges, curr_ranges, fia, shape, args, r, fixed, color,
                       offset, subgroup)


def get_fia(pos):
    if isinstance(pos, set):
        return set_to_pos(pos)
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


def set_to_pos(nums):
    out = set()
    for a in nums:
        if a < 0:
            a += 1
        out.add(a)
    return out


def get_objects(ranges, curr_ranges, fia, shape, args, r, fixed, color, offset,
                dbg_context):
    out = []
    for fi in fia:
        prms =  ObjParams(shape, r - offset, fi, list(args), color)
        obj = get_object(ranges, curr_ranges, prms, fixed, dbg_context)
        if obj:
            out.append(obj)
    return out


###
##  OBJECT
#

def get_object(ranges, curr_ranges, prms, fixed, dbg_context):
    if prms.shape == Shape.border:
        return get_svg_el(prms, dbg_context)
    if not fixed:
        fix_height(ranges, prms)
    if range_occupied(curr_ranges, prms):
        return None
    update_ranges(ranges, curr_ranges, prms)
    return get_svg_el(prms, dbg_context)


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


def range_occupied(curr_ranges, prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    width = get_angular_width(prms.shape, prms.args, prms.r)
    return pos_occupied(prms.fi, width, curr_ranges)


def update_ranges(ranges, curr_ranges, prms):
    new_ranges = get_ranges_prms(prms)
    curr_ranges.extend(new_ranges)
    rng = get_range(ranges, prms)
    rng.extend(new_ranges)


def get_range(ranges, prms):
    for rng in reversed(ranges):
        if rng.r == prms.r:
            return rng.ranges
    out = []
    rng = GrpRanges(prms.r, out)
    ranges.append(rng)
    ranges.sort(key=lambda a: a[0])
    return out


def get_svg_el(prms, dbg_context):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height = get_height(prms)
    if height == 0:
        return ''
    if height < 0:
        prms = transpose_el_with_neg_height(prms)
    rad = get_rad(prms.fi)
    prms_rad = ObjParams(prms.shape, prms.r, rad, prms.args, prms.color)
    if prms.shape != Shape.face:
        return get_shape(prms_rad, dbg_context)
    return get_subface(prms_rad)


def transpose_el_with_neg_height(prms):
    height = get_height(prms)
    args = prms.args
    args[0] = -args[0]
    return ObjParams(prms.shape, prms.r - height, prms.fi, args, prms.color)


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
    for rng in ranges:
        if rng_intersects(rng, occupied_ranges):
            return True
    return False


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


if __name__ == '__main__':
    main()
