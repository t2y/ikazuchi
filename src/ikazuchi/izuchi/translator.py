# -*- coding: utf-8 -*-

import abc
import json
import tempfile
import urllib2
from contextlib import closing, nested
from urllib import urlencode
from xml.etree import ElementTree as ET

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


class MicrosoftTranslator(object):
    """
    Microsoft Translator
    http://www.microsofttranslator.com/dev/
    see also
    Microsoft Terms of Use
    http://www.bing.com/developers/tou.aspx
    """
    domain = "api.microsofttranslator.com"
    common_path = "/V2/Http.svc/"
    app_id = "D9D0E326A70EA4E66218F43130890052808A0142"
    schema = {
        "base": "http://schemas.microsoft.com/2003/10/Serialization/",
        "array": "http://schemas.microsoft.com/2003/10/Serialization/Arrays",
        "mt": "http://schemas.datacontract.org/2004/07/"
                "Microsoft.MT.Web.Service.V2",
    }
    xml_attr = {
        "xmlns_array": {"xmlns": schema["array"]},
        "xmlns_mt": {"xmlns": schema["mt"]},
    }
    xml_tag = dict([(key, {
                            "int": "{%s}int" % schema[key],
                            "str": "{%s}string" % schema[key],
                          }) for key in schema.keys()])
    xml_translate_array_tag = [
        "{%s}ArrayOfTranslateArrayResponse" % schema["mt"],
        "{%s}TranslateArrayResponse" % schema["mt"],
        "{%s}From" % schema["mt"],
        "{%s}OriginalTextSentenceLengths" % schema["mt"],
        "{%s}int" % schema["array"],
        "{%s}TranslatedText" % schema["mt"],
        "{%s}TranslatedTextSentenceLengths" % schema["mt"],
        "{%s}int" % schema["array"],
    ]
    xml_type = {
        "int": ("ArrayOfint", "int"),
        "str": ("ArrayOfstring", "string"),
        "req": ("TranslateArrayRequest", None),
    }
    content_type = {
        "text": "text/plain",
        "html": "text/html",
        "xml": "text/xml; charset=utf-8",
    }

    def __init__(self, lang_from, lang_to, handler):
        self.lang_from = lang_from
        self.lang_to = lang_to
        self.handler = handler
        self._url = "http://{0}{1}".format(self.domain, self.common_path)

    def get_api_path(self, func):
        return "{0}?".format(func.func_name.title().replace("_", ""))

    def get_url(self, func, query):
        return "{0}{1}{2}".format(self._url,
                self.get_api_path(func), urlencode(query))

    def request(self, url, tag=None, post_data=None):
        items = []
        req = urllib2.Request(url)
        if post_data:
            req.add_header("Content-type", post_data["type"])
            req.add_data(post_data["data"])
        try:
            with closing(urllib2.urlopen(req)) as res:
                element = ET.parse(res)
                items = [i.text for i in element.getiterator(tag)]
        except urllib2.HTTPError as err:
            # FIXME: consider later
            err_msg = err.read()
            print err_msg
        return self.api(), items

    def _set_tree(self, tree, items, attr):
        for key, value in items:
            tree.start(key, attr)
            tree.data(value)
            tree.end(key)

    def _set_tree_with_integers(self, tree, nums):
        for num in nums:
            tree.start("int", self.xml_attr["xmlns_array"])
            tree.data(num)
            tree.end("int")

    def _set_tree_with_texts(self, tree, texts):
        for text in texts:
            tree.start("string", self.xml_attr["xmlns_array"])
            tree.data(text.encode("utf-8"))
            tree.end("string")

    def serialize_array(self, items, array_type, data_type):
        tree = ET.TreeBuilder()
        tree.start(array_type, self.xml_attr["xmlns_array"])
        if data_type == "string":
            self._set_tree_with_texts(tree, items)
        elif data_type == "int":
            self._set_tree_with_integers(tree, items)
        else:
            # FIXME: consider later
            pass
        ret = tree.end(array_type)
        return ET.tostring(ret)

    def serialize_translate_array(self, param, array_type):
        tree = ET.TreeBuilder()
        tree.start(array_type, {})
        for key, value in param:
            tree.start(key, {})
            if key == "Options":
                self._set_tree(tree, value, self.xml_attr["xmlns_mt"])
            elif key == "Texts":
                self._set_tree_with_texts(tree, value)
            else:
                tree.data(value)
            tree.end(key)
        ret = tree.end(array_type)
        return ET.tostring(ret)

    def break_sentences(self, text):
        query = {
            "appId": self.app_id,
            "text": text.encode("utf-8"),
            "language": self.lang_from,
        }
        url = self.get_url(self.break_sentences, query)
        api, lengths = self.request(url, self.xml_tag["array"]["int"])
        yield api, lengths

    def detect(self, text):
        query = {"appId": self.app_id, "text": text.encode("utf-8")}
        url = self.get_url(self.detect, query)
        api, lang = self.request(url, self.xml_tag["base"]["str"])
        yield api, lang

    def detect_array(self, texts):
        query = {"appId": self.app_id}
        url = self.get_url(self.detect_array, query)
        data = {
            "type": self.content_type["xml"],
            "data": self.serialize_array(texts, *self.xml_type["str"]),
        }
        api, langs = self.request(url, self.xml_tag["array"]["str"], data)
        yield api, langs

    def get_language_names(self, lang_codes):
        query = {"appId": self.app_id, "locale": self.lang_to}
        url = self.get_url(self.get_language_names, query)
        data = {
            "type": self.content_type["xml"],
            "data": self.serialize_array(lang_codes, *self.xml_type["str"]),
        }
        api, langs = self.request(url, self.xml_tag["array"]["str"], data)
        yield api, langs

    def get_languages_for_speak(self):
        query = {"appId": self.app_id}
        url = self.get_url(self.get_languages_for_speak, query)
        api, langs = self.request(url, self.xml_tag["array"]["str"])
        yield api, langs

    def get_languages_for_translate(self):
        query = {"appId": self.app_id}
        url = self.get_url(self.get_languages_for_translate, query)
        api, langs = self.request(url, self.xml_tag["array"]["str"])
        yield api, langs

    def get_translations(self, text):
        query = {
            "appId": self.app_id,
            "text": text.encode("utf-8"),
            "from": self.lang_from,
            "to": self.lang_to,
            "contentType": self.content_type["text"],
            "maxTranslations": 10,
            "category": "general",
        }
        # FIXME: consider later
        options = {}
        data = {
            "type": self.content_type["xml"],
            "data": self.serialize_array(options, *self.xml_type["str"]),
        }
        url = self.get_url(self.get_translations, query)
        api, trans = self.request(url, self.xml_tag["base"]["str"], data)
        yield self.api(), trans

    def get_translations_array(self, texts): pass

    def speak(self, text):
        # FIXME: consider later
        query = {
            "appId": self.app_id,
            "text": text.encode("utf-8"),
            "language": self.lang_to,
            "format": "audio/wav",
        }
        url = self.get_url(self.speak, query)
        req = urllib2.Request(url)
        with nested(tempfile.NamedTemporaryFile(mode="wb"),
                    closing(urllib2.urlopen(req))) as (tmp, res):
            tmp.write(res.read())
            tmp.file.seek(0)

    def translate(self, text):
        query = {
            "appId": self.app_id,
            "text": text.encode("utf-8"),
            "from": self.lang_from,
            "to": self.lang_to,
            "contentType": self.content_type["text"],
            "category": "general",
        }
        url = self.get_url(self.translate, query)
        api, trans = self.request(url, self.xml_tag["base"]["str"])
        yield self.api(), trans[0]

    def translate_array(self, texts):
        query = {"appId": self.app_id}
        url = self.get_url(self.translate_array, query)
        param = [
            ("AppId", self.app_id),
            ("From", self.lang_from),
            ("Options", [
                ("Category", "general"),
                ("ContentType", self.content_type["text"]),
                ("Uri", "all"),
                ("User", "all"),
                ("State", ""),
            ]),
            ("Texts", texts),
            ("To", self.lang_to),
        ]
        data = {
            "type": self.content_type["xml"],
            "data": self.serialize_translate_array(
                        param, self.xml_type["req"][0]),
        }
        api, items = self.request(url, None, data)
        _cycle = 7
        trans = [items[i] for i in range(5, _cycle * len(texts), _cycle)]
        yield self.api(), trans

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

    def translate(self, text):
        translated = ""
        self.query.update(text=text.encode("utf-8"))
        url = "{0}{1}".format(self._url, urlencode(self.query))
        req = urllib2.Request(url)
        with closing(urllib2.urlopen(req)) as res:
            res_json = json.loads(res.read())
            translated = res_json["value"]["items"][0]["description"]
        yield self.api(), translated


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
