#!/usr/bin/env python
# -*- coding: utf-8 -*-

import optparse
import os
import sys

from izuchi.translator import *
from utils import *

VERSION = "0.1"
TRANSLATE_API = ["google", "yahoo"]

def get_args():
    usage = "usage: %prog [options]"
    ver = "%prog {0}".format(VERSION)
    parser = optparse.OptionParser(usage, version=ver)
    parser.add_option("-a", "--api", dest="api",
                      default=TRANSLATE_API[0], metavar="API",
                      help=u"translation api are {0}".format(TRANSLATE_API))
    parser.add_option("-f", "--from", dest="lang_from",
                      default="en", metavar="LANG",
                      help=u"original language(msgid)")
    parser.add_option("-t", "--to", dest="lang_to",
                      default="ja", metavar="LANG",
                      help=u"target language(msgstr)")
    parser.add_option("-p", "--pofile", dest="po_file",
                      default=None, metavar="POFILE",
                      help=u"target po file")
    parser.add_option("-s", "--sentence", dest="sentence",
                      default=None, metavar="SENTENCE",
                      help=u"target sentence")
    parser.add_option("-v", "--verbose", dest="verbose", 
                      action="store_true", default=False,
                      help=u"print debug messages to stdout")

    opts, args = parser.parse_args()
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
