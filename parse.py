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
from math import pi, asin, ceil, sqrt, floor, isclose
from numbers import Real

from shape import Shape
from svg import get_shape
from util import replace_matched_items, read_file, write_to_file, get_enum, \
    check_args, get_rad, get_point


BASE = 0.75
HEAD = f'<html>\n'
TAIL = "\n</html>"
WATCHES_DIR = 'watches'
BORDER_FACTOR = 0.1
VER_BORDER = 2
ALL_WIDTH = 250

Range = namedtuple('Range', ['start', 'end'])
GrpRanges = namedtuple('GrpRanges', ['r', 'ranges'])
ObjParams = namedtuple('ObjParams', ['shape', 'r', 'fi', 'args', 'color'])
ShapeTup = namedtuple('ShapeTup', ['shape', 'fixed'])


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
    svg = parse_file(filename)
    return f'<svg height=300px width=300px>\n<g transform=' \
           f'"translate(150, 150), scale({BASE})")>{svg}</g></svg>\n'


def parse_all_watches(directory):
    out = []
    filenames = os.listdir(directory)
    filenames = [a for a in filenames if '.txt' in a]
    no_columns = ceil(sqrt(len(filenames)))
    x, y = 0, 0
    for i, filename in enumerate(filenames, 1):
        svg = get_watch_relative(directory, filename, x, y)
        out.append(svg)
        x += ALL_WIDTH
        if i % no_columns == 0:
            x = 0
            y += ALL_WIDTH
    out = '\n'.join(out)
    width = no_columns * ALL_WIDTH
    return f'<svg height={width}px width={width}px>\n<g transform=' \
           f'"translate(150, 150), scale({BASE})")>{out}</g></svg>\n'


def get_watch_relative(directory, filename, x, y):
    path = f'{directory}/{filename}'
    svg = parse_file(path)
    return f'<g transform="translate({x}, {y})">{svg}</g>'


def parse_file(path):
    watch_str = get_watch_str(path)
    print(f'Parsing "{path}".')
    return get_svg(watch_str)


def get_watch_str(path):
    if not os.path.isfile(path):
        print(f'File "{path}" does not exist.', file=sys.stderr)
        sys.exit(2)
    return ''.join(read_file(path))


###
##  GROUPS
#

def get_svg(watch_str):
    variables, bezel, face = get_parts(watch_str)
    bezel = replace_matched_items(bezel, variables)
    set_negative_height(bezel)
    face = replace_matched_items(face, variables)
    bezel_parts = get_part_svg(bezel)
    bezel_height = 100
    if bezel_parts:
        bezel_svg, bezel_height = bezel_parts
    else:
        bezel_svg = bezel_parts
    face_svg, _ = get_part_svg(face)
    svg = ''.join(bezel_svg + face_svg)
    return scale_svg(svg, bezel_height)


def scale_svg(svg, bezel_height):
    if bezel_height == 100:
        return svg
    factor = 200 / (2*bezel_height)
    return f'<g transform="scale({factor})">{svg}</g>'


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
    bezel = None
    if isinstance(parts[0], dict):
        if len(parts) == 3:
            dictionary, bezel, elements = parts
        else:
            dictionary, elements = parts
    else:
        if len(parts) == 2:
            bezel, elements = parts
        else:
            elements = parts[0]
    return dictionary, bezel, elements


def get_part_svg(elements):
    if not elements:
        return []
    out = []
    radii = get_radii(elements)
    ranges = []
    max_height = 0
    for r, element in zip(reversed(radii), reversed(elements)):
        group, height = get_group(r, element[1:], ranges)
        out.extend(group)
        if height > max_height:
            max_height = height
    out.reverse()
    return out, max_height


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
    max_height = 0
    ranges.append(GrpRanges(r, []))
    curr_ranges = []
    for subgroup in subgroups:
        elements, height = get_subgroup(r, subgroup, ranges, curr_ranges)
        out.extend(elements)
        if height > max_height:
            max_height = height
    return out, max_height


