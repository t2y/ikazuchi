# -*- coding: utf-8 -*-

import abc
import json
import urllib2
from contextlib import closing
from urllib import urlencode

__all__ = [
    "TranslatingGoogle",
]


class Translator(object):
    """Base class for Translator"""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, lang_from, lang_to, handler):
        """Overridden by MixIn class
        must be set "self.handler = handler"
        """

    @abc.abstractmethod
    def translate(self, msgid):
        pass

    def translate_with_handler(self):
        """handler must be implement _translate method"""
        self.handler._translate(self.translate)


class GoogleTranslator(object):
    """
    Translator with Google Translate API
    http://code.google.com/intl/ja/apis/language/translate/overview.html
    see also
    Google Translate API Terms of Use
    http://code.google.com/intl/ja/apis/language/translate/terms.html
    """
    def __init__(self, lang_from, lang_to, handler):
        self.handler = handler
        self.query = {
            "v": "1.0",
            "langpair": "{0}|{1}".format(lang_from, lang_to),
        }
        protocol = "http://"
        domain = "ajax.googleapis.com"
        path = "/ajax/services/language/translate?"
        self._url = "{0}{1}{2}".format(protocol, domain, path)

    def translate(self, msgid):
        msgstr = ""
        self.query.update(q=msgid)
        url = "{0}{1}".format(self._url, urlencode(self.query))
        req = urllib2.Request(url)
        with closing(urllib2.urlopen(req)) as res:
            res_json = json.loads(res.read())
            if res_json["responseStatus"] == 200:
                msgstr = res_json["responseData"]["translatedText"]
            else:
                raise RuntimeError(res_json)
        return msgstr


# MixIn each implemented Translator
class TranslatingGoogle(GoogleTranslator, Translator):
    pass
