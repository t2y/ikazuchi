# -*- coding: utf-8 -*-

import polib
from base import BaseHandler

try:
    from ikazuchi.locale import _
except ImportError:
    def _(s): return s

class POFileHandler(BaseHandler):
    """
    Handler class for translating interactively
    """
    def __init__(self, po_file, encoding):
        self.encoding = encoding
        self.po = polib.pofile(po_file, autodetect_encoding=False,
                               encoding=self.encoding[1])
        self.po.metadata["Content-Type"] = "text/plain; charset={0}".format(
                                                self.encoding[1])

    def _select_translation(self, ref, current, entered):
        """define which translated string use"""
        s = entered
        if entered.lower() == "y":
            s = ref
        elif current and entered == "":
            s = current
        return s

    def _call_method(self, translate):
        """translate msgid in po file"""
        _prompt = _(u"Input: ").encode(self.encoding[0])
        for p in self.po:
            api, ref = translate(p.msgid)
            print _(u"msgid:\t\t\t{0}").format(p.msgid)
            if p.msgstr:
                print _(u"current msgstr:\t\t{0}").format(p.msgstr)
            print _(u"reference({0}):\t{1}").format(api, ref)
            entered = unicode(raw_input(_prompt), self.encoding[0])
            p.msgstr = self._select_translation(ref, p.msgstr, entered)
            self.po.save()
            print _(u"updated msgstr:\t\t{0}").format(p.msgstr)
            print ""
