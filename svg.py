from collections import namedtuple
from math import cos, sin, pi
from numbers import Real
from enum import Enum, auto
from random import random

from shape import Shape
from util import get_enum, check_args, get_cent, get_point


NUM_FACT = 6
BENT_DELTA = 0.1


class NumKind(Enum):
    """Second element is converter function from fi of numbers position to
    string with the number."""
    hour = auto(), lambda fi: get_hour(fi)
    minute = auto(), lambda fi: get_minute(fi)
    roman = auto(), lambda fi: ROMAN[get_hour(fi)]
    day = auto(), lambda fi: DAYS[get_day(fi)]
    month = auto(), lambda fi: MONTHS[get_month(fi)]
    tachy = auto(), lambda fi: get_tachy(fi)


class NumOrient(Enum):
    """Second element is converter function from fi of numbers position to
    fi of it's rotation."""
    half_rotating = auto(), lambda fi: get_fi_half_rotating(fi)
    horizontal = auto(), lambda fi: 0
    rotating = auto(), lambda fi: get_fi_rotating(fi)


ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IIII', 5: 'V', 6: 'VI', 7: 'VII',
         8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'}
DAYS = {1: "MON", 2: "TUE", 3: "WED", 4: "THU", 5: "FRI", 6: "SAT", 7: "SUN"}
MONTHS = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL",
          8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}

# Subgroup string used for error messages.
dbg_context = None


def get_shape(prms, _dbg_context):
    global dbg_context
    dbg_context = _dbg_context
    check_args(prms, dbg_context)
    fun_name = f'get_{prms.shape.name}'
    fun = globals()[fun_name]
    return fun(prms)


def get_number(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    # namedtuple('NumArgs', ['size', 'kind', 'orient', 'font', 'weight','bent'])
    args = get_num_args(prms)
    r = prms.r - args.size / 2
    p = get_point(prms.fi, r)
    i = get_num_str(args.kind, prms.fi)
    rot = get_num_rotation(args.orient, prms.fi)
    return f'<g transform="translate({p.x}, {p.y})"><text ' \
           f'transform="rotate({rot}), translate(0, {args.size/NUM_FACT})" ' \
           f'class="title" fill="{prms.color}" fill-opacity="1" ' \
           f'font-size="{get_num_size(args.size)}" ' \
           f'font-weight="{args.weight}" font-family="{args.font}" ' \
           f'alignment-baseline="middle" text-anchor="middle">{i}</text></g>'


def get_bent_number(prms):
    args = get_num_args(prms)
    if args.orient == NumOrient.horizontal:
        return get_number(prms)
    return get_bent_rotated(prms, args)


def get_bent_rotated(prms, args):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])
    namedtuple('NumArgs', ['size', 'kind', 'orient', 'font', 'weight',
    'bent'])"""
    r, delta, sweep = get_bent_prms(prms, args)
    fi = prms.fi + pi
    p1 = get_point(fi + delta, r)
    p2 = get_point(fi - delta, r)
    i = get_num_str(args.kind, prms.fi)
    a_id = f'path{i}{fi}{r}{random()}'
    path = f'M {p1.x} {p1.y} A {r} {r} 0 1 {sweep} {p2.x} {p2.y}'
    # ruler = f'<path d="{path}" fill="rgba(0,0,0,0)" stroke="#ddd"/>'
    return '<defs>' \
        f'<path id="{a_id}" d="{path}"/></defs>' \
        f'<text font-size="{get_num_size(args.size)}" ' \
        f'font-family="{args.font}">' \
        f'<textPath xlink:href="#{a_id}" startOffset="50%" ' \
        f'text-anchor="middle">{i}</textPath>' \
        '</text>'


def get_bent_prms(prms, args):
    bottom_half = 0 < prms.fi < pi
    if args.orient == NumOrient.half_rotating and bottom_half:
        return prms.r, -BENT_DELTA, 0
    return prms.r - args.size, BENT_DELTA, 1


def get_num_args(prms):
    args = prms.args
    orient, font, weight, bent = '', 'arial', '', False
    if len(args) == 2:
        size, kind = args
    elif len(args) == 3:
        size, kind, orient = args
    elif len(args) == 4:
        size, kind, orient, font = args
    else:
        size, kind, orient, font, weight = args
    orient = get_orient(orient)
    NumArgs = namedtuple('NumArgs', ['size', 'kind', 'orient', 'font', 'weight',
                                     'bent'])
    return NumArgs(size, kind, orient, font, weight, bent)


def get_num_size(size):
    return size*(1 + 1.0 / NUM_FACT*2)


def get_border(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args', 'color'])"""
    height = prms.args[0]
    r = prms.r - height / 2
    fi = 1 if len(prms.args) < 2 else prms.args[1]
    if fi >= 1:
        return _get_circle(r, height, prms.color)
    arc_sweep = 0 if fi < 0.5 else 1
    rng = fi * 2 * pi / 2
    d = describe_arc(0, 0, r, prms.fi - rng, prms.fi + rng, arc_sweep)
    return f'<g stroke="{prms.color}" fill="none" stroke-width="{height}">' \
           f'<path d="{d}"/></g>'


