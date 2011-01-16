# -*- coding: utf-8 -*-

try:
    import vim
except ImportError:
    print "call ':pyfile raimei' from vim"
    sys.exit(0)

import sys
from ikazuchi import izuchi
from locale import getdefaultlocale

TRANSLATE_API = {
    "google": izuchi.TranslatingGoogle,
    "microsoft": izuchi.TranslatingMicrosoft,
    "yahoo": izuchi.TranslatingYahoo,
}

def eval_or_default(param, default):
    try:
        ret = vim.eval(param)
    except:
        # FIXME: cannot catch vim.error
        ret = default
    return ret

def get_vim_variables():
    # settings from VimScript(.vimrc)
    _envvar = getdefaultlocale()
    api_name = eval_or_default("raimei_api", "google")
    lang_from = eval_or_default("raimei_from", "en")
    lang_to = eval_or_default("raimei_to", _envvar[0].split("_")[0])
    encoding = eval_or_default("&enc", _envvar[1])
    comp = eval_or_default("raimei_comp", None)
    return api_name, lang_from, lang_to, encoding, comp

def translate_with_range(translator, encoding):
    apis = []
    vim.current.range.append("")
    for line in vim.current.range:
        for info in translator.translate(line):
            apis.append(info[0])
            vim.current.range.append(info[1].encode(encoding))
    print "Translated by {0}".format(apis[::-1])

def translate(api_name, lang_from, lang_to, encoding, comp):
    if comp:
        t = izuchi.TranslatingComparison
    else:
        t = TRANSLATE_API[api_name]
    translator = t(lang_from, lang_to, None)
    return translate_with_range(translator, encoding)

def main():
    vim_vars = get_vim_variables()
    translate(*vim_vars)

if __name__ == "__main__":
    main()
