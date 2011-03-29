#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys

from izuchi.translator import TRANSLATE_API
from locale import _
from utils import *

__version__ = "0.3.0"

def get_args():
    _ver = "%(prog)s {0}".format(__version__)
    parser = argparse.ArgumentParser(version=_ver)
    parser.set_defaults(api="google", detect=False,
                        lang_from="en", lang_to=get_lang(),
                        po_file=None, sentence=None, encoding=None,
                        quiet=False, verbose=False)
    parser.add_argument("-a", "--api", dest="api", metavar="API",
                        help=u"APIs are {0}, 'all' cannot use with "
                              "'-p po_file' option".format(
                              TRANSLATE_API.keys()))
    parser.add_argument("-d", "--detect", dest="detect", action="store_true",
                        help=u"detect language for target sentence")
    parser.add_argument("-f", "--from", dest="lang_from", metavar="LANG",
                        help=u"original language")
    parser.add_argument("-t", "--to", dest="lang_to", metavar="LANG",
                        help=u"target language to translate")
    parser.add_argument("-p", "--pofile", dest="po_file",
                        metavar="POFILE", help=u"target po file")
    parser.add_argument("-s", "--sentence", dest="sentence",
                        metavar="SENTENCE", help=u"target sentence")
    parser.add_argument("-e", "--encoding", dest="encoding",
                        action=EncodingAction, metavar="ENCODING",
                        help=u"input/output encoding")
    parser.add_argument("-q", "--quiet", dest="quiet", action="store_true",
                        help=u"not to show original sentence to stdout")

    opts = parser.parse_args()
    if not opts.lang_to:
        opts.lang_to = raw_input(u"Type language code: ")

    err_msg = None
    if opts.api not in TRANSLATE_API.keys():
        err_msg = _(u"Unsupported API: {0}").format(opts.api)
    elif opts.api == "all" and opts.po_file:
        err_msg = _(u"Unsupport to translate po file with all translators")
    elif opts.po_file and not os.access(opts.po_file, os.R_OK):
        err_msg = _(u"Cannot access po file: {0}").format(opts.po_file)
    elif not (opts.po_file or opts.sentence):
        err_msg = _(u"Set argument either '-p po_file' or '-s sentence'")
    elif opts.encoding:
        err_encoding = check_encoding(opts.encoding)
        if err_encoding:
            err_msg = _(u"unknown encodings: {0}").format(err_encoding)

    if err_msg:
        parser.print_help()
        print err_msg
        sys.exit(0)

    if not opts.encoding:
        set_default_encoding(opts)
    convrt_str_to_unicode(opts)
    return opts

def main():
    opts = get_args()
    handler = get_handler(opts)
    t = TRANSLATE_API[opts.api](opts.lang_from, opts.lang_to, handler)
    t.call_method_with_handler()

if __name__ == "__main__":
    check_python_version()
    main()
