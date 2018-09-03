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
from math import ceil, sqrt

from fii import get_fii
from fonts import get_font_def
from options import OptInfo, get_option_values
from ranges import GrpRanges, range_occupied, update_ranges, pos_occupied, \
    get_angular_width
from shape import Shape
from svg import get_shape
from util import replace_matched_items, read_file, write_to_file, get_enum, \
    check_args, get_rad, get_point, add_defaults


INVERT_COLOR = False

BASE = 0.75
HEAD = f'<html>\n'
TAIL = "\n</html>"
WATCHES_DIR = 'watches'
VER_BORDER = 2
ALL_WIDTH = 250
RADIUS_KEY = 'RADIUS'
DIAMETER_KEY = 'DIAMETER'
UNIT_KEY = 'UNIT'

INCLUDED_FONTS = 'lange', 'lange_thin'

ObjParams = namedtuple('ObjParams', ['shape', 'r', 'fi', 'args', 'color'])
ShapeTup = namedtuple('ShapeTup', ['shape', 'fixed'])

OPTIONS = (
    OptInfo('max_lines', 'l', True, int, 10000)
)


###
##  MAIN
#

def main():
    max_lines, args = get_option_values(OPTIONS, sys.argv)
    if len(args) < 1:
        svg = parse_all_watches(WATCHES_DIR, max_lines)
    else:
        filename = f'{WATCHES_DIR}/{args[0]}'
        svg = parse_single_watch(filename)
    write_to_file('index.html', f'{get_head()} {svg} {TAIL}')


def get_head():
    fonts_defs = [get_font_def(a) for a in INCLUDED_FONTS]
    fonts_css = '\n'.join(fonts_defs)
    return f'{HEAD}\n<style type="text/css">\n{fonts_css}\n</style>'


def parse_single_watch(filename):
    svg = parse_file(filename)
    return f'<svg height=300px width=300px>\n<g transform=' \
           f'"translate(150, 150), scale({BASE})")>{svg}</g></svg>\n'


def parse_all_watches(directory, max_lines=None):
    out = []
    filenames = os.listdir(directory)
    filenames = [a for a in filenames if '.txt' in a]
    no_watches = len(filenames)
    no_columns = ceil(sqrt(no_watches)) if not max_lines else \
        ceil(no_watches / max_lines)
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
    return get_watch(watch_str)


def get_watch_str(path):
    if not os.path.isfile(path):
        print(f'File "{path}" does not exist.', file=sys.stderr)
        sys.exit(2)
    return ''.join(read_file(path))


###
##  GET WATCH
#

def get_watch(watch_str, r_factor=1):
    variables, bezel, face = get_parts(watch_str)
    if RADIUS_KEY in variables:
        radius = variables[RADIUS_KEY]
        r_factor = 100 / radius
    elif DIAMETER_KEY in variables:
        diameter = variables[DIAMETER_KEY]
        r_factor = 200 / diameter
    variables[UNIT_KEY] = 1 / r_factor
    bezel, face = sub_variables(variables, bezel, face)
    set_negative_height(bezel)
    bezel_parts = get_part_svg(bezel, r_factor)
    bezel_height = 100
    if bezel_parts:
        bezel_svg, bezel_height = bezel_parts
    else:
        bezel_svg = bezel_parts
    face_svg, _ = get_part_svg(face, r_factor)
    svg = ''.join(bezel_svg + face_svg)

    # Move the background here (from get_subface)
    # bckg = f'<circle cx={p.x} cy={p.y} r={size/2+VER_BORDER} ' \
    #        f'style="stroke-width:0; fill: {fill_color};"></circle>'
    # return f'{bckg}<g transform="translate({p.x}, {p.y}), scale({scale})">' \
    #        f'{svg}</g>'

    return scale_svg(svg, bezel_height)


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


def sub_variables(variables, bezel, face):
    # Double pass:
    variables = var_pass(variables)
    variables = var_pass(variables)
    bezel = replace_matched_items(bezel, variables)
    face = replace_matched_items(face, variables)
    return bezel, face


def var_pass(variables):
    keys = variables.keys()
    values = replace_matched_items(variables.values(), variables)
    return dict(zip(keys, values))


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


def scale_svg(svg, bezel_height):
    if bezel_height == 100:
        return svg
    factor = 200 / (2*bezel_height)
    return f'<g transform="scale({factor})">{svg}</g>'


###
##  GET PART (Bezel/face)
#

def get_part_svg(elements, r_factor):
    """Part is either face or bezel."""
    if not elements:
        return []
    out = []
    radii = get_radii(elements, r_factor)
    ranges = []
    max_height = 0
    for r, element in zip(reversed(radii), reversed(elements)):
        group, height = get_group(r, element[1:], ranges, r_factor)
        out.extend(group)
        if height > max_height:
            max_height = height
    out.reverse()
    return out, max_height


def get_radii(elements, r_factor):
    out = []
    r = 100
    offsets = [a[0]*r_factor for a in elements]
    for offset in offsets:
        r -= offset
        out.append(r)
    return out


