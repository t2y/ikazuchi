# -*- coding: utf-8 -*-

import json
import urllib2
from contextlib import closing
from urllib import urlencode
from utils import get_ip_address

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
    domain = "ajax.googleapis.com"
    common_path = "/ajax/services/language/"
    key = "ABQIAAAAK6kpHnylgmAYtO7ZX01XXRSvW2ISZ2KI4wU-F"\
          "k6WlRk77d73EhTtYeI1LUl3BfkKv-17KKEWzdRTMw"
    userip = get_ip_address()
    q_format = "html"

    def __init__(self, lang_from, lang_to, handler):
        self.lang_from = lang_from
        self.lang_to = lang_to
        self.handler = handler
        self._url = "http://{0}{1}".format(self.domain, self.common_path)

    def get_api_path(self, func):
        return "{0}?".format(func.func_name)

    def get_url(self, func, query):
        return "{0}{1}{2}".format(self._url,
                self.get_api_path(func), urlencode(query))

    def request(self, url):
        req = urllib2.Request(url)
        with closing(urllib2.urlopen(req)) as res:
            res_json = json.loads(res.read())
            if res_json["responseStatus"] == 200:
                response = res_json["responseData"]
            else:
                raise RuntimeError(res_json)
        return response

    def call_api(self, func, query, key=None):
        """high-level method to make url and request"""
        url = self.get_url(func, query)
        response = self.request(url)
        if key:
            response = response[key]
        return self.api(), response

    def detect(self, text):
        """ JSON Developer's Guide for Language Detect
        http://code.google.com/intl/ja/apis/language/translate/v1/\
        using_rest_langdetect.html
        """
        query = {
            "v": "1.0",
            "q": text.encode("utf-8"),
            "key": self.key,
            "userip": self.userip,
        }
        return self.call_api(self.detect, query, "language")

    def translate(self, text):
        """ JSON Developer's Guide for Translate
        http://code.google.com/intl/ja/apis/language/translate/v1/\
        using_rest_translate.html
        """
        query = {
            "v": "1.0",
            "q": text.encode("utf-8"),
            "langpair": "{0}|{1}".format(self.lang_from, self.lang_to),
            "key": self.key,
            "userip": self.userip,
            "format": self.q_format,
        }
        _key = "translatedText"
        api, response = self.call_api(self.translate, query, _key)
        return api, self.parse_html(response)

    def translate_tts(self, text, lang, f):
        """ Unofficial Google Text To Speech API
        http://weston.ruter.net/projects/google-tts/
        """
        headers = {"User-Agent":
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-US) "
            "AppleWebKit/534.16 (KHTML, like Gecko) "
            "Chrome/10.0.648.204 Safari/534.16"
        }
        query = {"tl": lang, "q": text.encode("utf-8")}
        url = "http://translate.google.com/translate_tts?{0}".format(
                urlencode(query))
        req = urllib2.Request(url, None, headers)
        with closing(urllib2.urlopen(req)) as res:
            f.write(res.read())
            f.flush()
        return self.api()
