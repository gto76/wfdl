from collections import namedtuple
from math import cos, sin, pi
from numbers import Real
from enum import Enum, auto

from util import get_enum


class NumberKind(Enum):
    hour = auto(), lambda deg: get_hour(deg)
    minute = auto(), lambda deg: get_minute(deg)
    roman = auto(), lambda deg: ROMAN[get_hour(deg)]
    day = auto(), lambda deg: DAYS[get_day(deg)]
    month = auto(), lambda deg: MONTHS[get_month(deg)]


class NumberOrientation(Enum):
    half_rotating = auto(), lambda deg: get_fi_half_rotating(deg)
    horizontal = auto(), lambda deg: 0
    rotating = auto(), lambda deg: get_fi_rotating(deg)


ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IIII', 5: 'V', 6: 'VI', 7: 'VII',
         8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'}
DAYS = {1: "MON", 2: "TUE", 3: "WED", 4: "THU", 5: "FRI", 6: "SAT", 7: "SUN"}
MONTHS = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL",
          8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}


def get_shape(prms, dbg_context):
    fun_name = f'get_{prms.shape.name}'
    fun = globals()[fun_name]
    return fun(prms, dbg_context)


def get_border(prms, dbg_context):
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


def get_line(prms, dbg_context):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height, width = prms.args
    x1 = cos(prms.fi) * prms.r
    x2 = cos(prms.fi) * (prms.r - height)
    y1 = sin(prms.fi) * prms.r
    y2 = sin(prms.fi) * (prms.r - height)
    return _get_line(x1, y1, x2, y2, width)


def get_date(prms, dbg_context):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args', 'color'])"""
    bckg = get_line(prms, dbg_context)
    height, width = prms.args
    txt_size = width - 3
    Prms = namedtuple('Prms', ['shape', 'r', 'fi', 'args', 'color'])
    prms = Prms(prms.shape, prms.r - height / 2 + txt_size / 2, prms.fi,
                [txt_size, 31, "horizontal"], "white")
    txt = get_number(prms, dbg_context)
    return bckg + txt


def get_rounded_line(prms, dbg_context):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height, width = prms.args
    rot = (prms.fi - pi / 2) / pi * 180
    return f'<rect rx="{width/2}" y="{prms.r-height}" x="-{width/2}" ry=' \
           f'"{width/2}" transform="rotate({rot})" height="{abs(height)}" ' \
           f'width="{width}"></rect>'


def get_two_lines(prms, dbg_context):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height, width, sep = prms.args
    x1 = cos(prms.fi) * (prms.r - height)
    x2 = cos(prms.fi) * prms.r
    y1 = sin(prms.fi) * (prms.r - height)
    y2 = sin(prms.fi) * prms.r
    factor = width / 2 * (1 + sep)
    dx = sin(prms.fi) * factor
    dy = cos(prms.fi) * factor
    return _get_line(x1 + dx, y1 + dy, x2 + dx, y2 + dy, width) + \
           _get_line(x1 - dx, y1 - dy, x2 - dx, y2 - dy, width)


def get_circle(prms, dbg_context):
    diameter = prms.args[0]
    cx = cos(prms.fi) * (prms.r - diameter / 2)
    cy = sin(prms.fi) * (prms.r - diameter / 2)
    return f'<circle cx={cx} cy={cy} r={abs(diameter) / 2} style=' \
           f'"stroke-width: 0; fill: rgb(0, 0, 0);"></circle>'


def get_triangle(prms, dbg_context):
    height, width = prms.args
    x1 = (cos(prms.fi) * prms.r) - (sin(prms.fi) * width / 2)
    y1 = (sin(prms.fi) * prms.r) + (cos(prms.fi) * width / 2)
    x2 = (cos(prms.fi) * prms.r) + (sin(prms.fi) * width / 2)
    y2 = (sin(prms.fi) * prms.r) - (cos(prms.fi) * width / 2)
    x3 = cos(prms.fi) * (prms.r - height)
    y3 = sin(prms.fi) * (prms.r - height)
    return f'<polygon points="{x1},{y1} {x2},{y2} {x3},{y3}" />'


