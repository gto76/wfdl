#!/usr/bin/python3
#
# Usage: parse.py 
# 

import math
import sys
import re

base = 50
aaa = [[0, 12], [10, 60], [5, 120]]

def main():
    out = ""
    filled_positions = set()
    for a in aaa:
        length = a[0]
        n = a[1]
        positions = get_positions(n)
        positions = positions.difference(filled_positions)
        out += get_circle(positions, base, base+length)
        filled_positions.update(positions)
    print(out)



def get_positions(n):
    return set([i/n for i in range(n)])



def get_circle(positions, ri, ro):
    out = ""
    for position in positions:
        deg = position * 2*math.pi
        out += get_line(deg, ri, ro)
    return out 


def get_line(deg, ro, ri):
    x1 = math.cos(deg) * ri
    x2 = math.cos(deg) * ro
    y1 = math.sin(deg) * ri
    y2 = math.sin(deg) * ro
    return '<line x1={} y1={} x2={} y2={} style="stroke-width:1; stroke:#000000"></line>'.format(x1, y1, x2,y2)


if __name__ == '__main__':
    main()
