from collections import namedtuple
from math import asin, pi


BORDER_FACTOR = 0.1
Range = namedtuple('Range', ['start', 'end'])
GrpRanges = namedtuple('GrpRanges', ['r', 'ranges'])


def range_occupied(curr_ranges, prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    width = get_angular_width(prms.shape, prms.args, prms.r)
    return pos_occupied(prms.fi, width, curr_ranges)


def update_ranges(ranges, curr_ranges, prms):
    new_ranges = get_ranges_prms(prms)
    curr_ranges.extend(new_ranges)
    rng = get_range(ranges, prms)
    rng.extend(new_ranges)


def get_ranges_prms(prms):
    width = get_angular_width(prms.shape, prms.args, prms.r)
    return get_ranges(prms.fi, width)


def get_range(ranges, prms):
    for rng in reversed(ranges):
        if rng.r == prms.r:
            return rng.ranges
    out = []
    rng = GrpRanges(prms.r, out)
    ranges.append(rng)
    ranges.sort(key=lambda a: a.r)
    return out


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
