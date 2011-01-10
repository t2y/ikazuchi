# -*- coding: utf-8 -*-

import sys

from izuchi.handler import *


def dispatch_handler(opts):
    if opts.po_file:
        h = InteractiveHandler(opts.po_file)
    elif opts.sentence:
        h = SingleSentenceHandler(opts.sentence)
    return h


def check_python_version():
    ver = sys.version_info
    if ver[0] == 2 and ver[1] < 6:
        print "unsuporrted Python version, use 2.6 above"
        sys.exit(0)
