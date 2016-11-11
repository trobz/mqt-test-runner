# coding: utf-8
"""
helpers shared by the various QA tools
"""

# http://stackoverflow.com/questions/17771287/python-octal-escape-character-033-from-a-dictionary-value-translates-in-a-prin
GREY = "\033[0;37m"  # 'darkwhite'GREY
DARK_GREY = "\033[0;30m"  # 'darkblack'GREY
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
YELLOW_LIGHT = "\033[33m"
CLEAR = "\033[0;m"


def colorized(text, color):
    return '\n'.join(
        map(lambda line: color + line + CLEAR, text.split('\n')))


def green(text):
    return colorized(text, GREEN)


def yellow(text):
    return colorized(text, YELLOW)


def red(text):
    return colorized(text, RED)


def yellow_light(text):
    return colorized(text, YELLOW_LIGHT)


def grey(text):
    return colorized(text, GREY)


def dark_grey(text):
    return colorized(text, DARK_GREY)


fail_msg = red("FAIL")
success_msg = green("Success")
