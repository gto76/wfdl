#!/usr/bin/python3
#
# Usage: parse.py 
# 

import math
import sys
import re

BASE = 0.75
HEAD = '<html>\n<svg height=300px width=300px>\n<g transform="translate(150, 150), scale({})")>\n'.format(BASE)
TAIL = "\n</g>\n</svg>\n</html>"

ELEMENTS = [100, [0, 12, 1], [10, 60, 1], [5, 120, 1]]
ELEMENTS_B = [90, [30, 12, 5]]

def main():
    out = HEAD
    out += get_group(ELEMENTS)
    out += get_group(ELEMENTS_B)
    print(out+TAIL)


def get_group(elements):
    if len(elements) < 2:
        return
    out = ""
    filled_positions = set()
    offset = elements[0]
    elements = elements[1:]
    for element in elements:
        length = element[0]
        n = element[1]
        width = element[2]
        positions = get_positions(n)
        positions = positions.difference(filled_positions)
        out += get_circle(positions, offset, offset-length, width)
        filled_positions.update(positions)
    return out


def get_positions(n):
    return set([i/n for i in range(n)])


def get_circle(positions, ro, ri, width):
    out = ""
    for position in positions:
        deg = position * 2*math.pi
        out += get_line(deg, ri, ro, width)
    return out 


def get_line(deg, ri, ro, width):
    x1 = math.cos(deg) * ri
    x2 = math.cos(deg) * ro
    y1 = math.sin(deg) * ri
    y2 = math.sin(deg) * ro
    return '<line x1={} y1={} x2={} y2={} style="stroke-width:{}; ' \
           'stroke:#000000"></line>'.format(x1, y1, x2, y2, width)


if __name__ == '__main__':
    main()
