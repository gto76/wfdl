from collections import namedtuple
from math import cos, sin, pi, degrees, atan, sqrt
from numbers import Real
from enum import Enum, auto
from random import random

from shape import Shape
from util import get_enum, check_args, get_cent, get_point, get_point_xy, \
    add_defaults


NUM_FACT = 6
BENT_DELTA = 0.1


class NumKind(Enum):
    """Second element is converter function from fi of numbers position to
    string with the number."""
    hour = auto(), lambda fi: get_hour(fi)
    hour_24 = auto(), lambda fi: get_hour(fi) + 12
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
    perpendicular = auto(), lambda fi: get_fi_perpendicular(fi)


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
    return _get_text(text=i, point=p, size=args.size, rotation=rot,
                     color=prms.color, weight=args.weight, font=args.font)
    # return f'<g transform="translate({p.x}, {p.y})"><text ' \
    #        f'transform="rotate({rot}), translate(0, {args.size/NUM_FACT})" ' \
    #        f'class="title" fill="{prms.color}" fill-opacity="1" ' \
    #        f'font-size="{get_num_size(args.size)}" ' \
    #        f'font-weight="{args.weight}" font-family="{args.font}" ' \
    #        f'alignment-baseline="middle" text-anchor="middle">{i}</text></g>'


def _get_text(text, point, size, rotation, color, weight, font):
    return f'<g transform="translate({point.x}, {point.y})"><text ' \
           f'transform="rotate({rotation}), translate(0, {size/NUM_FACT})" ' \
           f'class="title" fill="{color}" fill-opacity="1" ' \
           f'font-size="{get_num_size(size)}" ' \
           f'font-weight="{weight}" font-family="{font}" ' \
           f'alignment-baseline="middle" text-anchor="middle">{text}</text></g>'


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
        f'fill = "{prms.color}" ' \
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
    size, kind, orient, font, weight, bent = \
        add_defaults(prms.args, [None, 'hour', '', 'arial', '', False])
    NumArgs = namedtuple('NumArgs', ['size', 'kind', 'orient', 'font', 'weight',
                                     'bent'])
    return NumArgs(size, kind, get_orient(orient), font, weight, bent)


def get_num_size(size):
    return size*(1 + 1.0 / NUM_FACT*2)


def get_border(prms):
    return _get_border(prms)


def get_shifted_border(prms):
    return _get_border(prms, True)


def _get_border(prms, shifted=False):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args', 'color'])"""
    height = prms.args[0]
    r = prms.r - height / 2
    fi = 1 if len(prms.args) < 2 else prms.args[1]
    if fi >= 1:
        return _get_circle(r, height, prms.color)
    arc_sweep = 0 if fi < 0.5 else 1
    rng = fi * 2 * pi / 2
    d = describe_arc(0, 0, r, prms.fi, prms.fi + 2*rng, arc_sweep) if shifted \
        else describe_arc(0, 0, r, prms.fi - rng, prms.fi + rng, arc_sweep)
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
    return _get_line(p1.x, p1.y, p2.x, p2.y, width, prms.color)


