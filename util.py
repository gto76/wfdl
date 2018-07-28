import ast
import operator as op
import re
from math import pi
from numbers import Number, Real



OPERATORS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}

###
##  DICT SUB
#


def replace_matched_items(elements, dictionary):
    if not elements:
        return []
    out = []
    for element in elements:
        if type(element) is set:
            out.append(replace_in_set(element, dictionary))
        elif type(element) is list:
            out.append(replace_matched_items(element, dictionary))
        elif type(element) is dict:
            out.append(element)
        else:
            out.append(get_value_of_exp(element, dictionary))
    return out


def replace_in_set(elements, dictionary):
    return {get_value_of_exp(element, dictionary) for element in elements}


def get_value_of_exp(exp, dictionary):
    if isinstance(exp, Number):
        return exp
    for key, value in dictionary.items():
        exp = exp.replace(key, str(value))
    if re.search('[a-zA-Z]', exp):
        return exp
    return eval_expr(exp)


def eval_expr(expr):
    return eval_(ast.parse(expr, mode='eval').body)


def eval_(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return OPERATORS[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp):
        return OPERATORS[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(node)


###
##  UTIL
#


def get_enum(a_enum, enum_name, dbg_context):
    try:
        out = a_enum[enum_name]
    except KeyError:
        no_enum_error(a_enum, enum_name, dbg_context)
    else:
        return out


def no_enum_error(a_enum, name, dbg_context):
    enum_name_tokens = re.split('([A-Z][a-z]*)', a_enum.__name__)
    enum_name = ' '.join([a.lower() for a in enum_name_tokens if a])
    enums = ', '.join([f'"{a.name}"' for a in list(a_enum)])
    msg = f'Invalid {enum_name} "{name}" in subgroup "{dbg_context}". ' \
        f'Available {enum_name}s: {enums}.'
    raise ValueError(msg)


def check_args(prms, dbg_context):
    if len(prms.shape.value) < 4:
        return
    check_args_no(prms, dbg_context)
    check_args_type(prms, dbg_context)


def check_args_no(prms, dbg_context):
    shape = prms.shape
    no_args = len(prms.args)
    min_args = shape.value[2]
    max_args = len(shape.value[3])
    if no_args < min_args:
        not_enough_args_err(shape, min_args, no_args, dbg_context)
    if no_args > max_args:
        too_much_args_err(shape, max_args, no_args, dbg_context)


def not_enough_args_err(shape, min_args, no_args, subgroup):
    msg = f'Shape "{shape.name}" needs at least {min_args} arguments, but ' \
          f'{no_args} were provided in subgroup "{subgroup}".'
    raise ValueError(msg)


def too_much_args_err(shape, max_args, no_args, subgroup):
    msg = f'Shape "{shape.name}" can have at most {max_args} arguments, but ' \
          f'{no_args} were provided in subgroup "{subgroup}".'
    raise ValueError(msg)


def check_args_type(prms, subgroup):
    for i, arg in enumerate(prms.args):
        if not isinstance(arg, Real):
            msg = f'Argument {arg} of shape "{prms.shape.name}" is a number. ' \
                f'Subgroup "{subgroup}".'
            raise ValueError(msg)
        max_arg = prms.shape.value[3][i]
        if arg > max_arg:
            msg = f'Argument {arg} of shape "{prms.shape.name}" is larger ' \
                f'than the maximum alloved value ({max_arg}). ' \
                f'Subgroup "{subgroup}".'
            raise ValueError(msg)




def read_file(filename):
    with open(filename, encoding='utf-8') as file:
        return file.readlines()


def write_to_file(filename, text):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)


def get_rad(fi):
    return fi * 2 * pi - pi / 2