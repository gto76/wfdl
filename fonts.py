from genericpath import isfile


FONTS_FOLDER = 'fonts'
FONTS_ALIASES = {'lange': 'engraversmtbold', 'lange_thin': 'engr'}


def get_font_def(font_name):
    font_path = f'{FONTS_FOLDER}/{font_name}.ttf'
    if not isfile(font_path):
        if font_name not in FONTS_ALIASES:
            return
        font_path = f'{FONTS_FOLDER}/{FONTS_ALIASES[font_name]}.ttf'
    return '@font-face {' \
           f'    font-family: "{font_name}";' \
           f'    src: url({font_path}) format("truetype");' \
           '}' \
           'p.customfont {' \
           f'    font-family: "{font_name}", Arial;' \
           '}'