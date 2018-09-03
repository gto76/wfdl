from collections import namedtuple
from enum import Enum


Properties = namedtuple('Properties', ['get_height', 'get_width', 'min_no_args',
                                       'max_args', 'no_size_args'])


class Shape(Enum):
    """First property is the height formula.
    Second the is width formula.
    Third has number of required arguments.
    Fourth the maximum sizes of the arguments.
    Fifth defines number of arguments that determine size."""

    number = Properties(lambda a: a[0], lambda a: a[0] * 1.34, None, None, 1)      # height, kind (minute, roman,
    # hour), orient (horizontal, rotating, half_rotating) [, font]
    bent_number = Properties(lambda a: a[0], lambda a: a[0] * 1.34, None, None, 1) # height, kind (minute, roman,
    # hour), orient (horizontal, rotating, half_rotating) [, font]
    face = Properties(lambda a: a[0], lambda a: a[0], None, None, 1)               # height, params
    border = Properties(lambda a: a[0], lambda a: a[1], 1, (100, 1), 1)            # height, fi
    shifted_border = Properties(lambda a: a[0], lambda a: a[1], 1, (100, 1), 1)            # height, fi
    line = Properties(lambda a: a[0], lambda a: a[1], 2, (100, 100), 2)            # height, width
    rounded_line = Properties(lambda a: a[0], lambda a: a[1], 2, (100, 100), 2)    # height, width
    two_lines = Properties(lambda a: a[0], lambda a: 2*a[1] + a[1]*a[2], 3, (100, 100, 10), 2) # height, width, distance_factor
    circle = Properties(lambda a: a[0], lambda a: a[0], 1, (200, ), 1)             # height
    triangle = Properties(lambda a: a[0], lambda a: a[1], 2, (100, 100), 2)        # height, width
    upside_triangle = Properties(lambda a: a[0], lambda a: a[1], 2, (100, 100), 2) # height, width
    square = Properties(lambda a: a[0], lambda a: a[0], 1, (100, ), 1)             # height
    octagon = Properties(lambda a: a[0], lambda a: a[1], 3, (100, 100, 1), 2)      # height, width, sides_factor
    arrow = Properties(lambda a: a[0], lambda a: a[1], 3, (100, 100, 1), 2)        # height, width, angle
    rhombus = Properties(lambda a: a[0], lambda a: a[1], 2, (100, 100), 2)         # height, width
    trapeze = Properties(lambda a: a[0], lambda a: a[1], 3, (100, 100, 100), 3)    # height, width, width_2
    tear = Properties(lambda a: a[0], lambda a: a[1], 2, (100, 100), 2)            # height, width
    spear = Properties(lambda a: a[0], lambda a: a[1], 3, (100, 100, 1), 2)        # height, width, center
    date = Properties(lambda a: a[0], lambda a: a[1], 2, (100, 100), 2)            # height, width, params
    lange_date = Properties(lambda a: a[0], lambda a: a[0]*(122/74), 1, (100, ), 1)      # height
    moonphase = Properties(lambda a: a[0], lambda a: 2*a[0], 1, (100, 10, 40, 80), 1)         # height


    def get_height(self, args):
        fun = self.value.get_height
        return fun(args)

    def get_width(self, args):
        fun = self.value.get_width
        return fun(args)
