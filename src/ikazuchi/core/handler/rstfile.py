# -*- coding: utf-8 -*-

import re
from base import BaseHandler

_INLINE = [
    "\*+.*?\*+",    # italic or bold
    "``.*?``",      # literal
]

_ROLE = [
    ":.*?:`.*?`",   # :ref:`xxx`
]

_INLINE_ROLE = re.compile(r"({0})".format("|".join(_INLINE + _ROLE)))

class reSTFileHandler(BaseHandler):
    """
    Handler class for translating reST file
    """
    def _call_method(self, translate): pass

    @classmethod
    def markup_notranslate(self, text):
        repl = r"<span class=notranslate>\1</span>"
        return re.sub(_INLINE_ROLE, repl, text)
