# -*- coding: utf-8 -*-

try:
    import vim
except ImportError:
    print "call ':pyfile raimei' from vim"

import re
import sys
import izuchi


def get_vim_variables():
    # settings from VimScript(.vimrc)
    api_name = vim.eval("raimei_api")
    lang_from = vim.eval("raimei_from")
    lang_to = vim.eval("raimei_to")
    enc = vim.eval("&enc")
    return api_name, lang_from, lang_to, enc

def get_lines_with_sentence(start, end):
    previous = start - 2
    subsequent = end + 2
    text = " ".join(vim.current.buffer[previous:subsequent])
    text += " "  # FIXME: pattern matching for end with "."

    # get lines each single sentence
    lines = []
    flags = re.MULTILINE
    base_ptrn = r"[\.|:][ |$]+"
    sentence_num = len(re.findall(base_ptrn, text, flags))
    if sentence_num > 0:
        ptrn = ""
        for i in range(sentence_num):
            ptrn += r"(.*{0})".format(base_ptrn)
        match = re.findall(ptrn, text, flags)
        # format lines
        if match:
            if isinstance(match[0], tuple):
                lines = [line.strip().rstrip() for line in match[0]]
            else:
                lines = [match[0].strip().rstrip()]
    return lines

def get_target_lines():
    match = re.search(r"\((.*)\)", str(vim.current.range))
    start, end = map(int, match.groups()[0].split(":"))
    lines = get_lines_with_sentence(start, end)
    if not lines:
        # with lines "as is"
        lines = vim.current.buffer[start - 1:end]
    return lines

def translate_with_range(translator, enc):
    apis, translated = set(), []
    vim.current.range.append("")
    target_lines = get_target_lines()
    for line in target_lines:
        for info in translator.translate(unicode(line, enc)):
            apis.add(info[0])
            translated.append(info[1].encode(enc))
    # append translated text into vim in reverse
    for text in reversed(translated):
        vim.current.range.append(text)
    vim.command("let raimei_target_lines={0}".format(target_lines))
    print "Translated by {0}".format(list(apis))

def translate(api_name, lang_from, lang_to, enc):
    t = izuchi.translator.TRANSLATE_API[api_name](lang_from, lang_to, None)
    return translate_with_range(t, enc)

def main():
    try:
        vim_vars = get_vim_variables()
    except NameError:
        return
    except vim.error:
        print "Set enc, raimei_api, raimei_from, raimei_to variables!"
        return
    translate(*vim_vars)

if __name__ == "__main__":
    main()