def get_subgroup(r, subgroup, ranges, curr_ranges):
    offset, color = 0, "black"
    no_el = get_no_el(subgroup)
    if no_el == 3:
        pos, shape_name, args = subgroup
    elif no_el == 4:
        pos, shape_name, args, color = subgroup
    else:
        pos, shape_name, args, color, offset = subgroup

    shape_name, fixed, centered = parse_shape(shape_name)
    shape = get_enum(Shape, shape_name, subgroup)
    fii = get_fii(pos)
    if centered:
        offset -= shape.get_height(args) / 2
    return get_objects(ranges, curr_ranges, fii, shape, args, r - offset, fixed,
                       color, subgroup)


def get_no_el(subgroup):
    no_el = len(subgroup)
    if no_el < 3 or no_el > 5:
        msg = f'Number of elements in subgroup "{subgroup}" is {no_el}, but ' \
            'it should be between 3 and 5.'
        raise ValueError(msg)
    return no_el


def parse_shape(shape_name):
    fixed = 'fixed' in shape_name
    centered = 'centered' in shape_name
    shape_name = shape_name.split()[0]
    return shape_name, fixed, centered


def get_fii(pos):
    if isinstance(pos, set):
        return set_to_pos(pos)
    elif isinstance(pos, Real):
        return [i / pos for i in range(ceil(pos))]
    elif isinstance(pos, dict):
        if 'tachy' in pos:
            # return pos['tachy']
            return get_tachy(pos['tachy'])
        position = pos['pos']
        if 'offset' in pos:
            offset = pos['offset']
            off = 1 / floor(position) * offset
            return [i/position + off for i in range(ceil(position))]
        elif 'filter' in pos:
            a_filter = pos['filter']
            return [a/position for a in a_filter]
    elif isinstance(pos, list):
        n = pos[0]
        start = 0
        if len(pos) == 2:
            end = pos[1]
        else:
            start = pos[1]
            end = pos[2]
        return [i / n for i in range(n) if is_between(i/n, start, end)]


def get_tachy(locations):
    return [60/a for a in locations]


def is_between(fi, fi_start, fi_end):
    fi, fi_start, fi_end = normalize_fi(fi), normalize_fi(fi_start), \
                           normalize_fi(fi_end)
    if isclose(fi, fi_start) or isclose(fi, fi_end):
        return True
    crosses_zero = fi_start > fi_end
    if crosses_zero:
        between_start_and_zero = fi_start <= fi
        between_zero_and_end = fi <= fi_end
        return between_start_and_zero or between_zero_and_end
    return fi_start <= fi <= fi_end


def normalize_fi(fi):
    if -1 >= fi >= 1:
        fi %= 1
    if fi < 0:
        fi += 1
    return fi


def set_to_pos(nums):
    out = set()
    for a in nums:
        if a < 0:
            a += 1
        out.add(a)
    return out


def get_objects(ranges, curr_ranges, fii, shape, args, r, fixed, color,
                dbg_context):
    out = []
    height = 0
    for fi in fii:
        prms = ObjParams(shape, r, fi, list(args), color)
        check_args(prms, dbg_context)
        obj = get_object(ranges, curr_ranges, prms, fixed, dbg_context)
        if not obj:
            continue
        out.append(obj)
        if height == 0:
            height = get_height(prms) + r
    return out, height


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
    return prms.shape.get_height(prms.args)


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
    ranges.sort(key=lambda a: a.r)
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
    p = get_point(prms.fi, prms.r - size/2)
    scale = size / 200
    bckg = f'<circle cx={p.x} cy={p.y} r={size/2+VER_BORDER} ' \
        f'style="stroke-width:0; fill: rgb(255, 255, 255);"></circle>'
    return f'{bckg}<g transform="translate({p.x}, {p.y}), scale({scale})">' \
        f'{svg}</g>'


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
    start, end = rng.start, rng.end
    for fil_range in filled_ranges:
        f_start, f_end = fil_range.start, fil_range.end
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
        return [Range(start + 1, 1), Range(0, end)]
    if end > 1:
        return [Range(start, 1), Range(0, end - 1)]
    return [Range(start, end)]


def get_angular_width(shape, args, r):
    width = shape.get_width(args)
    width = abs(width)
    return compute_angular_width(width, r)


def compute_angular_width(width, r):
    a_sin = width / r
    return asin(a_sin) / (2 * pi)


if __name__ == '__main__':
    main()
