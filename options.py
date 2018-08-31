import getopt
import sys
from collections import namedtuple


OptInfo = namedtuple('OptInfo', ['long', 'short', 'requires_arg', 'default'])

HELP_OPT = OptInfo('help', 'h', False, False)

#
# def get_option_values(options, argv):
#     opts, args = parse_options(options, argv)
#     opts_dict = {get_opt(options, opt_str): arg for opt_str, arg in opts}
#     out = [get_option(a, opts_dict) for a in options]
#     return out + [get_help(options), args]
#

def get_option_values(options, argv):
    argv = argv[1:]
    options = tuple([HELP_OPT] + [options])
    opts, args = parse_options(options, argv)
    opts_dict = {get_opt(options, opt_str): arg for opt_str, arg in opts}
    out = [get_option(a, opts_dict) for a in options]
    if out[0]:
        print(get_help(options))
        sys.exit()
    return out[1:] + [args]


def get_option(opt, opts_dict):
    out = opts_dict.get(opt, opt.default)
    flag_present = not opt.requires_arg and out == ''
    if flag_present:
        return True
    return out


def parse_options(options, argv):
    try:
        return getopt.getopt(argv, get_short_options(options),
                             get_long_options(options))
    except getopt.GetoptError:
        print(get_help(options))
        sys.exit(2)


def get_opt(options, opt_str):
    for opt in options:
        if check_opt(opt, opt_str):
            return opt


def check_opt(opt, opt_str):
    return opt_str in (f'-{opt.short}', f'--{opt.long}')


def get_short_options(options):
    out = (get_short_option(a) for a in options)
    return ''.join(out)


def get_short_option(opt):
    flag = ':' if opt.requires_arg else ''
    return opt.short + flag


def get_long_options(options):
    return [get_long_option(a) for a in options]


def get_long_option(opt):
    flag = '=' if opt.requires_arg else ''
    return opt.long + flag


def get_help(options):
    helps = (get_option_help(a) for a in options)
    out = ' '.join(helps)
    return f'test.py {out}'


def get_option_help(opt):
    out = f'-{opt.short}'
    if opt.requires_arg:
        out += f' <{opt.long}>'
    return out