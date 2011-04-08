# -*- coding: utf-8 -*-

import abc
import utils
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
    def detect(self, text): pass

    @abc.abstractmethod
    def translate(self, text): pass

    def call_method_with_handler(self):
        method = getattr(self, self.handler.method_name)
        self.handler._call_method(method)


# MixIn each implemented Translator
class TranslatingGoogle(GoogleTranslator, Translator): pass
class TranslatingMicrosoft(MicrosoftTranslator, Translator): pass
class TranslatingYahoo(YahooTranslator, Translator): pass

TRANSLATE_API = {
    "google": TranslatingGoogle,
    "microsoft": TranslatingMicrosoft,
    "yahoo": TranslatingYahoo,
}
