# -*- coding: utf-8 -*-

from base import BaseHandler
from tempfile import NamedTemporaryFile

class AudioHandler(BaseHandler):
    """
    Handler class for text-to-speech
    """
    def __init__(self, opts):
        self.sentences = opts.sentences[1:]
        self.encoding = opts.encoding
        if opts.api == "google":
            self.method_name = "translate_tts"
        elif opts.api == "microsoft":
            self.method_name = "speak"

    def _encode(self, text):
        return text.encode(self.encoding[1])

    def _call_method(self, api_method):
        for s in self.sentences:
            with NamedTemporaryFile(mode="wb") as tmp:
                api = api_method(s, tmp)
                _method = u"{0}({1}):".format(self.method_name, api)
                print self._encode(u"{0:25}".format(_method))
                self.play_audio(tmp.name)

    def play_audio(self, file_name):
        import platform
        import subprocess
        os_name = platform.system()
        if os_name == "Darwin":
            subprocess.call(["afplay", file_name])
