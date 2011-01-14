# -*- coding: utf-8 -*-

from nose.tools import *

# functions for test
from ikazuchi.izuchi.handler import *
from ikazuchi.izuchi.translator import *

class TestComparisonTranslator(object):

    def setup(self):
        self.comp = TranslatingComparison("en", "ja",
                        SingleSentenceHandler("args"))

    def test_is_exist_handler(self):
        for t in self.comp.translators:
            assert_equals(SingleSentenceHandler, t.handler.__class__)

    def test_call_api(self):
        for i, translated in enumerate(self.comp.translate("test")):
            expected = (self.comp.translators[i].api(),
                        unicode("テスト", "utf-8"))
            assert_equals(expected, translated)