def get_group(r, group, ranges, r_factor):
    """Group consists of subgroups with same radius."""
    if not group:
        return
    out = []
    max_height = 0
    ranges.append(GrpRanges(r, []))
    curr_ranges = []
    for subgroup in group:
        elements, height = get_subgroup(r, subgroup, ranges, curr_ranges,
                                        r_factor)
        out.extend(elements)
        if height > max_height:
            max_height = height
    return out, max_height


###
##  GET SUBGROUP (Objects with same shape and radius)
#

def get_subgroup(r, subgroup, ranges, curr_ranges, r_factor):
    """Subgroup consists of objects with same properties except for fi."""
    pos, shape_name, args, offset, color = \
        add_defaults(subgroup, [None, None, None, 0, 'black'])
    offset *= r_factor
    shape_name, fixed, centered = parse_shape(shape_name)
    shape = get_enum(Shape, shape_name, subgroup)
    update_lengths(shape, args, r_factor)
    fii = get_fii(pos)
    if centered:
        offset -= shape.get_height(args) / 2
    r -= offset
    prmii = (ObjParams(shape, r, fi, list(args), color) for fi in fii)
    return get_objects(ranges, curr_ranges, prmii, fixed, subgroup, r_factor)


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


def update_lengths(shape, args, r_factor):
    no_size_args = shape.value.no_size_args
    for i in range(no_size_args):
        args[i] = args[i] * r_factor


###
##  GET OBJECTS
#

def get_objects(ranges, curr_ranges, prmii, fixed, dbg_context, r_factor):
    out = []
    height = 0
    for prms in prmii:
        check_args(prms, dbg_context)
        obj = get_object(ranges, curr_ranges, prms, fixed, dbg_context,
                         r_factor)
        if not obj:
            continue
        out.append(obj)
        if height == 0:
            height = get_height(prms) + prms.r
    return out, height


def get_object(ranges, curr_ranges, prms, fixed, dbg_context, r_factor):
    """prms = ObjParams(shape, r, fi, args, color)"""
    if prms.shape in [Shape.border, Shape.shifted_border]:
        return get_svg_el(prms, dbg_context, r_factor)
    if not fixed:
        fix_height(ranges, prms)
    if range_occupied(curr_ranges, prms):
        return None
    update_ranges(ranges, curr_ranges, prms)
    return get_svg_el(prms, dbg_context, r_factor)


###
##  FIX HEIGHT
#

def fix_height(ranges, prms):
    """prms = ObjParams(shape, r, fi, args, color)"""
    height = get_height(prms)
    max_height = get_max_height(ranges, prms)
    if abs(height) > abs(max_height):
        update_height(prms.shape, prms.args, max_height)


def get_max_height(all_ranges, prms):
    """prms = ObjParams(shape, r, fi, args, color)"""
    if len(all_ranges) <= 1:
        return 100
    for grp_ranges in reversed(all_ranges[:-1]):
        r, ranges = grp_ranges
        width = get_angular_width(prms.shape, prms.args, r)
        if pos_occupied(prms.fi, width, ranges):
            return calculate_max_height(prms, r)
    return 100


def calculate_max_height(prms, r):
    """prms = ObjParams(shape, r, fi, args, color)"""
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


###
##  GET SVG EL
#

def get_svg_el(prms, dbg_context, r_factor):
    """prms = ObjParams(shape, r, fi, args, color)"""
    height = get_height(prms)
    if height == 0:
        return ''
    if height < 0:
        prms = transpose_el_with_neg_height(prms)
    rad = get_rad(prms.fi)
    prms_rad = ObjParams(prms.shape, prms.r, rad, prms.args, prms.color)
    if prms.shape != Shape.face:
        if INVERT_COLOR:
            prms_rad = invert_color(prms_rad)
        return get_shape(prms_rad, dbg_context)
    return get_subface(prms_rad, r_factor)


def invert_color(prms):
    new_color = prms.color
    if prms.color in ('black', 'white', ''):
        new_color = 'black' if prms.color == 'white' else 'white'
    return ObjParams(prms.shape, prms.r, prms.fi, prms.args, new_color)


def transpose_el_with_neg_height(prms):
    """prms = ObjParams(shape, r, fi, args, color)"""
    height = get_height(prms)
    args = prms.args
    args[0] = -args[0]
    return ObjParams(prms.shape, prms.r - height, prms.fi, args, prms.color)


def get_subface(prms, r_factor):
    """prms = ObjParams(shape, r, fi, args, color)"""
    face_str = str(prms.args[1])
    size = prms.args[0]
    r_factor_sub = 1 if r_factor == 1 else 200/(size/r_factor)
    svg = get_watch(face_str, r_factor_sub)
    p = get_point(prms.fi, prms.r - size/2)
    scale = size / 200
    fill_color = 'black' if INVERT_COLOR else 'white'
    bckg = f'<circle cx={p.x} cy={p.y} r={size/2+VER_BORDER} ' \
        f'style="stroke-width:0; fill: {fill_color};"></circle>'
    return f'{bckg}<g transform="translate({p.x}, {p.y}), scale({scale})">' \
        f'{svg}</g>'


###
##  UTIL
#

def get_height(prms):
    """prms = ObjParams(shape, r, fi, args, color)"""
    return prms.shape.get_height(prms.args)


if __name__ == '__main__':
    main()
