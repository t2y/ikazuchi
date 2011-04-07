# -*- coding: utf-8 -*-

from base import BaseHandler

class SingleSentenceHandler(BaseHandler):
    """
    Handler class for translating single sentence
    """
    def __init__(self, opts):
        self.sentence = opts.sentence
        self.encoding = opts.encoding
        self.quiet = opts.quiet
        if opts.detect:
            self.method_name = "detect"

    def _encode(self, text):
        return text.encode(self.encoding[1])

    def _call_method(self, api_method):
        if not self.quiet:
            print self._encode(u"{0:25}{1}".format("sentence:", self.sentence))
        api, result = api_method(self.sentence)
        _method = u"{0}({1}):".format(self.method_name, api)
        print self._encode(u"{0:25}{1}".format(_method, result))
