import ast
import operator as op
import re
from numbers import Number


###
##  DICT SUB
#

OPERATORS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}


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

def no_enum_error(a_enum, name, dbg_context):
    enum_name_tokens = re.split('([A-Z][a-z]*)', a_enum.__name__)
    enum_name = ' '.join([a.lower() for a in enum_name_tokens if a])
    enums = ', '.join([f'"{a.name}"' for a in list(a_enum)])
    msg = f'Invalid {enum_name} "{name}" in subgroup "{dbg_context}". ' \
        f'Available {enum_name}s: {enums}.'
    raise ValueError(msg)


def read_file(filename):
    with open(filename, encoding='utf-8') as file:
        return file.readlines()


def write_to_file(filename, text):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)