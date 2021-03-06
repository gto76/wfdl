from itertools import chain
from math import ceil, isclose, log10
from numbers import Real


def get_fii(pos):
    if isinstance(pos, set):
        return get_fii_set(pos)
    elif isinstance(pos, Real):
        return get_fii_real(pos)
    elif isinstance(pos, dict):
        return get_fii_dict(pos)
    elif isinstance(pos, list):
        return get_fii_list(pos)


def get_fii_set(nums):
    out = set()
    for a in nums:
        if a < 0:
            a += 1
        out.add(a)
    return out


def get_fii_real(pos):
    return [(i/pos) for i in range(ceil(pos))]


# def get_fii_dict(pos):
#     if 'tachy' in pos:
#         return get_tachy(pos)
#     if 'log' in pos:
#         return get_log(pos)
#     position = pos['pos']
#     if 'offset' in pos:
#         offset = pos['offset']
#         out = get_fii(position)
#         return [a+offset for a in out]
#     return get_fii(position)


def get_fii_dict(pos):
    offset = pos.get('offset', 0)
    if 'tachy' in pos:
        out = get_tachy(pos)
    elif 'log' in pos:
        out = get_log(pos)
    else:
        out = get_fii(pos['pos'])
    return [normalize_fi(a + offset) for a in out]


def get_tachy(pos):
    locations = pos['tachy']
    if type(locations) == list:
        locations = list_to_range(locations)
    return [(60 / a) for a in locations]


def get_log(pos):
    locations = pos['log']
    if type(locations) == list:
        locations = list_to_range(locations)
    offset = 1 - log10(6)
    return [(log10(a) - 1 + offset) for a in locations]


def list_to_range(a_list):
    out = parse_sets(a_list)
    a_len = len(a_list)
    if a_len < 2:
        raise ValueError(f'Wrong number of arguments in locations list: '
                         f'{a_list}')
    if a_len == 2:
        start, end = a_list
        return chain(out, range(start, end+1))
    elif a_len == 3:
        start, end, step = a_list
        return chain(out, range(start, end+1, step))
    elif a_len > 3:
        start, end, step = a_list[0], a_list[1], a_list[2]
        out = chain(out, range(start, end+1, step))
        no_pairs = (a_len - 3) / 2
        if no_pairs % 1 != 0:
            raise ValueError(f'Wrong number of arguments in locations list: '
                             f'{a_list}')
        for i in range(int(no_pairs)):
            new_end, step = a_list[3 + 2*i], a_list[4 + 2*i]
            tmp_range = range(end+step, new_end+1, step)
            end = new_end
            out = chain(out, tmp_range)
        return out


def parse_sets(a_list):
    out = []
    set_indexes = [a_list.index(a) for a in a_list if type(a) == set]
    for i in set_indexes:
        a_set = a_list.pop(i)
        out.extend(a_set)
    return out


def get_range(locations):
    start, end, step = locations.get('start'), locations.get('end'), \
                       locations.get('step', 1)
    return range(start, end + 1, step)


def get_fii_list(pos):
    n = pos[0]
    start = 0
    if len(pos) == 2:
        end = pos[1]
    else:
        start = pos[1]
        end = pos[2]
    return [i/n for i in range(n+1) if is_between(i/n, start, end)]


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
    # Old and always false:
    # if -1 >= fi >= 1:
    if -1 >= fi or fi >= 1:
        fi %= 1
    if fi < 0:
        fi += 1
    return fi
