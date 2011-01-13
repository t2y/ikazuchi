# -*- coding: utf-8 -*-

import abc
import locale
import polib

from ikazuchi.locale import _

__all__ = [
    "InteractiveHandler",
    "SingleSentenceHandler",
]

DEFAULT_ENCODING = "utf-8"


class BaseHandler(object):
    """Base class for handler"""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def _translate(self, msgid):
        pass


class InteractiveHandler(BaseHandler):
    """
    Handler class for translating interactively
    """
    def __init__(self, po_file):
        self.po = polib.pofile(po_file)
        self.po.metadata["Content-Type"] = "text/plain; charset=utf-8"
        self.encoding = locale.getdefaultlocale()[1]
        if not self.encoding:
            self.encoding = DEFAULT_ENCODING

    def _select_translation(self, for_ref, current, entered):
        """define which translated string use"""
        s = entered
        if entered.lower() == "y":
            s = for_ref
        elif current and entered == "":
            s = current
        return s

    def _translate(self, translate):
        """translate msgid in po file"""
        _prompt = _(u"Input: ").encode(self.encoding)
        for p in self.po:
            for_ref = translate(p.msgid)
            print _(u"msgid:\t\t{0}").format(p.msgid)
            if p.msgstr:
                print _(u"current msgstr:\t{0}").format(p.msgstr)
            print _(u"for reference:\t{0}").format(for_ref)
            entered = unicode(raw_input(_prompt), self.encoding)
            p.msgstr = self._select_translation(for_ref, p.msgstr, entered)
            self.po.save()
            print _(u"updated msgstr:\t{0}").format(p.msgstr)
            print ""


class SingleSentenceHandler(BaseHandler):
    """
    Handler class for translating single sentence
    """
    def __init__(self, sentence):
        self.sentence = sentence

    def _translate(self, translate):
        print _(u"sentence:\t\t{0}").format(self.sentence)
        for api, text in translate(self.sentence):
            print _(u"translated({0}):\t{1}").format(api, text)
