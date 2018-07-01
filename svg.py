from math import cos, sin, pi


ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IIII', 5: 'V', 6: 'VI', 7: 'VII',
         8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'}


def get_line(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height, width = prms.args
    x1 = cos(prms.fi) * prms.r
    x2 = cos(prms.fi) * (prms.r - height)
    y1 = sin(prms.fi) * prms.r
    y2 = sin(prms.fi) * (prms.r - height)
    return _get_line(x1, y1, x2, y2, width)


def get_rounded_line(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height, width = prms.args
    rot = (prms.fi - pi / 2) / pi * 180
    return f'<rect rx="{width/2}" y="{prms.r}" x="-{width/2}" ry="{width/2}" ' \
           f'transform="rotate({rot})" height="{height}" width="{width}">' \
           '</rect>'


def get_two_lines(prms):
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


def get_circle(prms):
    diameter = prms.args[0]
    cx = cos(prms.fi) * (prms.r - diameter / 2)
    cy = sin(prms.fi) * (prms.r - diameter / 2)
    return f'<circle cx={cx} cy={cy} r={diameter / 2} style="stroke-width: 0;' \
           ' fill: rgb(0, 0, 0);"></circle>'


def get_triangle(prms):
    height, width = prms.args
    x1 = (cos(prms.fi) * prms.r) - (sin(prms.fi) * width / 2)
    y1 = (sin(prms.fi) * prms.r) + (cos(prms.fi) * width / 2)
    x2 = (cos(prms.fi) * prms.r) + (sin(prms.fi) * width / 2)
    y2 = (sin(prms.fi) * prms.r) - (cos(prms.fi) * width / 2)
    x3 = cos(prms.fi) * (prms.r - height)
    y3 = sin(prms.fi) * (prms.r - height)
    return f'<polygon points="{x1},{y1} {x2},{y2} {x3},{y3}" />'


def get_number(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    font = ''
    if len(prms.args) == 3:
        size, kind, orient = prms.args
    else:
        size, kind, orient, font = prms.args
    x = cos(prms.fi) * (prms.r - size / 2)
    y = sin(prms.fi) * (prms.r - size / 2)
    i = get_num_str(kind, prms.fi)
    rot = get_num_rotation(orient, prms.fi)
    return f'<g transform="translate({x}, {y})"><text transform="rotate({rot}' \
           f')" class="title" fill="#111111" fill-opacity="0.9" font-size=' \
           f'"{size}" font-weight="bold" font-family="{font}" ' \
           f'alignment-baseline="middle" text-anchor="middle">{i}</text></g>'


def get_upside_triangle(prms):
    height, width = prms.args


def get_square(prms):
    height = prms.args[0]

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



def get_octagon(prms):
    height, width, sides_factor = prms.args


def get_arrow(prms):
    height, width, angle = prms.args


def get_rhombus(prms):
    height, width = prms.args


def get_trapeze(prms):
    height, width, width_2 = prms.args


def get_tear(prms):
    height, width = prms.args


def get_spear(prms):
    height, width, center = prms.args


###
##  UTIL
#

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
