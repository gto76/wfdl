from enum import Enum, auto


class Shape(Enum):
    """Second element is width formula. Third no of required arguments. Fourth
    the maximum sizes of the arguments."""
    number = auto(), lambda args: args[0] * 1.34 # height, kind (minute, roman,
    # hour), orient (horizontal, rotating, half_rotating) [, font]
    face = auto(), lambda args: args[0]           # height, params
    border = auto(), lambda args: args[1], 1, (100, 1)         # height, fi
    line = auto(), lambda args: args[1], 2, (100, 100)           # height, width
    rounded_line = auto(), lambda args: args[1], 2, (100, 100)   # height, width
    two_lines = auto(), lambda args: 2*args[1] + args[1]*args[2], 3, (100, 100, 10)  # height,
    # width, distance_factor
    circle = auto(), lambda args: args[0], 1, (100, )      # height
    triangle = auto(), lambda args: args[1], 2, (100, 100)       # height, width
    upside_triangle = auto(), lambda args: args[1], 2, (100, 100)  # height, width
    square = auto(), lambda args: args[0], 1, (100, )         # height
    octagon = auto(), lambda args: args[1], 3, (100, 100, 1)        # height, width, sides_factor
    arrow = auto(), lambda args: args[1], 3, (100, 100, 1)          # height, width, angle
    rhombus = auto(), lambda args: args[1], 2, (100, 100)        # height, width
    trapeze = auto(), lambda args: args[1], 3, (100, 100, 100)        # height, width, width_2
    tear = auto(), lambda args: args[1], 2, (100, 100)           # height, width
    spear = auto(), lambda args: args[1], 3, (100, 100, 1)        # height, width, center
    date = auto(), lambda args: args[1], 2, (100, 100)           # height, params
