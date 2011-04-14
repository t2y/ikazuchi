# -*- coding: utf-8 -*-

from base import BaseHandler
from ikazuchi.core.translator import TRANSLATE_API as API
from tempfile import NamedTemporaryFile

class AudioHandler(BaseHandler):
    """
    Handler class for text-to-speech
    """
    def __init__(self, opts):
        self.is_translate = False
        if opts.sentences[0] == "audio":
            self.sentences = opts.sentences[1:]
            self.lang = opts.lang_from
        else:
            self.sentences = opts.sentences[:-1]
            self.lang = opts.lang_to
            self.is_translate = True
        self.encoding = opts.encoding
        self.quiet = opts.quiet
        self.translator = API[opts.api](opts.lang_from, opts.lang_to, None)
        if opts.api == "google":
            self.method_name = "translate_tts"
        elif opts.api == "microsoft":
            self.method_name = "speak"

    def _encode(self, text):
        return text.encode(self.encoding[1])

    def _translate(self, text):
        if not self.quiet:
            print self._encode(u"{0:25}{1}".format("sentence:", text))
        api, translated = self.translator.translate(text)
        _method = u"{0}({1}):".format("translate", api)
        print self._encode(u"{0:25}{1}".format(_method, translated))
        return translated

    def _call_method(self, api_method):
        for target in self.sentences:
            if self.is_translate:
                target = self._translate(target)
            with NamedTemporaryFile(mode="wb") as tmp:
                api = api_method(target, self.lang, tmp)
                _method = u"{0}({1}):".format(self.method_name, api)
                print self._encode(u"{0:25}".format(_method))
                self.play_audio(tmp.name)

    def play_audio(self, file_name):
        import platform
        import subprocess
        os_name = platform.system()
        if os_name == "Darwin":
            subprocess.call(["afplay", file_name])
        else:
            print "Not supported for playing audio: {0}".format(os_name)
