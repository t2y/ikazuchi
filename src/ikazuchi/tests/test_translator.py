# -*- coding: utf-8 -*-

from nose.tools import *

# functions for test
from ikazuchi.core.translator.utils import *

def test_call_api_with_multithread():
    def dummy_func(_):
        return True
    lines_num = 30
    actual = call_api_with_multithread(dummy_func, range(lines_num))
    assert_equal([True] * lines_num, actual)
