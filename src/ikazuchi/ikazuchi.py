#!/usr/bin/env python
# -*- coding: utf-8 -*-

import optparse
import os
import sys

from locale import _
from utils import *

__version__ = "0.1"
TRANSLATE_API = ["google", "microsoft"]

def get_args():
    usage = _(u"%prog [options]")
    ver = "%prog {0}".format(__version__)
    parser = optparse.OptionParser(usage, version=ver)
    parser.set_defaults(api=TRANSLATE_API[0], lang_from="en",
                        lang_to=get_lang(), po_file=None, sentence=None,
                        comparison=False, verbose=False)
    parser.add_option("-a", "--api", dest="api", metavar="API",
                      help=u"translation api are {0}".format(TRANSLATE_API))
    parser.add_option("-f", "--from", dest="lang_from", metavar="LANG",
                      help=u"original language(msgid)")
    parser.add_option("-t", "--to", dest="lang_to", metavar="LANG",
                      help=u"target language(msgstr)")
    parser.add_option("-p", "--pofile", dest="po_file",
                      metavar="POFILE", help=u"target po file")
    parser.add_option("-s", "--sentence", dest="sentence",
                      metavar="SENTENCE", help=u"target sentence")
    parser.add_option("-c", "--comparison", dest="comparison",
                      action="store_true",
                      help=u"compare traslation between multi-api, "\
                            "cannot use with '-p po_file' option")
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="store_true",
                      help=u"print debug messages to stdout")

    opts, args = parser.parse_args()
    if not opts.lang_to:
        opts.lang_to = raw_input(u"Type language code: ")
    if opts.api in TRANSLATE_API and (
        opts.comparison and not opts.po_file) and (
        (opts.po_file and os.access(opts.po_file, os.R_OK)) or opts.sentence):
        return opts, args
    else:
        parser.print_help()
        sys.exit(0)

def main():
    opts, args = get_args()
    handler = get_handler(opts)
    t = get_translator(opts, handler)
    t.translate_with_handler()

if __name__ == "__main__":
    check_python_version()
    main()
