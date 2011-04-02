# -*- coding: utf-8 -*-

try:
    import vim
except ImportError:
    print "call ':pyfile raimei' from vim"

import re
import sys
import izuchi


_SENTENCE_PATTERN = {
    "en": r"[\.|:][ |$]+",
    "ja": r"[。|．]",
}

def get_vim_variables():
    # settings from VimScript(.vimrc)
    try:
        api_name = vim.eval("raimei_api")
        lang_from = vim.eval("raimei_from")
        lang_to = vim.eval("raimei_to")
        enc = vim.eval("&enc")
    except vim.error:
        #  vim.error is String Exception
        print "Set enc, raimei_api, raimei_from, raimei_to variables!"
        raise
    return api_name, lang_from, lang_to, enc

def remove_imcomplete_line(lines, start):
    prev = vim.current.buffer[start - 1:start]
    if prev and prev[0]:
        if not re.search(r"[\.|:|。|．]$", prev[0].rstrip()):
            # remove first line if previous line is not end of a sentence
            lines = lines[1:]
    return lines

def get_lines_with_sentence(start, end):
    text = " ".join(t.strip() for t in vim.current.buffer[start:end])
    text += " "  # FIXME: pattern matching for end with "."

    # get lines for each single sentence
    lines = []
    flags = re.MULTILINE
    base_ptrn = _SENTENCE_PATTERN.get(vim.eval("raimei_from")) or \
                _SENTENCE_PATTERN["en"]
    sentence_num = len(re.findall(base_ptrn, text, flags))
    if sentence_num > 0:
        ptrn = r"(.*{0})".format(base_ptrn) * sentence_num
        match = re.findall(ptrn, text, flags)
        # format lines
        if match:
            if isinstance(match[0], tuple):
                lines = remove_imcomplete_line(match[0], start)
                lines = [line.strip().rstrip() for line in lines]
            else:
                lines = [match[0].strip().rstrip()]
    return lines

def get_target_lines(start, end):
    lines = get_lines_with_sentence(start, end)
    if not lines:
        # with lines "as is"
        lines = vim.current.buffer[start:end]
    return lines

def get_index_of_range():
    # FIXME: how to get indexes(start, end) of the range
    range_text = str(vim.current.range)
    match = re.search(r"\((.*)\)", range_text)
    if match:
        start, end = map(int, match.groups()[0].split(":"))
        start -= 1  # because range returns line number(start from 1)
    else:
        raise ValueError("Cannot get index of the range: {0}".format(
                         range_text))
    return start, end

def translate_with_range(translator, enc):
    api, translated = "", ["", ]
    start, end = get_index_of_range()
    target_lines = get_target_lines(start, end)
    # call translate API
    for line in target_lines:
        #info = translator.translate(unicode(line, enc))
        api, _translated = translator.translate(unicode(line, enc))
        translated.append(_translated.encode(enc))
    # add translated text into vim
    translated.append("")  # just for look and feel
    vim.current.buffer.append(translated, end)
    vim.command("let raimei_target_lines={0}".format(target_lines))
    print "Translated by {0}".format(api)

def translate(api_name, lang_from, lang_to, enc):
    t = izuchi.translator.TRANSLATE_API[api_name](lang_from, lang_to, None)
    return translate_with_range(t, enc)

def main():
    try:
        vim_vars = get_vim_variables()
        translate(*vim_vars)
    except Exception as err:
        print err.message
        return

if __name__ == "__main__":
    main()
