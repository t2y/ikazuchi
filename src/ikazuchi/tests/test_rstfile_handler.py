# -*- coding: utf-8 -*-

from nose.tools import *

# functions for test
from ikazuchi.core.handler.rstfile import *

class TestreSTParser(object):

    def _test_func(self, data_set, func):
        """
        common assert function for each test
        """
        for data, expected in data_set:
            info, num = func(data)
            assert_equal(expected, [info, num])

    def test_get_directive(self):
        from data.rst.parse_directive import DATA_SET
        self._test_func(DATA_SET, reSTParser.get_directive)

    def test_get_sourceblock(self):
        from data.rst.parse_sourceblock import DATA_SET
        self._test_func(DATA_SET, reSTParser.get_sourceblock)

    def test_get_lineblock(self):
        from data.rst.parse_lineblock import DATA_SET
        self._test_func(DATA_SET, reSTParser.get_lineblock)

    def test_get_listblock(self):
        from data.rst.parse_listblock import DATA_SET
        self._test_func(DATA_SET, reSTParser.get_listblock)

    def test_get_tableblock(self):
        from data.rst.parse_tableblock import DATA_SET
        self._test_func(DATA_SET, reSTParser.get_tableblock)

    def test_get_section(self):
        from data.rst.parse_section import DATA_SET
        self._test_func(DATA_SET, reSTParser.get_section)

    def test_get_paragraph(self):
        from data.rst.parse_paragraph import DATA_SET
        self._test_func(DATA_SET, reSTParser.get_paragraph)

    def test_get_indent_paragraph(self):
        from data.rst.parse_indent_paragraph import DATA_SET
        self._test_func(DATA_SET, reSTParser.get_indent_paragraph)

class TestreSTApiCaller(object):

    def setup(self):
        self.caller = reSTApiCaller(None, None)

    def _test_func(self, data_set, func):
        """
        common assert function for each test
        """
        for data, expected in data_set:
            actual = func(data)
            assert_equal(expected, actual)

    def test_get_indent_and_text(self):
        from data.rst.api_call_text_with_indent import DATA_SET
        self._test_func(DATA_SET, reSTApiCaller.get_indent_and_text)

    def test_markup_paragraph_notranslate(self):
        from data.rst.api_call_markup_notranslate import DATA_SET
        self._test_func(DATA_SET, reSTApiCaller.markup_paragraph_notranslate)
