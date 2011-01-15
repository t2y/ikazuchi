# -*- coding: utf-8 -*-

from nose.tools import *

# functions for test
from ikazuchi.izuchi.handler import *
from ikazuchi.izuchi.translator import *

class TestComparisonTranslator(object):

    def setup(self):
        self.comp = TranslatingComparison("en", "ja",
                        SingleSentenceHandler("args"))
        self.comp_rev = TranslatingComparison("ja", "en",
                        SingleSentenceHandler("args"))

    def test_is_exist_handler(self):
        for t in self.comp.translators:
            assert_equals(SingleSentenceHandler, t.handler.__class__)

    def test_call_api(self):
        for i, translated in enumerate(self.comp.translate("test")):
            expected = (self.comp.translators[i].api(),
                        unicode("テスト", "utf-8"))
            assert_equals(expected, translated)

    def test_call_api_rev(self):
        text = unicode("テスト", "utf-8")
        for i, translated in enumerate(self.comp_rev.translate(text)):
            expected = (self.comp.translators[i].api(), u"test")
            comp_translated = translated[0], translated[1].lower()
            assert_equals(expected, comp_translated)
