# -*- coding: utf-8 -*-

def get_multiline(lines, range_num):
    """ read lines every range_num
    >>> list(get_multiline(["a", "b", "c"], 2))
    [['a', 'b'], ['b', 'c']]
    >>> list(get_multiline(["a", "b", "c", "d"], 2))
    [['a', 'b'], ['b', 'c'], ['c', 'd']]
    >>> list(get_multiline(["a", "b", "c"], 3))
    [['a', 'b', 'c']]
    >>> list(get_multiline(["a", "b", "c", "d"], 3))
    [['a', 'b', 'c'], ['b', 'c', 'd']]
    """
    to = range_num * (-1) + 1
    for num, _ in enumerate(lines[:to]):
        yield lines[num:num + range_num]

def get_sequential_block(lines, compare_func):
    """
    >>> import re
    >>> pattern = re.compile(r"\w+")
    >>> cmp_func = lambda s: not re.search(pattern, s)
    >>> get_sequential_block([], cmp_func)
    (0, [])
    >>> get_sequential_block(["a", "b", "\\n"], cmp_func)
    (1, ['a', 'b'])
    >>> get_sequential_block(["a", "b", "c", "\\n"], cmp_func)
    (2, ['a', 'b', 'c'])
    >>> pattern = re.compile(r"\\n")
    >>> cmp_func = lambda s: re.search(pattern, s)
    >>> get_sequential_block(["a", "b", "c", "\\n"], cmp_func)
    (2, ['a', 'b', 'c'])
    """
    num = 0
    break_flag = False
    for num, mline in enumerate(get_multiline(lines, 2)):
        if compare_func(mline[1]):
            break_flag = True
            break
    if lines and not break_flag:
        # maybe read out to EOF
        num += 1
    return num, lines[0:num + 1]