def get_upside_triangle(prms, dbg_context):
    height, width = prms.args
    x1 = cos(prms.fi) * prms.r
    y1 = sin(prms.fi) * prms.r
    r2 = prms.r - height
    x2 = (cos(prms.fi) * r2) - (sin(prms.fi) * width / 2)
    y2 = (sin(prms.fi) * r2) + (cos(prms.fi) * width / 2)
    x3 = (cos(prms.fi) * r2) + (sin(prms.fi) * width / 2)
    y3 = (sin(prms.fi) * r2) - (cos(prms.fi) * width / 2)
    return f'<polygon points="{x1},{y1} {x2},{y2} {x3},{y3}" />'


def get_number(prms, dbg_context):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    orient = ''
    font = 'arial'
    weight = ''
    if len(prms.args) == 2:
        size, kind = prms.args
    elif len(prms.args) == 3:
        size, kind, orient = prms.args
    elif len(prms.args) == 4:
        size, kind, orient, font = prms.args
    else:
        size, kind, orient, font, weight = prms.args
    x = cos(prms.fi) * (prms.r - size / 2)
    y = sin(prms.fi) * (prms.r - size / 2)
    i = get_num_str(kind, prms.fi, dbg_context)
    orient_tokens = orient.split()
    if len(orient_tokens) == 2 and orient_tokens[1] == 'bent':
        return _get_bent_num(size, kind, orient_tokens[1], font, weight, x, y,
                             i)
    rot = get_num_rotation(orient, prms.fi, dbg_context)
    fact = 6
    return f'<g transform="translate({x}, {y})"><text transform="rotate({rot}' \
           f'), translate(0, {size/fact})" class="title" fill="{prms.color}" ' \
           f'fill-opacity="1" font-size="{size*(1+1.0/fact*2)}" ' \
           f'font-weight="{weight}" font-family="{font}" ' \
           f'alignment-baseline="middle" text-anchor="middle">{i}</text></g>'


def _get_bent_num(size, kind, orient, font, weight, x, y, i):
    pass


def get_square(prms, dbg_context):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height = prms.args[0]
    ObjParams = namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])
    prms = ObjParams(prms.shape, prms.r, prms.fi, [height, height])
    return get_line(prms, dbg_context)


def get_octagon(prms, dbg_context):
    height, width, sides_factor = prms.args


def get_arrow(prms, dbg_context):
    height, width, angle = prms.args


def get_rhombus(prms, dbg_context):
    height, width = prms.args


def get_trapeze(prms, dbg_context):
    height, width, width_2 = prms.args


def get_tear(prms, dbg_context):
    height, width = prms.args


def get_spear(prms, dbg_context):
    height, width, center = prms.args


###
##  UTIL
#

def _get_line(x1, y1, x2, y2, width):
    return f'<line x1={x1} y1={y1} x2={x2} y2={y2} style="stroke-width:' \
           f'{width}; stroke:#000000"></line>'


def get_num_str(kind_name, deg, dbg_context):
    if isinstance(kind_name, Real):
        return deg_to_time(deg, kind_name)
    if isinstance(kind_name, list):
        i = deg_to_time(deg, len(kind_name))
        return kind_name[i - 1]
    kind = NumberKind.hour
    if kind_name:
        kind = get_enum(NumberKind, kind_name, dbg_context)
    converter = kind.value[1]
    return converter(deg)


def get_minute(deg):
    return deg_to_time(deg, 60)


def get_hour(deg):
    return deg_to_time(deg, 12)


def get_day(deg):
    return deg_to_time(deg, 7)


def get_month(deg):
    return deg_to_time(deg, 12)


def deg_to_time(deg, factor):
    i = (deg + pi / 2) / (2 * pi) * factor
    if factor < 0:
        i = abs(factor) + i
    i = round(i)
    if i == 0:
        i = factor
    return i


def get_num_rotation(orient_name, deg, dbg_context):
    orient = NumberOrientation.half_rotating
    if orient_name:
        orient = get_enum(NumberOrientation, orient_name, dbg_context)
    converter = orient.value[1]
    return converter(deg)


def get_fi_half_rotating(deg):
    return (deg + pi / 2 + (pi if 0 < deg < pi else 0)) / pi * 180


def get_fi_rotating(deg):
    return (deg + pi / 2) / pi * 180
