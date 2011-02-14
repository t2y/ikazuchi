# -*- coding: utf-8 -*-

import tempfile
import urllib2
from contextlib import closing, nested
from urllib import urlencode
from xml.etree import ElementTree as ET

__all__ = [
    "MicrosoftTranslator"
]

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
    max_trans = "5"
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
        "opt": ("TranslateOptions", None),
        "req": ("TranslateArrayRequest", None),
        "gettrans_req": ("GetTranslationsArrayRequest", None),
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

    def serialize_option(self, items, array_type):
        tree = ET.TreeBuilder()
        tree.start(array_type, self.xml_attr["xmlns_mt"])
        for key, value in items:
            tree.start(key, {})
            tree.data(value)
            tree.end(key)
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
        """ BreakSentences Method
        http://msdn.microsoft.com/en-us/library/ff512410.aspx
        """
        query = {
            "appId": self.app_id,
            "text": text.encode("utf-8"),
            "language": self.lang_from,
        }
        url = self.get_url(self.break_sentences, query)
        api, lengths = self.request(url, self.xml_tag["array"]["int"])
        yield api, lengths

    def detect(self, text):
        """ Detect Method
        http://msdn.microsoft.com/en-us/library/ff512411.aspx
        """
        query = {"appId": self.app_id, "text": text.encode("utf-8")}
        url = self.get_url(self.detect, query)
        api, lang = self.request(url, self.xml_tag["base"]["str"])
        yield api, lang

    def detect_array(self, texts):
        """ DetectArray Method
        http://msdn.microsoft.com/en-us/library/ff512412.aspx
        """
        query = {"appId": self.app_id}
        url = self.get_url(self.detect_array, query)
        data = {
            "type": self.content_type["xml"],
            "data": self.serialize_array(texts, *self.xml_type["str"]),
        }
        api, langs = self.request(url, self.xml_tag["array"]["str"], data)
        yield api, langs

    def get_language_names(self, lang_codes):
        """ GetLanguageNames Method
        http://msdn.microsoft.com/en-us/library/ff512414.aspx
        """
        query = {"appId": self.app_id, "locale": self.lang_to}
        url = self.get_url(self.get_language_names, query)
        data = {
            "type": self.content_type["xml"],
            "data": self.serialize_array(lang_codes, *self.xml_type["str"]),
        }
        api, langs = self.request(url, self.xml_tag["array"]["str"], data)
        yield api, langs

    def get_languages_for_speak(self):
        """ GetLanguagesForSpeak Method
        http://msdn.microsoft.com/en-us/library/ff512415.aspx
        """
        query = {"appId": self.app_id}
        url = self.get_url(self.get_languages_for_speak, query)
        api, langs = self.request(url, self.xml_tag["array"]["str"])
        yield api, langs

    def get_languages_for_translate(self):
        """ GetLanguagesForTranslate Method
        http://msdn.microsoft.com/en-us/library/ff512416.aspx
        """
        query = {"appId": self.app_id}
        url = self.get_url(self.get_languages_for_translate, query)
        api, langs = self.request(url, self.xml_tag["array"]["str"])
        yield api, langs

    def get_translations(self, text):
        """ GetTranslations Method
        http://msdn.microsoft.com/en-us/library/ff512417.aspx
        """
        query = {
            "appId": self.app_id,
            "text": text.encode("utf-8"),
            "from": self.lang_from,
            "to": self.lang_to,
            "maxTranslations": self.max_trans,
        }
        options = [
            ("Category", "general"),
            ("ContentType", self.content_type["text"]),
            ("Uri", ""),
            ("User", ""),
            ("State", ""),
        ]
        data = {
            "type": self.content_type["xml"],
            "data": self.serialize_option(options, self.xml_type["opt"][0])
        }
        url = self.get_url(self.get_translations, query)
        api, trans = self.request(url, None, data)
        yield self.api(), trans

    def get_translations_array(self, texts):
        """ GetTranslationsArray Method
        http://msdn.microsoft.com/en-us/library/ff512418.aspx
        """
        query = {"appId": self.app_id}
        params = [
            ("AppId", self.app_id),
            ("From", self.lang_from),
            ("Options", [
                ("Category", "general"),
                ("ContentType", self.content_type["text"]),
                ("Uri", ""),
                ("User", ""),
                ("State", ""),
            ]),
            ("Texts", texts),
            ("To", self.lang_to),
            ("MaxTranslations", self.max_trans),
        ]
        data = {
            "type": self.content_type["xml"],
            "data": self.serialize_translate_array(
                        params, self.xml_type["gettrans_req"][0]),
        }
        url = self.get_url(self.get_translations_array, query)
        api, trans = self.request(url, None, data)
        yield self.api(), trans

    def speak(self, text):
        """ Speak Method
        http://msdn.microsoft.com/en-us/library/ff512420.aspx
        """
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
        """ Translate Method
        http://msdn.microsoft.com/en-us/library/ff512421.aspx
        """
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
        """ TranslateArray Method
        http://msdn.microsoft.com/en-us/library/ff512422.aspx
        """
        query = {"appId": self.app_id}
        params = [
            ("AppId", self.app_id),
            ("From", self.lang_from),
            ("Options", [
                ("Category", "general"),
                ("ContentType", self.content_type["text"]),
                ("Uri", ""),
                ("User", ""),
                ("State", ""),
            ]),
            ("Texts", texts),
            ("To", self.lang_to),
        ]
        data = {
            "type": self.content_type["xml"],
            "data": self.serialize_translate_array(
                        params, self.xml_type["req"][0]),
        }
        url = self.get_url(self.translate_array, query)
        api, items = self.request(url, None, data)
        _cycle = 7
        trans = [items[i] for i in range(5, _cycle * len(texts), _cycle)]
        yield self.api(), trans
