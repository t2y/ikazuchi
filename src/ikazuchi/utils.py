# -*- coding: utf-8 -*-

import sys

from izuchi.handler import *
from izuchi.translator import *
from locale import _


def get_lang():
    from locale import getdefaultlocale
    lang, country = getdefaultlocale()[0].split("_")
    return lang


def get_handler(opts):
    h = None
    if opts.po_file:
        h = InteractiveHandler(opts.po_file)
    elif opts.sentence:
        h = SingleSentenceHandler(opts.sentence)
    return h


def get_translator(opts, handler):
    from ikazuchi import TRANSLATE_API
    t = None
    if opts.comparison:
        t = TranslatingComparison
    elif opts.api == TRANSLATE_API[0]:
        t = TranslatingGoogle
    elif opts.api == TRANSLATE_API[1]:
        t = TranslatingMicrosoft
    return t(opts.lang_from, opts.lang_to, handler)


def check_python_version():
    ver = sys.version_info
    if ver[0] == 2 and ver[1] < 6:
        print _UNSUPPORTED_VERSION
        sys.exit(0)

_UNSUPPORTED_VERSION = _("Unsuporrted Python version, use 2.6 above")
