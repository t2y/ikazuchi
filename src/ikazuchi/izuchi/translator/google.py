# -*- coding: utf-8 -*-

import json
import urllib2
from contextlib import closing, nested
from urllib import urlencode

__all__ = [
    "GoogleTranslator",
]

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
        domain = "ajax.googleapis.com"
        path = "/ajax/services/language/translate?"
        self._url = "http://{0}{1}".format(domain, path)

    def translate(self, text):
        translated = ""
        self.query.update(q=text.encode("utf-8"))
        url = "{0}{1}".format(self._url, urlencode(self.query))
        req = urllib2.Request(url)
        with closing(urllib2.urlopen(req)) as res:
            res_json = json.loads(res.read())
            if res_json["responseStatus"] == 200:
                translated = res_json["responseData"]["translatedText"]
            else:
                raise RuntimeError(res_json)
        yield self.api(), translated
