# -*- coding: utf-8 -*-

import abc

from google import GoogleTranslator
from microsoft import MicrosoftTranslator
from yahoo import YahooTranslator

__all__ = [
    "TRANSLATE_API",
]

class Translator(object):
    """Base class for Translator"""

    __metaclass__ = abc.ABCMeta
    api = lambda klass: klass.__class__.__name__.replace('Translating', '')

    @abc.abstractmethod
    def __init__(self, lang_from, lang_to, handler):
        """Overridden by MixIn class
        must be set "self.handler = handler"
        """

    @abc.abstractmethod
    def translate(self, text): pass

    def translate_with_handler(self):
        """handler must be implement _translate method"""
        self.handler._translate(self.translate)


class AllTranslator(object):
    """Class included in all translators for comparison"""
    def __init__(self, lang_from, lang_to, handler):
        self.handler = handler
        self.translators = [
            TranslatingGoogle(lang_from, lang_to, handler),
            TranslatingMicrosoft(lang_from, lang_to, handler),
            TranslatingYahoo(lang_from, lang_to, handler),
        ]

    def translate(self, text):
        for t in self.translators:
            for translated in t.translate(text):
                yield translated


# MixIn each implemented Translator
class TranslatingGoogle(GoogleTranslator, Translator): pass
class TranslatingMicrosoft(MicrosoftTranslator, Translator): pass
class TranslatingYahoo(YahooTranslator, Translator): pass
class TranslatingAll(AllTranslator, Translator): pass

TRANSLATE_API = {
    "google": TranslatingGoogle,
    "microsoft": TranslatingMicrosoft,
    "yahoo": TranslatingYahoo,
    "all": TranslatingAll,
}