def _get_circle(r, height, color):
    return f'<circle cx=0 cy=0 r={r} style="stroke-width: {height};' \
           f' stroke: {color}; fill: rgba(0, 0, 0, 0);"></circle>'


def get_line(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height, width = prms.args
    p1 = get_point(prms.fi, prms.r)
    p2 = get_point(prms.fi, prms.r - height)
    return _get_line(p1.x, p1.y, p2.x, p2.y, width)


def get_date(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args', 'color'])"""
    bckg = get_line(prms)
    height, width = prms.args
    txt_size = width - 3
    Prms = namedtuple('Prms', ['shape', 'r', 'fi', 'args', 'color'])
    prms = Prms(Shape.number, prms.r - height / 2 + txt_size / 2, prms.fi,
                [txt_size, "27", "horizontal"], "white")
    txt = get_number(prms)
    return bckg + txt


def get_rounded_line(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height, width = prms.args
    rot = (prms.fi - pi / 2) / pi * 180
    return f'<rect rx="{width/2}" y="{prms.r-height}" x="-{width/2}" ry=' \
           f'"{width/2}" transform="rotate({rot})" height="{abs(height)}" ' \
           f'width="{width}"></rect>'


def get_two_lines(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height, width, sep = prms.args
    p1 = get_point(prms.fi, prms.r - height)
    p2 = get_point(prms.fi, prms.r)
    factor = width / 2 * (1 + sep)
    dx = sin(prms.fi) * factor
    dy = cos(prms.fi) * factor
    return _get_line(p1.x + dx, p1.y + dy, p2.x + dx, p2.y + dy, width) + \
        _get_line(p1.x - dx, p1.y - dy, p2.x - dx, p2.y - dy, width)


def get_circle(prms):
    diameter = prms.args[0]
    p = get_point(prms.fi, prms.r - diameter / 2)
    return f'<circle cx={p.x} cy={p.y} r={abs(diameter) / 2} style=' \
           f'"stroke-width: 0; fill: rgb(0, 0, 0);"></circle>'


def get_triangle(prms):
    height, width = prms.args
    x1 = (cos(prms.fi) * prms.r) - (sin(prms.fi) * width / 2)
    y1 = (sin(prms.fi) * prms.r) + (cos(prms.fi) * width / 2)
    x2 = (cos(prms.fi) * prms.r) + (sin(prms.fi) * width / 2)
    y2 = (sin(prms.fi) * prms.r) - (cos(prms.fi) * width / 2)
    x3 = cos(prms.fi) * (prms.r - height)
    y3 = sin(prms.fi) * (prms.r - height)
    return f'<polygon points="{x1},{y1} {x2},{y2} {x3},{y3}" />'


def get_upside_triangle(prms):
    height, width = prms.args
    x1 = cos(prms.fi) * prms.r
    y1 = sin(prms.fi) * prms.r
    r2 = prms.r - height
    x2 = (cos(prms.fi) * r2) - (sin(prms.fi) * width / 2)
    y2 = (sin(prms.fi) * r2) + (cos(prms.fi) * width / 2)
    x3 = (cos(prms.fi) * r2) + (sin(prms.fi) * width / 2)
    y3 = (sin(prms.fi) * r2) - (cos(prms.fi) * width / 2)
    return f'<polygon points="{x1},{y1} {x2},{y2} {x3},{y3}" />'


def get_square(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height = prms.args[0]
    ObjParams = namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])
    prms = ObjParams(Shape.line, prms.r, prms.fi, [height, height])
    return get_line(prms)


# def get_octagon(prms, dbg_context):
#     check_args(prms, dbg_context)
#     height, width, sides_factor = prms.args
#
#
# def get_arrow(prms, dbg_context):
#     check_args(prms, dbg_context)
#     height, width, angle = prms.args
#
#
# def get_rhombus(prms, dbg_context):
#     check_args(prms, dbg_context)
#     height, width = prms.args
#
#
# def get_trapeze(prms, dbg_context):
#     check_args(prms, dbg_context)
#     height, width, width_2 = prms.args
#
#
# def get_tear(prms, dbg_context):
#     check_args(prms, dbg_context)
#     height, width = prms.args
#
#
# def get_spear(prms, dbg_context):
#     check_args(prms, dbg_context)
#     height, width, center = prms.args


###
##  UTIL
#

def describe_arc(x, y, r, start_fi, end_fi, arc_sweep):
    start = polar_to_cartesian(x, y, r, end_fi)
    end = polar_to_cartesian(x, y, r, start_fi)
    d = [
        'M', start.x, start.y,
        'A', r, r, 0, arc_sweep, 0, end.x, end.y
    ]
    return ' '.join(str(a) for a in d)


def polar_to_cartesian(center_x, center_y, radius, fi):
    Point = namedtuple('Point', list('xy'))
    x = center_x + (radius * cos(fi))
    y = center_y + (radius * sin(fi))
    return Point(x, y)


def _get_line(x1, y1, x2, y2, width):
    return f'<line x1={x1} y1={y1} x2={x2} y2={y2} style="stroke-width:' \
           f'{width}; stroke:#000000"></line>'


def get_num_str(kind_el, deg):
    if isinstance(kind_el, Real):
        return fi_to_time(deg, kind_el)
    if isinstance(kind_el, list):
        # if isinstance(kind_el[0], Real):
        # else:
        i = fi_to_time(deg, len(kind_el))
        return kind_el[i - 1]
    if isinstance(kind_el, dict):
        no_of_no = kind_el['kind']
        offset = kind_el['offset']
        offset = offset * 2 * pi
        out = fi_to_time(deg + offset, no_of_no)
        if out < 0:
            out += abs(no_of_no)
        return out
    if kind_el and kind_el not in [a.name for a in NumKind]:
        return kind_el
    kind = NumKind.hour
    if kind_el:
        kind = get_enum(NumKind, kind_el, dbg_context)
    converter = kind.value[1]
    return converter(deg)


def get_minute(fi):
    return fi_to_time(fi, 60)


def get_hour(fi):
    return fi_to_time(fi, 12)


def get_day(fi):
    return fi_to_time(fi, 7)


def get_month(fi):
    return fi_to_time(fi, 12)


def get_tachy(fi):
    return int(60 / get_cent(fi))


def fi_to_time(fi, factor):
    fi_cents = (fi + pi / 2) / (2 * pi)
    if fi_cents > 1:
        fi_cents %= 1
    i = fi_cents * factor
    if factor < 0:
        i = abs(factor) + i
    i = round(i*10)/10
    if i % 1 == 0:
        i = round(i)
    if i == 0:
        i = factor
    return i


def get_num_rotation(orient, deg):
    converter = orient.value[1]
    return converter(deg)


def get_orient(orient_name):
    orient = NumOrient.half_rotating
    if orient_name:
        orient = get_enum(NumOrient, orient_name, dbg_context)
    return orient


def get_fi_half_rotating(fi):
    return (fi + pi / 2 + (pi if 0 < fi < pi else 0)) / pi * 180


def get_fi_rotating(fi):
    return (fi + pi / 2) / pi * 180
