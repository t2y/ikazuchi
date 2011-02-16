# -*- coding: utf-8 -*-

import json
import urllib2
from contextlib import closing
from urllib import urlencode

__all__ = [
    "YahooTranslator",
]

class YahooTranslator(object):
    """
    Translator with Yahoo! Pipes
    http://pipes.yahoo.com/pipes/
    see also
    Yahoo! Pipes Terms of Use
    http://info.yahoo.com/legal/us/yahoo/pipes/pipes-4396.html
    """
    def __init__(self, lang_from, lang_to, handler):
        self.handler = handler
        self.query = {
            "_render": "json",
        }
        domain = "pipes.yahoo.com"
        path = "/t2y1979/{0}?".format(self._get_api(lang_from, lang_to))
        self._url = "http://{0}{1}".format(domain, path)

    def _get_api(self, lang_from, lang_to):
        # convert for for arbitrary api name
        api = "{0}2{1}".format(lang_from, lang_to)
        if lang_from == "ja" and lang_to == "en":
            api = "ja2en_"
        elif lang_from == "en" and lang_to.lower() == "zh-cn":
            api = "en2zhcn"
        elif lang_from == "en" and lang_to.lower() == "zh-tw":
            api = "en2zhtw"
        return api

    def detect(self, text):
        yield self.api(), "Not Implemented"

    def translate(self, text):
        translated = ""
        self.query.update(text=text.encode("utf-8"))
        url = "{0}{1}".format(self._url, urlencode(self.query))
        req = urllib2.Request(url)
        with closing(urllib2.urlopen(req)) as res:
            res_json = json.loads(res.read())
            translated = res_json["value"]["items"][0]["description"]
        yield self.api(), translated
