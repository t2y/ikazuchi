# -*- coding: utf-8 -*-

from nose.tools import *

# functions for test
from ikazuchi.core.translator.utils import *

def test_call_api_with_multithread():
    def dummy_func(num):
        sleep(0.1)
        return num
    from time import sleep
    args = range(30)
    assert_equal(args, call_api_with_multithread(dummy_func, args))
