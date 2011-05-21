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
    >>> list(get_multiline(["a", "b"], 3))
    [['a', 'b']]
    >>> list(get_multiline(["a", "b"], 5))
    [['a', 'b']]
    >>> list(get_multiline([], 2))
    [[]]
    """
    to = range_num * (-1) + 1
    if len(lines) <= abs(to):
        yield lines
    else:
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
    if len(lines) >= 2:
        for num, mline in enumerate(get_multiline(lines, 2)):
            if compare_func(mline[1]):
                break
        else:
            # maybe read out to EOF
            num += 1
    return num, lines[0:num + 1]

def get_east_asian_width(unicode_str):
    """
    Na: Narrow    1 半角英数
    H : Halfwidth 1 半角カナ
    W : Wide      2 全角文字
    F : Fullwidth 2 全角英数
    N : Neutral   1 アラビア文字
    A : Ambiguous 1 ギリシア文字、キリル文字(locale で幅が違う)
    >>> get_east_asian_width(unicode("1２3あいうabc", "utf-8"))
    13
    >>> get_east_asian_width(unicode("ﾊﾝｶｸｶﾅはどうかな？", "utf-8"))
    18
    >>> get_east_asian_width(unicode("スペース   全角　　　", "utf-8"))
    21
    """
    from unicodedata import east_asian_width
    width = 0
    for i in unicode_str:
        width += 1
        if east_asian_width(i) in ("W", "F"):
            width += 1
    return width

def zip_with_flatlist(list1, list2):
    """
    >>> zip_with_flatlist(range(3), range(3,6))
    [0, 3, 1, 4, 2, 5]
    >>> zip_with_flatlist(range(1), range(2,5))
    [0, 2]
    """
    _list = []
    for i, j in zip(list1, list2):
        _list.append(i)
        _list.append(j)
    return _list
