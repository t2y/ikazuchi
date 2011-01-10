#!/usr/bin/env python
# -*- coding: utf-8 -*-

import optparse
import os
import sys

from izuchi.translator import *
from locale import _
from utils import *

__version__ = "0.1"
TRANSLATE_API = ["google", "yahoo"]


def get_args():
    usage = _(u"%prog [options]")
    ver = "%prog {0}".format(__version__)
    parser = optparse.OptionParser(usage, version=ver)
    parser.add_option("-a", "--api", dest="api",
                      default=TRANSLATE_API[0], metavar="API",
                      help=_(u"translation api are {0}").format(TRANSLATE_API))
    parser.add_option("-f", "--from", dest="lang_from",
                      default="en", metavar="LANG",
                      help=_(u"original language(msgid)"))
    parser.add_option("-t", "--to", dest="lang_to",
                      default=get_lang(), metavar="LANG",
                      help=_(u"target language(msgstr)"))
    parser.add_option("-p", "--pofile", dest="po_file",
                      default=None, metavar="POFILE",
                      help=_(u"target po file"))
    parser.add_option("-s", "--sentence", dest="sentence",
                      default=None, metavar="SENTENCE",
                      help=_(u"target sentence"))
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="store_true", default=False,
                      help=_(u"print debug messages to stdout"))

    opts, args = parser.parse_args()
    if not opts.lang_to:
        opts.lang_to = raw_input(u"Type language code: ")
    if (opts.po_file and os.access(opts.po_file, os.R_OK)) or opts.sentence:
        return opts, args
    else:
        parser.print_help()
        sys.exit(0)


def main():
    opts, args = get_args()
    handler = dispatch_handler(opts)
    # only Google Translate API, now!
    t = TranslatingGoogle(opts.lang_from, opts.lang_to, handler)
    t.translate_with_handler()

if __name__ == "__main__":
    check_python_version()
    main()