def get_date(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args', 'color'])"""
    bckg = get_line(prms)
    height, width = prms.args
    if prms.fi in [0, pi]:
        txt_size = height - 2
    else:
        txt_size = width - 6

    color = 'white' if prms.color == 'black' else 'black'
    Prms = namedtuple('Prms', ['shape', 'r', 'fi', 'args', 'color'])
    prms = Prms(Shape.number, prms.r - height / 2 + txt_size / 2, prms.fi,
                [txt_size, '27', 'horizontal'], color)
    txt = get_number(prms)
    return bckg + txt


def get_lange_date(prms):
    height = prms.args[0]
    width = height * (122/74)
    line_width = height * (8/74)
    text_size = height * (46/74)
    surface = _get_line(-width/2, 0, width/2, 0, height, 'white')
    line_1 = _get_line(-width/2, (-height/2)+line_width/2, width/2, (-height/2)+line_width/2, line_width, 'black')
    line_2 = _get_line(-width/2, (height/2)-line_width/2, width/2, (height/2)-line_width/2, line_width, 'black')
    line_3 = _get_line(-width/2+line_width/2, -height/2, -width/2+line_width/2, height/2, line_width, 'black')
    line_4 = _get_line(0, -height/2, 0, height/2, line_width, 'black')
    line_5 = _get_line(width/2-line_width/2, -height/2, width/2-line_width/2, height/2, line_width, 'black')
    pos = get_point(prms.fi, prms.r - height / 2)



    return f'<g transform="translate({pos.x}, {pos.y})">{surface}{line_1}{line_2}{line_3}{line_4}{line_5}</g>'


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
    return _get_line(p1.x + dx, p1.y + dy, p2.x + dx, p2.y + dy, width
                     , prms.color) + \
        _get_line(p1.x - dx, p1.y - dy, p2.x - dx, p2.y - dy, width
                  , prms.color)


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
    Prms = namedtuple('Prms', ['shape', 'r', 'fi', 'args', 'color'])
    prms = Prms(Shape.line, prms.r, prms.fi, [height, height], prms.color)
    return get_line(prms)


def get_moonphase(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    stroke_width = 1.7
    height, r1, r2, r3, r4 = get_moonphase_args(prms)
    pos = get_point(prms.fi, prms.r-height/2)

    t1 = _get_triangle(r3+r1, r1+r2, r2+r3)
    p1_a = _get_point(t1)
    t2 = _get_triangle(r3+r1, r4-r1, r2+r3)
    p1_b = _get_point(t2)

    arc_1_a = describe_arc(p1_a.x, -p1_a.y, r1, t1.fi_b, -pi-t1.fi_a, 0)
    arc_1_b = describe_arc(p1_b.x, -p1_b.y, r1, -t2.fi_a, t2.fi_b, 0)
    arc_1_c = describe_arc(-p1_a.x, -p1_a.y, r1, t1.fi_a, -pi-t1.fi_b, 0)
    arc_1_d = describe_arc(-p1_b.x, -p1_b.y, r1, pi-t2.fi_b, pi+t2.fi_a, 0)
    arc_2 = describe_arc(0, 0, r2, -pi+t1.fi_a, -t1.fi_a, 0)
    arc_3_a = describe_arc(r2+r3, 0, r3, -pi+t1.fi_b, -pi+t2.fi_b, 0)
    arc_3_b = describe_arc(-(r2+r3), 0, r3, -t2.fi_b, -t1.fi_b, 0)
    arc_4 = describe_arc(0, 0, r4, -pi+t2.fi_a, -t2.fi_a, 0)

    arc = arc_1_a + arc_1_b + arc_1_c + arc_1_d + arc_2 + arc_3_a + arc_3_b + \
          arc_4
    return f'<g transform="translate({pos.x}, {pos.y}), scale({height/100})" ' \
           f'stroke="{prms.color}" fill="none" stroke-width="{stroke_width}">' \
           f'<path d="{arc}"/></g>'


def get_moonphase_args(prms):
    args = prms.args
    r1, r2, r3, r4 = 5 * (100 / 115), 20 * (100 / 115), 47.5 * (100 / 115), 100
    if len(args) == 1:
        height = args[0]
    else:
        height, r1, r2, r3 = args
    return height, r1, r2, r3, r4


def _get_point(t):
    y = t.a * sin(t.fi_b)
    x = sqrt(t.b**2 - y**2)
    return get_point_xy(x, y)


def _get_triangle(a, b, c):
    fi_a, fi_b, fi_c = _get_angles(a, b, c)
    Triangle = namedtuple('Triangle', ['a', 'b', 'c', 'fi_a', 'fi_b', 'fi_c'])
    return Triangle(a, b, c, fi_a, fi_b, fi_c)


def _get_angles(a, b, c):
    z_alpha = (a ** 2 - (b - c) ** 2) / ((b + c) ** 2 - a ** 2)
    z_beta = (b ** 2 - (c - a) ** 2) / ((c + a) ** 2 - b ** 2)
    z_delta = (c ** 2 - (a - b) ** 2) / ((a + b) ** 2 - c ** 2)
    return 2*atan(sqrt(z_alpha)), 2*atan(sqrt(z_beta)), 2*atan(sqrt(z_delta))


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


def _get_line(x1, y1, x2, y2, width, color):
    return f'<line x1={x1} y1={y1} x2={x2} y2={y2} style="stroke-width:' \
           f'{width}" stroke="{color}"></line>'


def get_num_str(kind_el, deg):
    use_zero = False
    countdown = False
    if isinstance(kind_el, dict):
        kind = kind_el['kind']
        use_zero = kind_el.get('use_zero', False)
        if use_zero in ['True', 'true']:
            use_zero = True
        countdown = kind_el.get('countdown', False)
        if countdown in ['True', 'true']:
            countdown = True
        offset = kind_el.get('offset', 0) * 2 * pi
        deg += offset
        kind_el = kind
    return _get_num_str(kind_el, deg, use_zero, countdown)


def _get_num_str(kind_el, deg, use_zero=False, countdown=False):
    if isinstance(kind_el, Real):
        out = fi_to_time(deg, kind_el, use_zero)
    elif isinstance(kind_el, list):
        i = fi_to_time(deg, len(kind_el), use_zero)
        out = kind_el[i - 1]
    elif kind_el and kind_el not in [a.name for a in NumKind]:
        out = kind_el
    else:
        kind = NumKind.hour
        if kind_el:
            kind = get_enum(NumKind, kind_el, dbg_context)
        converter = kind.value[1]
        out = converter(deg)
    if countdown and out:
        out = f'-{out}'
    return out


def get_minute(fi):
    return fi_to_time(fi, 60)


def get_hour(fi):
    return fi_to_time(fi, 12)


def get_day(fi):
    return fi_to_time(fi, 7, whole_nums=True)


def get_month(fi):
    return fi_to_time(fi, 12)


def get_tachy(fi):
    return int(60 / get_cent(fi))


def fi_to_time(fi, factor, use_zero=False, whole_nums=False):
    fi_cents = (fi + pi / 2) / (2 * pi)
    if fi_cents > 1:
        fi_cents %= 1
    i = fi_cents * factor
    if factor < 0:
        i = abs(factor) + i
    if whole_nums:
        i = round(i)
    else:
        i = round(i*10)/10
    if i % 1 == 0:
        i = round(i)
    if i < 0:
        i += abs(factor)
    if i == 0 and not use_zero:
        i = abs(factor)
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


def get_fi_perpendicular(fi):
    rad = fi if fi <= pi/2 else fi+pi
    return degrees(rad)
