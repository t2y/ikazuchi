# -*- coding: utf-8 -*-

import sys

from izuchi.handler import *
from locale import _


def get_lang():
    from locale import getdefaultlocale
    lang, country = getdefaultlocale()[0].split("_")
    return lang


def dispatch_handler(opts):
    if opts.po_file:
        h = InteractiveHandler(opts.po_file)
    elif opts.sentence:
        h = SingleSentenceHandler(opts.sentence)
    return h


def check_python_version():
    ver = sys.version_info
    if ver[0] == 2 and ver[1] < 6:
        print _UNSUPPORTED_VERSION
        sys.exit(0)

_UNSUPPORTED_VERSION = _("Unsuporrted Python version, use 2.6 above")
